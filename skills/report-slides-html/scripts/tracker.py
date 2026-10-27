#!/usr/bin/env python3
"""Đọc BẢNG THEO DÕI TIẾN ĐỘ (Google Sheets/Excel xuất PDF, .xlsx, .csv) và tính sẵn các con số tổng hợp.

  python3 tracker.py <file> <WORK> [--date DD/MM/YYYY]
Ghi WORK/tracker.json (các dòng) và WORK/facts.md (sự thật đã tính, kèm công thức để chép vào meta.computed).

Nguyên tắc: MỌI phép cộng/chia/đếm do script làm. Model chỉ chọn và chép.
"""
import argparse, datetime as dt, html, json, os, re, subprocess, sys, csv, zipfile
from collections import defaultdict

HEAD = {"stt": r"^(STT|TT|Số TT|No\.?|#)$",
        "task": r"^(Công|Công việc|Nhiệm vụ|Hạng mục|Nội dung|Đầu việc|Công tác|Task|Item|Activity|Work)",
        "unit": r"^(Đơn|Đơn vị|Phụ trách|Bộ phận|Chủ trì|Owner|PIC|Team|Unit|Department)",
        "owner": r"^(Người|Đầu mối|Cán bộ|Assignee|Person|Contact)",
        "req": r"^(Yêu$|Yêu cầu|Sản phẩm|Deliverable|Output)",
        "deadline": r"^(Thời$|Thời hạn|Hạn|Mốc|Ngày hoàn thành|Deadline|Due|Target)",
        "status": r"^(Tình$|Tình trạng|Trạng thái|Status|State)",
        "result": r"^(Kết$|Kết quả|Ghi chú|Cập nhật|Mô tả kết quả|Result|Notes?|Comment|Update|Progress note)"}

def vn(x, d=1):
    """Số kiểu Việt Nam: 1.468 ; 83,4"""
    if abs(x - round(x)) < 1e-9: return f"{int(round(x)):,}".replace(",", ".")
    return f"{x:.{d}f}".replace(".", ",")

def num(s):
    return float(s.replace(".", "").replace(",", "."))

# ------------------------------------------------------------ đọc PDF theo toạ độ chữ
def row_rules(path, page_no, page_w):
    """Toạ độ y ranh giới hàng: gom mọi đoạn ngang (nét có/không phép biến đổi, hình chữ nhật mảnh, mép ô tô nền);
    giữ các y mà tổng chiều dài đoạn phủ >= 50% bề rộng bảng. [] nếu không có."""
    import tempfile
    from collections import defaultdict
    f = os.path.join(tempfile.mkdtemp(), "p.svg")
    subprocess.run(["pdftocairo", "-svg", "-f", str(page_no), "-l", str(page_no), path, f], capture_output=True)
    if not os.path.exists(f): return []
    body = open(f, encoding="utf8").read().split("</defs>", 1)[-1]
    segs = []  # (y, x0, x1)
    for tag in re.findall(r"<path[^>]*>", body):
        d = re.search(r' d="([^"]+)"', tag)
        if not d: continue
        m = re.search(r'transform="matrix\(([^)]+)\)"', tag)
        A, B, C, D, E, Fm = (list(map(float, re.split(r"[ ,]+", m.group(1).strip()))) if m else [1, 0, 0, 1, 0, 0])
        T = lambda x, y: (A * x + C * y + E, B * x + D * y + Fm)
        if "stroke=" in tag:
            for x1, y1, x2, y2 in re.findall(r"M ([\d.-]+) ([\d.-]+) L ([\d.-]+) ([\d.-]+)", d.group(1)):
                p1, p2 = T(float(x1), float(y1)), T(float(x2), float(y2))
                if abs(p1[1] - p2[1]) < 0.5 and abs(p2[0] - p1[0]) > 3: segs.append((p1[1], min(p1[0], p2[0]), max(p1[0], p2[0])))
        elif "fill=" in tag:
            for sub in re.findall(r"M ([^MZ]+)Z", d.group(1)):
                pts = [T(*map(float, xy)) for xy in re.findall(r"([\d.-]+) ([\d.-]+)", sub)]
                if len(pts) < 3 or any(c in sub for c in "CQ"): continue
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                if w < 3 or w > page_w * 1.05: continue
                if h < 1.5: segs.append(((min(ys) + max(ys)) / 2, min(xs), max(xs)))
                elif h < 400: segs += [(min(ys), min(xs), max(xs)), (max(ys), min(xs), max(xs))]
    if not segs: return []
    left, right = min(s[1] for s in segs), max(s[2] for s in segs); width = right - left
    cover = defaultdict(float)
    for y, x0, x1 in segs: cover[round(y)] += x1 - x0
    ys = sorted(y for y, c in cover.items() if c >= 0.5 * width)
    out = []
    for y in ys:
        if not out or y - out[-1] > 2: out.append(y)
    return out

def pdf_rows(path):
    x = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True).stdout
    pages = re.findall(r"<page[^>]*>(.*?)</page>", x, re.S)
    page_w = [float(w) for w in re.findall(r'<page width="([\d.]+)"', x)]
    W = []
    for pi, pg in enumerate(pages):
        for m in re.finditer(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pg):
            W.append(dict(p=pi, x0=float(m.group(1)), y0=float(m.group(2)), x1=float(m.group(3)), y1=float(m.group(4)), t=html.unescape(m.group(5))))
    # tiêu đề cột: trang đầu, các chữ khớp HEAD nằm cùng dải trên cùng
    stt_w = next((w for w in W if w["p"] == 0 and re.fullmatch(r"STT", w["t"])), None)
    if not stt_w: return None, None
    top = stt_w["y1"] + 8
    # 1) mép trái các cột lấy TỪ DỮ LIỆU: vị trí chữ đầu dòng của ô (Sheets căn trái ô dữ liệu, căn giữa tiêu đề)
    data = [w for w in W if w["p"] > 0 or w["y0"] > top]
    starts = []
    for w in data:
        left = [v for v in data if v["p"] == w["p"] and abs(v["y0"] - w["y0"]) < 2 and 0 < w["x0"] - v["x1"] < 7]
        if not left: starts.append(w["x0"])
    starts.sort(); clusters = []
    for x in starts:
        if clusters and x - clusters[-1][-1] < 5: clusters[-1].append(x)
        else: clusters.append([x])
    big = [c for c in clusters if len(c) >= max(4, 0.02 * len(starts))]
    edges = sorted(min(c) for c in big)
    # 2) gán tên cột theo TÂM của tiêu đề
    band = [w for w in W if w["p"] == 0 and stt_w["y0"] - 26 < w["y0"] < top]
    named = {}
    for k, pat in HEAD.items():
        c = [w for w in band if re.match(pat, w["t"])]
        if not c: continue
        h = min(c, key=lambda w: w["x0"]); cx = (h["x0"] + h["x1"]) / 2 if k != "stt" else h["x0"] + 1
        i = max([j for j, e in enumerate(edges) if e - 4 <= cx] or [0])
        named.setdefault(i, k)
    bounds = []
    for j, e in enumerate(edges):
        k = named.get(j, f"col{j}")
        bounds.append((k, (e - 3) if j else 0, (edges[j + 1] - 3) if j + 1 < len(edges) else 1e9))
    # cột không tên (chữ tràn/thụt lề) gộp vào cột có tên đứng trước nó
    merged = []
    for k, a0, b0 in bounds:
        if k.startswith("col") and merged: merged[-1] = (merged[-1][0], merged[-1][1], b0)
        else: merged.append((k, a0, b0))
    bounds = merged
    def col_of(w):
        cx = w["x0"] + 1
        return next(k for k, a, b in bounds if a <= cx < b)
    # STT: chữ trong cột stt có dạng 1 / 1.a / 6.1
    rows = []
    for pi in range(len(pages)):
        ws = [w for w in W if w["p"] == pi and (pi > 0 or w["y0"] > top)]
        stts = sorted([w for w in ws if col_of(w) == "stt" and re.fullmatch(r"\d+(\.[a-z0-9])?", w["t"])], key=lambda w: w["y0"])
        if not stts: continue
        centers = [(s["y0"] + s["y1"]) / 2 for s in stts]
        cells = defaultdict(list)
        rules = row_rules(path, pi + 1, page_w[pi] if pi < len(page_w) else 800)
        spans = []
        for c in centers:
            above = [y for y in rules if y <= c]; below = [y for y in rules if y > c]
            spans.append((above[-1] if above else -1, below[0] if below else 1e9))
        if rules and all(a >= 0 and b < 1e9 for a, b in spans):
            for k, _, _ in bounds:
                if k == "stt": continue
                for ri, (a0, b0) in enumerate(spans):
                    ws_ = sorted([w for w in ws if col_of(w) == k and a0 <= (w["y0"] + w["y1"]) / 2 < b0], key=lambda w: (round(w["y0"]), w["x0"]))
                    if ws_: cells[(ri, k)].append(" ".join(w["t"] for w in ws_))
            for i, s_ in enumerate(stts):
                r = {"stt": s_["t"], "page": pi + 1, "_rule": True}
                for k, _, _ in bounds:
                    if k != "stt": r[k] = " ".join(cells.get((i, k), [])).strip()
                rows.append(r)
            continue
        for k, _, _ in bounds:
            if k == "stt": continue
            cw = sorted([w for w in ws if col_of(w) == k], key=lambda w: (round(w["y0"], 0), w["x0"]))
            # gom thành dòng
            lines = []
            for w in cw:
                if lines and abs(lines[-1]["y0"] - w["y0"]) < 2.5: lines[-1]["ws"].append(w); lines[-1]["y1"] = max(lines[-1]["y1"], w["y1"])
                else: lines.append(dict(y0=w["y0"], y1=w["y1"], ws=[w]))
            # gom dòng thành khối (ô): khoảng trống lớn -> ô mới
            blocks = []
            for ln in lines:
                if blocks and ln["y0"] - blocks[-1]["y1"] < 3.2: blocks[-1]["lines"].append(ln); blocks[-1]["y1"] = ln["y1"]
                else: blocks.append(dict(y0=ln["y0"], y1=ln["y1"], lines=[ln]))
            for b_ in blocks:
                c = (b_["y0"] + b_["y1"]) / 2
                ri = min(range(len(centers)), key=lambda i: abs(centers[i] - c))
                cells[(ri, k)].append(" ".join(" ".join(w["t"] for w in sorted(l["ws"], key=lambda w: w["x0"])) for l in b_["lines"]))
        for i, s in enumerate(stts):
            r = {"stt": s["t"], "page": pi + 1}
            for k, _, _ in bounds:
                if k != "stt": r[k] = " ".join(cells.get((i, k), [])).strip()
            rows.append(r)
    head_txt = " ".join(w["t"] for w in W if w["p"] == 0 and w["y1"] < stt_w["y0"] - 8)
    return rows, head_txt

def table_rows(rows2d):
    """Bảng 2 chiều (xlsx/csv) -> các dòng theo tên cột."""
    hdr_i = next((i for i, r in enumerate(rows2d) if any(re.match(HEAD["stt"], str(c).strip(), re.I) for c in r)), None)
    if hdr_i is None: return None, ""
    hdr = [str(c).strip() for c in rows2d[hdr_i]]
    keymap = {}
    for j, h in enumerate(hdr):
        for k, pat in HEAD.items():
            if h and re.match(pat, h, re.I) and k not in keymap.values(): keymap[j] = k; break
    out = []
    for r in rows2d[hdr_i + 1:]:
        d = {keymap[j]: str(c).strip() for j, c in enumerate(r) if j in keymap}
        if re.fullmatch(r"\d+(\.[a-z0-9]{1,2})*\.?", d.get("stt", "")): d["stt"] = d["stt"].rstrip("."); out.append(d)
    return out, " ".join(str(c) for r in rows2d[:hdr_i] for c in r)

def xlsx_rows(path):
    """Duyệt mọi sheet, lấy sheet đầu tiên có hàng tiêu đề chứa cột STT."""
    z = zipfile.ZipFile(path)
    ss = [html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))) for si in re.findall(r"<si>.*?</si>", z.read("xl/sharedStrings.xml").decode(), re.S)] if "xl/sharedStrings.xml" in z.namelist() else []
    sheets = sorted([n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[-1]))
    for sn in sheets:
        sh = z.read(sn).decode()
        grid = []
        for row in re.findall(r"<row[^>]*>(.*?)</row>", sh, re.S):
            r = {}
            for ref, typ, inner in re.findall(r'<c r="([A-Z]+)\d+"((?:[^>]*?t="\w+")?)[^>]*?(?:/>|>(.*?)</c>)', row, re.S):
                ci = 0
                for ch in ref: ci = ci * 26 + ord(ch) - 64
                v = re.search(r"<v>(.*?)</v>", inner or ""); isv = re.search(r"<is>.*?<t[^>]*>(.*?)</t>", inner or "", re.S)
                if 't="s"' in typ and v: r[ci - 1] = ss[int(v.group(1))]
                elif isv: r[ci - 1] = html.unescape(isv.group(1))
                elif v: r[ci - 1] = v.group(1)
            grid.append([r.get(i, "") for i in range(max(r) + 1)] if r else [])
        rows, head = table_rows(grid)
        if rows:
            for d in rows:  # ngày dạng số serial của Excel trong cột thời hạn
                if re.fullmatch(r"\d{5}(\.0+)?", d.get("deadline", "")):
                    dd = dt.date(1899, 12, 30) + dt.timedelta(days=int(float(d["deadline"])))
                    d["deadline"] = dd.strftime("%d/%m/%Y")
            return rows, head
    return None, ""

def docx_rows(path):
    """Bảng trong Word: lấy bảng đầu tiên có cột STT."""
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf8", "replace")
    for tbl in re.findall(r"<w:tbl>.*?</w:tbl>", x, re.S):
        grid = []
        for tr in re.findall(r"<w:tr\b.*?</w:tr>", tbl, re.S):
            grid.append([" ".join(html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))) for p in re.findall(r"<w:p\b.*?</w:p>", tc, re.S)).strip()
                         for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, re.S)])
        rows, head = table_rows(grid)
        if rows:
            before = x[:x.index(tbl)]
            head = " ".join(html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p))) for p in re.findall(r"<w:p\b.*?</w:p>", before, re.S)[-8:])
            return rows, head
    return None, ""

# ------------------------------------------------------------ chuẩn hoá & tính
def status_of(s):
    s = (s or "").lower()
    if re.search(r"trễ|chậm|quá hạn|delay|overdue|late|blocked|vướng", s): return "tre"
    if re.search(r"chưa hoàn thành|not complete|incomplete", s): return "dang"
    if re.search(r"hoàn thành|đã xong|\bxong\b|\bdone\b|complete|closed|finished", s): return "xong"
    if re.search(r"chưa bắt đầu|chưa thực hiện|chưa triển khai|chưa làm|not started|to ?do|pending|open", s): return "chua"
    if re.search(r"đang|triển khai|in progress|ongoing|doing|wip", s): return "dang"
    return ""

def parse_date(s, year):
    s = s or ""
    m = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](20\d\d)", s)
    if m: return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(20\d\d)-(\d{1,2})-(\d{1,2})", s)
    if m: return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])", s)
    if m:
        try: return dt.date(year, int(m.group(2)), int(m.group(1)))
        except ValueError: return None
    return None

DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(20\d\d)")
FRAC = re.compile(r"(?<![\d/])(\d{1,3}(?:\.\d{3})+|\d+)\s*/\s*(\d{1,3}(?:\.\d{3})+|\d+)(?![\d/])\s*([A-Za-zÀ-ỹđĐ]+(?:\s+[A-Za-zÀ-ỹđĐ]+)?)?")
TB = re.compile(r"(\d+(?:[.,]\d+)?)\s*(TB|GB|PB|tỷ đồng|triệu đồng|tỷ|triệu)(?![\wÀ-ỹ])", re.I)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("work"); ap.add_argument("--date")
    a = ap.parse_args(); os.makedirs(a.work, exist_ok=True)
    ext = a.src.lower().rsplit(".", 1)[-1]
    if ext == "pdf": rows, head = pdf_rows(a.src)
    elif ext == "xlsx": rows, head = xlsx_rows(a.src)
    elif ext == "csv": rows, head = table_rows(list(csv.reader(open(a.src, encoding="utf-8-sig"))))
    elif ext == "docx": rows, head = docx_rows(a.src)
    else: sys.exit("KHÔNG PHẢI BẢNG THEO DÕI (tracker.py đọc .pdf, .xlsx, .csv, .docx có bảng). Bỏ qua bước này, làm theo quy trình thường.")
    if not rows: sys.exit("KHÔNG PHẢI BẢNG THEO DÕI (không thấy cột STT). Bỏ qua bước này, làm theo quy trình thường.")
    m = DATE.search(head or ""); rep_date = a.date or (m.group(0) if m else dt.date.today().strftime("%d/%m/%Y"))
    if not re.fullmatch(r"\d{1,2}/\d{1,2}/20\d\d", rep_date):
        sys.exit("LỖI: ngày báo cáo phải dạng DD/MM/YYYY (--date)")
    d, mo, y = map(int, rep_date.split("/")); today = dt.date(y, mo, d)
    for r in rows:
        if not r.get("unit") and re.fullmatch(r"(VNPT\s+\w+|[A-ZĐ][\w&-]+)", (r.get("task") or "").strip()):
            r["unit"] = r["task"].strip()   # dòng con: tên đơn vị nằm ở cột Công việc
        r["st"] = status_of(r.get("status"))
        dd_ = parse_date(r.get("deadline", ""), today.year)
        r["due"] = dd_.strftime("%d/%m/%Y") if dd_ else ""
    json.dump(dict(date=rep_date, header=head, rows=rows), open(os.path.join(a.work, "tracker.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)

    F = []; add = lambda kind, text, value="", formula="": F.append(dict(kind=kind, text=text, value=value, formula=formula))
    items = defaultdict(list)
    for r in rows: items[r["stt"].split(".")[0]].append(r)
    _tot = re.compile(r"^\s*(tổng\s*(cộng|số|chung|toàn)|tong\s*cong|grand\s*total|sub\s*total|total\b)", re.I)
    total_rows = [r for r in rows if any(_tot.match(str(r.get(k) or "")) for k in ("stt", "task", "unit"))]
    parent_rows = [r for r in rows if r not in total_rows and any(x['stt'].startswith(r['stt']+'.') for x in rows)]
    work = [r for r in rows if r not in total_rows and r not in parent_rows and r['st']]
    duplicate_groups = defaultdict(list)
    for r in work:
        sig = (r['stt'].split('.')[0], str(r.get('unit') or '').lower(), r.get('result',''), r.get('due',''), r.get('st',''))
        if r.get('unit'): duplicate_groups[sig].append(r['stt'])
    duplicate_groups = [ids for ids in duplicate_groups.values() if len(ids)>1]
    duplicate_items = {ids[0].split('.')[0] for ids in duplicate_groups}
    active_items = {it: [r for r in work if r['stt'].split('.')[0]==it] for it in items}
    active_items = {it: rs for it,rs in active_items.items() if rs}
    nd = sum(r['st']=='xong' for r in work)
    raw_status = sum(bool(r['st']) for r in rows)
    add('chung', f'Ngày báo cáo: {rep_date}. {len(rows)} dòng dữ liệu; {raw_status} dòng có trạng thái; {len(work)} dòng chi tiết có trạng thái thuộc {len(active_items)} nhóm công việc (không tính dòng tổng/cha). Hoàn thành {nd}/{len(work)} dòng chi tiết theo nguyên bản, chưa khử dòng nghi trùng. Không gọi mẫu số này là số đầu việc duy nhất.',
        value=f'{nd}/{len(work)}', formula=f'đếm nguyên bản {len(work)} dòng chi tiết có trạng thái, không tính tổng/cha; hoàn thành {nd}; chưa khử dòng nghi trùng')
    for ids in duplicate_groups:
        add('nghi-trung', 'Các dòng '+', '.join(ids)+' trùng đơn vị, kết quả, hạn và trạng thái. Chưa xác nhận là bản ghi thừa; phải nêu bất thường, không khử âm thầm để đếm đầu việc duy nhất hoặc cộng tổng.')
    for it, sub in active_items.items():
        done=sum(r['st']=='xong' for r in sub)
        title=next((r.get('task') for r in items[it] if r.get('task')), '')[:90]
        dues=sorted({r['due'] for r in sub if r['due']},key=lambda d:tuple(map(int,d.split('/')[::-1])))
        add('muc', f'Mục {it} «{title}»: {done}/{len(sub)} dòng chi tiết hoàn thành theo nguyên bản'+(' (có dòng nghi trùng)' if it in duplicate_items else '')+(f'; hạn {dues[0]}–{dues[-1]}' if len(dues)>1 else f'; hạn {dues[0]}' if dues else ''),value=f'{done}/{len(sub)}',formula=f'đếm {done} dòng hoàn thành / {len(sub)} dòng chi tiết nguyên bản của mục {it}, không tính cha/tổng')
    overdue=[r for r in work if r['due'] and dt.datetime.strptime(r['due'],'%d/%m/%Y').date()<today and r['st']!='xong']
    not_started=[r for r in work if r['st']=='chua']
    union={r['stt'] for r in overdue+not_started};intersection={r['stt'] for r in overdue}&{r['stt'] for r in not_started}
    add('tap-trang-thai',f'{len(overdue)} dòng quá hạn; {len(not_started)} dòng chưa bắt đầu; giao hai nhóm {len(intersection)} dòng ({", ".join(sorted(intersection)) or "không có"}); hợp hai nhóm {len(union)} dòng ({", ".join(sorted(union)) or "không có"}). Không gộp nhãn mà giữ số của một nhóm.')
    late_children=[]
    for total in total_rows:
        if not total['due']:continue
        late_children.extend(r for r in work if r['due'] and dt.datetime.strptime(r['due'],'%d/%m/%Y')>dt.datetime.strptime(total['due'],'%d/%m/%Y'))
    if late_children:
        add('moc-khac-nhau','Mốc dòng tổng '+', '.join(r['stt']+': '+r['due'] for r in total_rows if r['due'])+' sớm hơn các hạn thành phần: '+', '.join(r['stt']+' '+r['due'] for r in late_children)+'. Nêu khác biệt phạm vi, không tự kéo hạn các dòng về mốc tổng.')
    profile={'raw_rows':len(rows),'status_rows':raw_status,'detail_rows':len(work),'groups':len(active_items),'completed_detail_rows':nd,'duplicate_candidates':duplicate_groups,'overdue':[r['stt'] for r in overdue],'not_started':[r['stt'] for r in not_started],'union':sorted(union),'intersection':sorted(intersection),'later_than_total':[r['stt'] for r in late_children]}
    json.dump(profile,open(os.path.join(a.work,'source-checks.json'),'w',encoding='utf8'),ensure_ascii=False,indent=2)
    for key,value in [('dòng nguồn',len(rows)),('dòng có trạng thái',raw_status),('dòng chi tiết nguyên bản',len(work)),('nhóm công việc',len(active_items)),('dòng quá hạn',len(overdue)),('dòng chưa bắt đầu',len(not_started)),('dòng thuộc hợp hai nhóm',len(union))]:
        add('dem-nguon',f'{key}: {value}',value=str(value),formula=f'đếm {key} trong bảng nguồn = {value}')
    # quá hạn
    for r in rows:
        if r["due"] and r["st"] != "xong":
            d2 = dt.date(*map(int, r["due"].split("/")[::-1]))
            if d2 < today: add("qua-han", f"Dòng {r['stt']} ({r.get('unit','')}) hạn {r['due']} đã qua, trạng thái: {r.get('status') or 'trống'}.", value=r["due"])
    # chưa bắt đầu
    cb = [f"{r['stt']} {r.get('unit','')}".strip() for r in rows if r["st"] == "chua"]
    if cb: add("chua-bat-dau", "Dòng chưa bắt đầu/chưa thực hiện: " + "; ".join(cb))
    # phân số X/Y trong kết quả
    per_item_unit = defaultdict(list)
    # Chặn cộng sai phạm vi (v5): bỏ dòng TỔNG/CỘNG; bỏ dòng mục cha khi mục đã có dòng con mang phân số
    # (dòng cha thường đã là tổng của con); bỏ dòng trùng y hệt (cùng đơn vị, cùng tử/mẫu, cùng đơn vị đo) trong một mục.
    TOTAL = re.compile(r"^\s*(tổng\s*(cộng|số|chung|toàn)|tong\s*cong|cộng\s*(dồn|chung|toàn)?\s*[:\-]?\s*$|grand\s*total|sub\s*total|total\b)", re.I)
    has_child_frac = {r["stt"].split(".")[0] for r in rows if "." in r["stt"] and FRAC.search(r.get("result", ""))}
    seen_sig, skipped = set(), []
    def in_scope(r, x, yv, unit):
        if any(TOTAL.match(str(r.get(k) or "")) for k in ("stt", "task", "unit")):
            skipped.append(f"{r['stt']} (dòng tổng)"); return False
        if "." not in r["stt"] and r["stt"] in has_child_frac:
            skipped.append(f"{r['stt']} (dòng mục cha, đã có dòng con)"); return False
        sig = (r["stt"].split(".")[0], (r.get("unit") or "").lower(), x, yv, unit)
        if r.get("unit") and sig in seen_sig:
            skipped.append(f"{r['stt']} (nghi trùng; chỉ loại khỏi phép cộng tạm, chưa xác nhận bản ghi thừa)"); return False
        seen_sig.add(sig); return True
    for r in rows:
        txt = r.get("result", "")
        fr = []
        for m in FRAC.finditer(txt):
            x, yv = num(m.group(1)), num(m.group(2))
            if not yv or x > yv or re.fullmatch(r"(19|20)\d\d", m.group(2)): continue
            unit = (m.group(3) or "").lower().strip()
            fr.append((m.group(1), m.group(2), x, yv, unit))
            add("ti-le", f"Dòng {r['stt']} ({r.get('unit','')}): {m.group(1)}/{m.group(2)} {unit} = {vn(100 * x / yv)}%".strip(),
                value=f"{vn(100 * x / yv)}%", formula=f"{m.group(1)} / {m.group(2)} = {vn(100 * x / yv)}%")
            if in_scope(r, x, yv, unit):
                per_item_unit[(r["stt"].split(".")[0], unit)].append((r["stt"], r.get("unit", ""), x, yv, m.group(1), m.group(2)))
        # cộng các phân số CÙNG đơn vị đo trong một dòng (vd 2 site cùng 'host esxi')
        byu = defaultdict(list)
        for f in fr:
            if f[4]: byu[f[4]].append(f)
        for u, fs in byu.items():
            if len(fs) >= 2:
                sx, sy = sum(f[2] for f in fs), sum(f[3] for f in fs)
                add("tong-dong", f"Dòng {r['stt']}: cộng {len(fs)} phân số '{u}': {vn(sx)}/{vn(sy)}, tỷ lệ {vn(100*sx/sy)}% (= {vn(sx)} / {vn(sy)})",
                    value=f"{vn(sx)}/{vn(sy)}", formula=f"{' + '.join(f[0] for f in fs)} = {vn(sx)} (tử số); {' + '.join(f[1] for f in fs)} = {vn(sy)} (mẫu số)")
    # cộng theo mục: các dòng con cùng mục, mỗi dòng 1 phân số (vd tiến độ từng đơn vị)
    if skipped: add("chan-cong", "Không đưa vào phép cộng: " + "; ".join(sorted(set(skipped))))
    by_item = defaultdict(list)
    for (it, u), lst in per_item_unit.items():
        for e in lst: by_item[(it, u)].append(e)   # v5: không trộn đơn vị đo khác nhau trong một mục
    units_per_item = defaultdict(int)
    for (it, u) in by_item: units_per_item[it] += 1
    for (it, u), lst in by_item.items():
        if units_per_item[it] > 1 and not u: continue   # mục có nhiều đơn vị đo: bỏ nhóm không rõ đơn vị
        one_per_row = {}
        for e in lst: one_per_row.setdefault(e[0], e)
        es = list(one_per_row.values())
        if it not in duplicate_items and len(es) >= 3 and len({e[0] for e in es}) == len(es):
            sx, sy = sum(e[2] for e in es), sum(e[3] for e in es)
            add("tong-muc", f"Mục {it}: cộng tiến độ các dòng {', '.join(e[0] for e in es)}: {vn(sx)}/{vn(sy)} ({vn(100*sx/sy)}%)",
                value=f"{vn(sx)}/{vn(sy)}", formula=f"{' + '.join(e[4] for e in es)} = {vn(sx)} (tử số); {' + '.join(e[5] for e in es)} = {vn(sy)} (mẫu số)")
            add("tong-muc", f"Mục {it}: tổng số đã hoàn thành = {vn(sx)}", value=vn(sx), formula=f"{' + '.join(e[4] for e in es)} = {vn(sx)}")
            add("tong-muc", f"Mục {it}: còn lại = {vn(sy - sx)}", value=vn(sy - sx), formula=f"{vn(sy)} - {vn(sx)} = {vn(sy - sx)}")
    # Same measurement unit does not prove disjoint objects across tasks.
    if len({it for it, u in per_item_unit}) > 1:
        add("pham-vi", "Không tự cộng qua các mục: cùng đơn vị đo không chứng minh các đối tượng không trùng. Giữ riêng từng mục; tổng nguồn chỉ là số do nguồn công bố, cần nêu phạm vi.")
    # nguồn lực: cộng theo từng đơn vị đo (TB, GB, tỷ đồng, triệu đồng…)
    from collections import defaultdict as _dd
    byunit = _dd(list)
    for r in rows:
        for m in TB.finditer(r.get("result", "")):
            u = m.group(2).lower(); u = {"tỷ": "tỷ đồng", "triệu": "triệu đồng"}.get(u, u).replace("tb", "TB").replace("gb", "GB").replace("pb", "PB")
            byunit[u].append((r["stt"], r.get("unit", ""), num(m.group(1)), m.group(1)))
    for u, ts in byunit.items():
        if len(ts) >= 2:
            s_ = sum(t[2] for t in ts)
            add("nguon-luc", f"Các giá trị {u} nêu trong bảng: " + "; ".join(f"{t[0]} {t[1]}: {t[3]} {u}" for t in ts) + f". Tổng = {vn(s_)} {u}",
                value=f"{vn(s_)} {u}", formula=f"{' + '.join(t[3] for t in ts)} = {vn(s_)}")
    for i, f in enumerate(F, 1): f["id"] = f"F{i}"
    json.dump(F, open(os.path.join(a.work, "facts.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
    out = [f"# Sự thật tính từ bảng theo dõi (ngày báo cáo {rep_date}) – do script tính, CHÉP NGUYÊN, không tự tính lại", ""]
    for f in F: out.append(f"- {f['id']} [{f['kind']}] {f['text']}" + (f"  → computed: {{\"value\": \"{f['value']}\", \"formula\": \"{f['formula']}\"}}" if f["formula"] else ""))
    out += ["", "## Bảng đã đọc (STT | đơn vị | hạn | tình trạng | kết quả rút gọn)"]
    for r in rows: out.append(f"- {r['stt']} | {r.get('unit','')} | {r.get('deadline','')} | {r.get('status','')} | {r.get('result','')[:160]}")
    open(os.path.join(a.work, "facts.md"), "w", encoding="utf8").write("\n".join(out) + "\n")
    print(f"OK: {len(rows)} dòng, {len(F)} sự thật. Xem {os.path.join(a.work, 'facts.md')}")

if __name__ == "__main__":
    main()
