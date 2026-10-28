#!/usr/bin/env python3
"""report-slides-html: tài liệu gốc -> báo cáo dạng slide HTML 16:9 -> PDF (+ Word đơn giản).

Các lệnh (WORK = thư mục làm việc của một báo cáo):
  report.py env                                  kiểm tra môi trường, in lệnh cài thứ còn thiếu
  report.py extract <file> [<file> ...] --work WORK   trích chữ + ảnh trang mọi file nguồn -> WORK/content.md
  report.py find WORK "<từ khóa>"                tìm trong nguồn (không phân biệt hoa thường, dấu)
  report.py new WORK                             tạo WORK/report.json từ khung mẫu
  report.py build WORK [--no-pdf]                kiểm tra + dựng HTML + xuất PDF + ảnh xem trước
  report.py docx WORK                            xuất Word đơn giản từ report.json

Mọi lệnh in dòng NEXT: chỉ việc cần làm tiếp.
"""
import argparse, subprocess
import importlib
import importlib.util
import json
import platform
import re
import shutil
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

MAX_ATTEMPTS = 3  # số lần build lỗi số liệu trước khi chuyển thành cảnh báo


def write_status(work, done, result, nxt):
    """WORK/STATUS.md: đường dẫn tuyệt đối + bước vừa xong + việc tiếp theo (đọc lại khi mất ngữ cảnh)."""
    from datetime import datetime
    r = f"{sys.executable} {HERE / 'report.py'}"
    files = ", ".join(p.name for p in sorted(Path(work).glob("*")) if p.suffix in (".md", ".json", ".html", ".pdf", ".docx"))
    Path(work, "STATUS.md").write_text(
        f"# Trạng thái báo cáo – cập nhật {datetime.now():%d/%m/%Y %H:%M}\n\n"
        f"Đọc file này trước tiên nếu vừa bị ngắt hoặc mất ngữ cảnh.\n\n"
        f"- SKILL_DIR: `{SKILL}`\n- Lệnh R: `{r}`\n- WORK: `{work}`\n"
        f"- Hướng dẫn: `{SKILL / 'SKILL.md'}` · `{SKILL / 'references' / 'huong-dan-k7.md'}`\n"
        f"- File trong WORK: {files}\n\n## Bước vừa xong\n{done}\n\n## Kết quả\n{result}\n\n"
        f"## Việc tiếp theo\n{nxt}\n", encoding="utf-8")


def out(msg=""):
    print(msg, flush=True)


# ---------------------------------------------------------------- env

def cmd_env(_):
    out(f"Python {sys.version.split()[0]} trên {platform.system()}")
    libs = [("docx", "python-docx", True, "xuất Word, đọc .docx"),
            ("pptx", "python-pptx", True, "đọc .pptx"),
            ("PIL", "Pillow", True, "ghép ảnh xem trước"),
            ("fitz", "PyMuPDF", False, "đọc/render PDF (thay được bằng poppler)"),
            ("openpyxl", "openpyxl", False, "đọc .xlsx")]
    missing = []
    for mod, pip, req, why in libs:
        try:
            importlib.import_module(mod)
            out(f"  [OK]       {pip:<12} {why}")
        except Exception:
            out(f"  [{'THIẾU' if req else 'tùy chọn'}] {pip:<12} {why}")
            if req:
                missing.append(pip)
    poppler = bool(shutil.which("pdftotext") and shutil.which("pdftoppm"))
    fitz_ok = importlib.util.find_spec("fitz") is not None
    out(f"  [{'OK' if poppler else 'không có'}] poppler      pdftotext/pdftoppm")
    if not (poppler or fitz_ok):
        missing.append("PyMuPDF")
    from export_pdf import find_browser
    b = find_browser()
    out(f"  [{'OK' if b else 'THIẾU'}] trình duyệt  {b or 'cần Chrome/Edge/Chromium để xuất PDF'}")
    from extract import find_soffice
    out(f"  [{'OK' if find_soffice() else 'không có'}] LibreOffice  (tùy chọn: ảnh trang cho pptx/docx không kèm PDF)")
    out()
    if missing:
        out(f"NEXT: chạy `{sys.executable} -m pip install {' '.join(missing)}` rồi chạy lại `report.py env`.")
    elif not b:
        out("NEXT: cài Google Chrome (hoặc Edge), hoặc đặt biến môi trường REPORT_BROWSER=<đường dẫn trình duyệt>. "
            "Tạm thời vẫn dựng được HTML bằng `build --no-pdf`.")
    else:
        out("ĐỦ ĐIỀU KIỆN. NEXT: report.py extract <các file nguồn> --work <WORK>")


# ---------------------------------------------------------------- extract / find

def cmd_extract(a):
    from extract import extract_file
    work = Path(a.work).expanduser().resolve()
    work.mkdir(parents=True, exist_ok=True)
    combined, listing = [], []
    for k, f in enumerate(a.files, 1):
        src = Path(f).expanduser().resolve()
        if not src.exists():
            raise SystemExit(f"LỖI: không thấy file {src}")
        sub = work / "sources" / f"{k:02d}-{re.sub(r'[^0-9A-Za-z_.-]+', '_', src.stem)[:40]}"
        meta = extract_file(src, sub, dpi=a.dpi, no_images=a.no_images)
        text = (sub / "content.md").read_text(encoding="utf-8")
        combined.append(text.replace(f"# {src.name}", f"# NGUỒN {k}: {src.name}", 1))
        listing.append((k, src.name, meta["type"], meta["pages"], len(text), sub, meta))
    content = "\n\n".join(combined)
    (work / "content.md").write_text(content, encoding="utf-8")
    lines = content.count("\n") + 1
    out(f"Đã trích {len(listing)} file -> {work / 'content.md'} ({len(content):,} ký tự, {lines:,} dòng)")
    kicker_hits = len(re.findall(r"\b\d{1,2}\s*/\s*\d{1,2}\s*·", content))
    if "THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO" in content.upper() or kicker_hits >= 3:
        out("CẢNH BÁO NGUỒN: văn bản trích ra có dấu hiệu là MỘT BÁO CÁO DO CHÍNH SKILL NÀY ĐÃ XUẤT RA TRƯỚC ĐÂY "
            "(thấy kicker 'THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO' và/hoặc nhiều tiêu đề dạng 'NN / NN ·'), "
            "không phải bảng theo dõi/tài liệu gốc. DỪNG LẠI, hỏi người dùng xác nhận đúng file nguồn trước khi viết tiếp — "
            "không tự coi báo cáo cũ là nguồn, vì sẽ lặp lại nguyên mọi số liệu và lỗi của bản cũ.")
    for k, name, typ, pages, n, sub, meta in listing:
        out(f"  NGUỒN {k}: {name} [{typ}, {pages or '?'} trang/slide, {n:,} ký tự]"
            + (f" – ảnh trang: {sub / 'pages'}" if meta["page_images"] else ""))
        for w in meta["warnings"]:
            out(f"    ! {w}")
    # sự thật tính sẵn cho mọi đầu vào (bảng theo dõi + số liệu chung)
    import datetime as _dt
    rep_date = a.date or _dt.date.today().strftime("%d/%m/%Y")
    r = subprocess.run([sys.executable, str(SKILL / "scripts" / "facts.py"), str(work), rep_date] + [str(Path(f).expanduser().resolve()) for f in a.files],
                       capture_output=True, text=True)
    out("  " + (r.stdout.strip() or r.stderr.strip()[-300:]) + f"  -> {work / 'facts.md'}")
    if r.returncode:
        raise SystemExit("LỖI: không tạo được facts đầy đủ; sửa môi trường rồi extract lại. " + r.stderr[-1500:])
    step = 600
    write_status(work, "Bước 1 – trích nguồn", f"{len(listing)} file, {len(content):,} ký tự, {lines:,} dòng",
                 f"Bước 2: đọc hết content.md (đoạn {step} dòng), ghi notes.md; rồi `R new {work}`.")
    if lines > step:
        out(f"\nNEXT: đọc HẾT {work / 'facts.md'}, rồi {work / 'content.md'} theo từng đoạn {step} dòng (offset 1, {step + 1}, "
            f"{2 * step + 1}…). Ghi các ý + số liệu chính ra {work / 'notes.md'} sau mỗi đoạn, "
            f"rồi chạy `report.py new {work}`.")
    else:
        out(f"\nNEXT: đọc toàn bộ {work / 'facts.md'} rồi {work / 'content.md'}, ghi notes.md, rồi chạy `report.py new {work}`.")


def fold(s):
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def cmd_find(a):
    work = Path(a.work).expanduser().resolve()
    content = (work / "content.md").read_text(encoding="utf-8")
    q = fold(a.query)
    src, page, hits = "", "", 0
    for line in content.splitlines():
        if line.startswith("# NGUỒN"):
            src = line[2:].split(":", 1)[0]
        elif line.startswith("## "):
            page = line[3:].strip()
        elif q in fold(line):
            hits += 1
            out(f"[{src} > {page}] {line.strip()[:220]}")
            if hits >= 40:
                out("… (còn nữa, thu hẹp từ khóa)")
                break
    if not hits:
        out(f"KHÔNG THẤY '{a.query}' trong nguồn.")


# ---------------------------------------------------------------- new

def cmd_new(a):
    work = Path(a.work).expanduser().resolve()
    work.mkdir(parents=True, exist_ok=True)
    dst = work / "report.json"
    if dst.exists() and not a.force:
        out(f"Đã có {dst} (không ghi đè; thêm --force để tạo lại).")
    else:
        shutil.copy(SKILL / "assets" / "skeleton.json", dst)
        out(f"Đã tạo {dst} từ khung mẫu.")
    from k7_build import K7
    write_status(work, "Bước 3 – tạo khung report.json", "report.json gần như rỗng, chưa có nội dung thật",
                 f"Viết lại toàn bộ report.json theo 12 mẫu K7 (huong-dan-k7.md), rồi `R build {work}`.")
    out(f"NEXT: đọc {SKILL / 'references' / 'huong-dan-k7.md'} (mục 4-9: cấu trúc, 12 mẫu, giới hạn chữ, icon), "
        f"xem ví dụ {K7 / 'vi-du' / 'vnpt-idecide.json'} và {K7 / 'vi-du' / 'gioi-thieu-vnpt-ai.json'}, "
        f"rồi VIẾT LẠI TOÀN BỘ {dst} bằng nội dung của tài liệu nguồn, chọn mẫu phù hợp cho từng slide. "
        f"Xong chạy `report.py build {work}`.")


# ---------------------------------------------------------------- build

def resolve_json(target):
    p = Path(target).expanduser().resolve()
    if p.is_dir():
        rep = p / "report.json"
        if not rep.is_file() and (p / "_work" / "report.json").is_file():
            rep = p / "_work" / "report.json"  # finish() đã dọn report.json vào _work/ sau khi hoàn tất
        return rep, p
    return p, p.parent


def load_json(path):
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        lines = raw.splitlines()
        ctx = "\n    ".join(f"dòng {k}: {lines[k - 1].strip()[:200]}"
                            for k in (e.lineno - 1, e.lineno) if 0 < k <= len(lines))
        hint = ""
        if "delimiter" in e.msg:
            hint = " (thường do thiếu dấu phẩy giữa hai phần tử, hoặc có dấu \" trong chữ – thay bằng “ ”)"
        elif "Expecting property name" in e.msg:
            hint = " (thường do dấu phẩy thừa trước } hoặc ])"
        return None, (f"report.json sai cú pháp JSON ở dòng {e.lineno}, cột {e.colno}: {e.msg}{hint}\n"
                      f"    {ctx}")


# K7 (mau: bia/so-lieu/the/...): trường toạ độ/tên kỹ thuật, không phải nội dung cần đối chiếu nguồn.
# "mau","icon","src","x","y","w","h","logo","nen","noi","soMuc" theo đúng BO_QUA của k7/cong-cu/kiem-slide.py.
SKIP_KEYS = {"kicker", "num", "weight", "percent", "cols", "tone", "type", "max", "label_width",
             "output_name", "sources", "computed", "theme", "gap", "grow", "dark", "num_cols", "date",
             "mau", "icon", "src", "x", "y", "w", "h", "logo", "nen", "noi", "soMuc", "ban", "ngonNgu",
             "canXacNhan", "id", "ma"}


def _is_bilingual(d):
    return isinstance(d, dict) and ("vi" in d or "en" in d) and not any(isinstance(x, (dict, list)) for x in d.values())


def iter_texts(node, slide=None, key=None):
    """Duyệt mọi chuỗi chữ cần đối chiếu nguồn. Ô song ngữ K7 {"vi":.., "en":..}: chỉ lấy "vi" -
    nguồn luôn tiếng Việt, và số kiểu Anh (1,272) sẽ bị báo nhầm là không khớp nếu lấy cả "en"."""
    if _is_bilingual(node):
        v = node.get("vi") or node.get("en") or ""
        if v:
            yield slide, re.sub(r"^\s*\d+[a-z]?\s*[·|:–—-]\s*", "", v) if key == "dauMuc" else v
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            yield from iter_texts(v, slide, k)
    elif isinstance(node, list):
        for v in node:
            yield from iter_texts(v, slide, key)
    elif isinstance(node, str):
        yield slide, re.sub(r"^\s*\d+[a-z]?\s*[·|:–—-]\s*", "", node) if key == "dauMuc" else node


UNIT_RE = re.compile(r"\s?(%|tỷ|triệu|nghìn|ngàn|TB|GB|Gbps|Mbps)(?![\wÀ-ỹ])", re.IGNORECASE)
SECTION_NO = re.compile(r"^\s*\d{1,2}\s*/\s*\d{1,2}")  # "01 / 04" ở đầu kicker là số thứ tự phần


def slide_texts(s):
    """Mọi chuỗi chữ của một slide cần đối chiếu (kể cả kicker, bỏ số thứ tự phần)."""
    for _, t in iter_texts(s):
        yield t
    if s.get("kicker"):
        yield SECTION_NO.sub("", s["kicker"])


# Vietnamese numbers: dots group thousands only in groups of three; comma is
# decimal. A lone dot with a different group length is a decimal (e.g. 34.6%).
NUMBER_PATTERN = r"\d+(?:[.,]\d+)*"


def numeric_value(token):
    from decimal import Decimal
    token = token.strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", token):
        token = token.replace(".", "")
    return Decimal(token.replace(",", "."))


def percent_matches(value, shown):
    """Accept only rounding to the precision explicitly displayed (half up)."""
    from decimal import Decimal, ROUND_HALF_UP
    if value is None:
        return False
    decimal = shown.split(",", 1)[1] if "," in shown else (
        shown.split(".", 1)[1] if "." in shown and not re.fullmatch(r"\d{1,3}(?:\.\d{3})+", shown) else "")
    quantum = Decimal(1).scaleb(-len(decimal))
    return value.quantize(quantum, rounding=ROUND_HALF_UP) == numeric_value(shown)


def check_numbers(rep, content):
    """Compare numeric values, retaining units. Ratios must be evidenced before
    their rounded percentages are accepted. Never match computed substrings."""
    from decimal import Decimal
    src = re.sub(r"\s+", " ", content)
    computed = [str(c.get("value", "")) for c in rep.get("meta", {}).get("computed", [])
                if isinstance(c, dict) and c.get("formula")]
    values = set()
    units = {}
    for text in [src] + computed:
        for m in re.finditer(NUMBER_PATTERN, text):
            value = numeric_value(m.group())
            values.add(value)
            unit = UNIT_RE.match(text, m.end())
            if unit:
                units.setdefault(unit.group(1).lower(), set()).add(value)
    ratio_re = re.compile(r"(?<![\d/.,])(" + NUMBER_PATTERN + r")\s*/\s*(" + NUMBER_PATTERN + r")(?![\d/.,])")
    source_ratios = {(numeric_value(m[1]), numeric_value(m[2])) for m in ratio_re.finditer(src)}
    missing = {}
    for i, slide in enumerate(rep["slides"], 1):
        for text in slide_texts(slide):
            # Only a directly associated fraction may justify a derived %.
            linked = {}
            pattern = ratio_re.pattern + r"([^%/\n]{0,45}?)(\d+(?:[.,]\d+)?)\s*%"
            for pair in re.finditer(pattern, text):
                a, b = numeric_value(pair[1]), numeric_value(pair[2])
                bridge = pair[3]
                if (a, b) not in source_ratios or not b:
                    continue
                if re.search(r"\d|[,;>≥<≤]|trọng số|điểm|hạng|mục tiêu|tăng|giảm|so với|kế hoạch", bridge, re.I):
                    continue
                if percent_matches(a / b * Decimal(100), pair[4]):
                    linked[pair.start(4)] = True
            for m in re.finditer(NUMBER_PATTERN, text):
                tok = m.group(); value = numeric_value(tok)
                u = UNIT_RE.match(text, m.end())
                if len(tok) < 2 and not u:
                    continue
                if re.match(r"[/.,]\d", text[m.end():m.end()+2]):
                    continue
                if u:
                    unit = u.group(1).lower()
                    known = units.get(unit, set())
                    valid = value in known
                    if unit == "%":
                        valid = valid or m.start() in linked or any(percent_matches(v, tok) for v in known)
                    if not valid:
                        shown = tok + ("" if unit == "%" else " ") + u.group(1)
                        missing.setdefault(shown, set()).add(i)
                elif value not in values:
                    missing.setdefault(tok, set()).add(i)
    return missing


def check_number_format(rep):
    """Cùng một con số (>=4 chữ số) nhưng viết khác cách nhau (có chỗ có dấu chấm phân cách nghìn, có chỗ không)."""
    seen = {}
    for i, s in enumerate(rep["slides"], 1):
        for text in slide_texts(s):
            for m in re.finditer(r"(?<![\d.,])\d{1,3}(?:\.\d{3})+(?![\d.,])|(?<![\d.,])\d{4,}(?![\d.,])", text):
                tok = m.group(0)
                bare = tok.replace(".", "")
                seen.setdefault(bare, {}).setdefault(tok, set()).add(i)
    errs = []
    for bare, variants in seen.items():
        if len(variants) > 1:
            parts = "; ".join(f"\"{v}\" (slide {','.join(map(str, sorted(sl)))})" for v, sl in variants.items())
            errs.append(f"số {bare}: {parts}")
    return errs


def _pct_ok(a, b, shown):
    """a/b có làm tròn ra đúng 'shown' (chuỗi % như '37,5') không."""
    if not b:
        return False
    from decimal import Decimal
    return percent_matches(Decimal(str(a)) / Decimal(str(b)) * Decimal(100), shown)


def check_consistency(rep):
    """Số trong báo cáo tự mâu thuẫn: tỷ lệ % không khớp phân số đi kèm, thanh tỷ lệ, tiến độ."""
    errs = []
    frac = re.compile(r"(?<![\d/.,])(\d[\d.,]*)\s*/\s*(\d[\d.,]*)(?![\d/])([^%/\n]{0,45}?)(\d+(?:[.,]\d+)?)\s?%")
    for i, s in enumerate(rep["slides"], 1):
        blocks = []
        for row in s.get("rows") or []:
            for b in row.get("blocks", []):
                blocks += b.get("blocks", []) if b.get("type") == "stack" else [b]
        for b in blocks:
            if b.get("type") == "split":
                parts = b.get("parts") or []
                total = sum(float(p.get("weight") or 0) for p in parts)
                for p in parts:
                    m = re.match(r"\**\s*(\d+(?:,\d+)?)\s?%", str(p.get("desc", "")))
                    if m and total and not _pct_ok(float(p["weight"]), total, m.group(1)):
                        right = f"{float(p['weight']) / total * 100:.1f}".replace(".", ",")
                        errs.append(f"slide {i}: thanh tỷ lệ “{p.get('label')}” ghi {m.group(1)}% nhưng "
                                    f"{p['weight']:g}/{total:g} = {right}%")
            if b.get("type") == "progress":
                vm = re.search(r"\d+(?:,\d+)?", str(b.get("value", "")))
                if vm and isinstance(b.get("percent"), (int, float)) and abs(vn_num(vm.group(0)) - b["percent"]) > 0.6:
                    errs.append(f"slide {i}: progress value “{b['value']}” khác percent {b['percent']}")
        for text in slide_texts(s):
            for m in frac.finditer(text):
                if re.search(r"\d", m.group(3)):
                    continue  # giữa phân số và % còn số khác: không chắc là cặp
                if re.search(r"trọng số|điểm|hạng|mục tiêu|tăng|giảm|so với|kế hoạch", m.group(3).lower()):
                    continue  # % đó là chỉ số khác, không phải tỷ lệ của phân số
                if re.search(r"[,;>≥<≤]", m.group(3)):
                    continue  # sang vế câu khác: % không gắn với phân số
                if m.group(2) in ("5", "10", "100") and "," in m.group(1):
                    continue  # điểm số kiểu 9,0/10
                try:
                    a, bb = vn_num(m.group(1)), vn_num(m.group(2))
                except ValueError:
                    continue
                if not bb:
                    errs.append(f"slide {i}: tỷ lệ có mẫu số 0: {m.group(0).strip()}")
                    continue
                if not _pct_ok(a, bb, m.group(4)):
                    right = f"{a / bb * 100:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                    errs.append(f"slide {i}: “{m.group(0).strip()}” – {m.group(1)}/{m.group(2)} = {right}%")
    return errs


def _words(text):
    return re.findall(r"[0-9a-zà-ỹđ]+", unicodedata.normalize("NFC", text.lower()))


def _ngrams(text, n=3):
    w = _words(text)
    return {" ".join(w[k:k + n]) for k in range(len(w) - n + 1)}


# Nhãn chuẩn của skill (được phép dùng ở mọi báo cáo dù nguồn không có)
STANDARD_LABELS = """Thông điệp tổng hợp trình lãnh đạo. Kết quả chính và kiến nghị. Đã đạt được. Kiến nghị.
Tiếp theo. Khó khăn, rủi ro. Khó khăn, vướng mắc. Kết quả thực hiện. Trọng tâm thời gian tới. Vướng mắc trọng tâm.
Hoàn thành. Đang triển khai. Đang đánh giá. Chưa hoàn thành. Ghi chú. Nguyên tắc. Mục tiêu. Thông điệp, kiến nghị.
Danh mục. Chi tiết. Báo cáo tiến độ triển khai."""


def check_example_leak(rep, content):
    """Cụm 3 từ lấy từ ví dụ mẫu mà nguồn không có -> nhiều khả năng chép nhầm (vd 'CHUYÊN ĐỀ 05').
    Chỉ xét cụm có chữ số hoặc có từ hoàn toàn không xuất hiện trong nguồn (tránh báo nhầm cụm thông dụng).
    'Có trong nguồn' = 3 từ cùng xuất hiện trong khoảng 12 từ liên tiếp (PDF nhiều cột hay làm đứt cụm)."""
    from k7_build import K7
    ex_files = sorted((K7 / "vi-du").glob("*.json"))
    if not ex_files:
        return []
    ex_slides = []
    for ex in ex_files:
        ex_slides += json.loads(ex.read_text(encoding="utf-8")).get("slides", [])
    ex_ng = set()
    for s in ex_slides:
        for t in slide_texts(s):
            ex_ng |= _ngrams(t)
    ex_ng -= _ngrams(STANDARD_LABELS) | _ngrams((SKILL / "assets" / "skeleton.json").read_text(encoding="utf-8"))
    sw = _words(content)
    pos = {}
    for k, w in enumerate(sw):
        pos.setdefault(w, []).append(k)

    def in_source(g):
        ws = g.split()
        if any(w not in pos for w in ws):
            return False
        for a in pos[ws[0]]:
            if all(any(abs(b - a) <= 12 for b in pos[w]) for w in ws[1:]):
                return True
        return False

    hits = {}
    for i, s in enumerate(rep["slides"], 1):
        for text in slide_texts(s):
            for g in _ngrams(text) & ex_ng:
                ws = g.split()
                # A missing common word is not evidence of copying. Require a
                # number (stat copied from the wrong deck) as the distinctive signal.
                distinctive = bool(re.search(r"\d", g))
                if distinctive and not in_source(g):
                    hits.setdefault(g, set()).add(i)
    return sorted(hits.items(), key=lambda kv: min(kv[1]))


def vn_num(s):
    """'12.480' -> 12480, '74,92' -> 74.92, '1.2' -> 1.2 (dấu chấm + đúng 3 số = phân cách nghìn)."""
    s = s.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", s):
        return float(s.replace(".", "").replace(",", "."))
    return float(s.replace(",", "."))


def check_formulas(rep):
    """Tính lại từng phép tính trong meta.computed; trả về danh sách lỗi."""
    errs = []
    for c in rep.get("meta", {}).get("computed") or []:
        if not isinstance(c, dict):
            continue
        value, formula = str(c.get("value", "")), str(c.get("formula", ""))
        left = formula.split("=")[0]
        expr = re.sub(r"\d+(?:[.,]\d+)*", lambda m: repr(vn_num(m.group(0))), left)
        expr = expr.replace("×", "*").replace("x", "*").replace("÷", "/").replace("%", "")
        vm = re.search(r"\d+(?:[.,]\d+)*", value)
        if not vm or not re.fullmatch(r"[\d.\s+\-*/()e]+", expr) or not re.search(r"[+\-*/]", expr):
            continue  # không phải biểu thức số đơn giản: bỏ qua
        try:
            got = eval(expr, {"__builtins__": {}})  # chỉ còn số và + - * / ( )
        except Exception:
            continue
        want = vn_num(vm.group(0))
        dec = len(vm.group(0).split(",")[1]) if "," in vm.group(0) and not re.fullmatch(r"\d{1,3}(\.\d{3})+", vm.group(0)) else 0
        tol = 0.5 * 10 ** -dec + 1e-9
        cands = [got, got * 100] if "%" in value else [got]
        if not any(abs(g - want) <= tol for g in cands):
            shown = cands[-1]
            right = f"{shown:,.{max(dec, 2)}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
            errs.append(f"\"{value}\" sai: {left.strip()} = {right}{'%' if '%' in value else ''}")
    return errs


def unused_source_numbers(rep, content):
    """Các số/ngày có trong nguồn nhưng không xuất hiện ở báo cáo (để phát hiện bỏ sót)."""
    lines, in_header = [], False
    for l in content.splitlines():  # bỏ phần metadata từ "# NGUỒN" đến "## Trang/Slide/Toàn văn" đầu tiên
        if l.startswith("# "):
            in_header = True
        elif l.startswith("## "):
            in_header = False
        elif not in_header:
            lines.append(l)
    body = "\n".join(lines)
    report_text = json.dumps(rep["slides"], ensure_ascii=False)
    seen, out_ = set(), []
    for m in re.finditer(r"\d+(?:[.,/]\d+)*", body):
        tok = m.group(0).rstrip(".,")
        if len(tok) < 2 or tok in seen:
            continue
        seen.add(tok)
        important = (UNIT_RE.match(body, m.end()) or re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}|\d{1,2}/\d{4}", tok)
                     or re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?", tok))
        if not important:
            continue  # chỉ nhắc số có đơn vị (%, tỷ…), ngày tháng, số lớn – số trơn quá nhiễu
        alt = tok.translate(str.maketrans(",.", ".,"))
        if tok not in report_text and alt not in report_text:
            ctx = body[max(0, m.start() - 35):m.end() + 25].replace("\n", " ").strip()
            out_.append((tok, ctx))
    return out_


COMMON_CAPS = set("""báo cáo tiến độ tổng quan kết quả kiến nghị đã đạt được tiếp theo thông điệp tổng hợp trình lãnh đạo
khó khăn vướng mắc rủi ro đơn vị mục hạn nhóm việc slide trang cập nhật ngày tháng năm quý giai đoạn đề xuất
chưa bắt đầu đang thực hiện hoàn thành chậm trễ quá hạn đầu việc phụ lục ghi chú nguồn tổng cộng""".split())


def check_invented_names(rep, content):
    """Tên riêng (≥2 từ liền nhau, MỌI từ viết hoa chữ đầu, không viết hoa toàn bộ) có từ KHÔNG xuất hiện ở đâu
    trong nguồn -> nghi bịa (vd 'Nam Cần Thơ' khi nguồn chỉ ghi 'South'). Bỏ qua từ đầu câu và nhãn chuẩn."""
    src = set(_words(content))
    hits = {}
    tok = re.compile(r"[^\W\d_]+", re.UNICODE)
    for i, s in enumerate(rep["slides"], 1):
        for text in slide_texts(s):
            text = unicodedata.normalize("NFC", text)
            for sent in re.split(r"(?<=[.!?:;•|\n])\s*|\s+[–—-]\s+", text):
                ws = [(m.group(0), m.start()) for m in tok.finditer(sent)]
                run = []
                for k, (w, _) in enumerate(ws + [("", 0)]):
                    title = w[:1].isupper() and not w.isupper() and len(w) > 1
                    if title and k > 0:          # từ đầu câu viết hoa theo ngữ pháp: không tính
                        run.append(w); continue
                    if len(run) >= 2:
                        lw = [x.lower() for x in run]
                        if not all(x in COMMON_CAPS for x in lw) and any(x not in src and x not in COMMON_CAPS for x in lw):
                            hits.setdefault(" ".join(run), set()).add(i)
                    run = []
    return sorted(hits.items(), key=lambda x: min(x[1]))


def check_semantic_scope(rep, work):
    """Kiểm số/trạng thái gắn đúng đơn vị, mục so với bảng theo dõi (nếu nguồn là bảng). Xem semantic.py."""
    files = sorted((work / "tracker").glob("*/tracker.json")) if (work / "tracker").exists() else []
    if not files:
        return []
    from semantic import check_semantics
    errs = []
    for f in files:
        try:
            rows = json.loads(f.read_text(encoding="utf-8")).get("rows", [])
        except Exception:
            continue
        errs += check_semantics(rep, rows, slide_texts)
    return errs


def cmd_build(a):
    from k7_build import kiem_k7, render_k7
    path, work = resolve_json(a.target)
    if not path.exists():
        raise SystemExit(f"LỖI: không thấy {path}. NEXT: report.py new {work}")
    attempts_file = work / ".build_attempts"
    attempts = int(attempts_file.read_text() or 0) + 1 if attempts_file.exists() else 1
    attempts_file.write_text(str(attempts))
    out(f"== BUILD {path}" + (f" (lần sửa thứ {attempts - 1})" if attempts > 1 else "") + " ==")

    rep, err = load_json(path)
    if err:
        out("[1] Cấu trúc: LỖI\n  " + err)
        out(f"NEXT: sửa đúng dòng trên trong {path} rồi chạy lại `report.py build {work}`.")
        sys.exit(1)
    ds = kiem_k7(rep)
    errors = [f"{x['vi_tri']} · {x['ma']}: {x['y']}" for x in ds if x["muc"] == "loi"]
    nhac = [x for x in ds if x["muc"] == "nhac"]
    if errors:
        out(f"[1] Cấu trúc (K7 kiem-slide.py): LỖI ({len(errors)})")
        for e in errors[:30]:
            out("  - " + e)
        out(f"NEXT: sửa các mục trên (tra {SKILL / 'references' / 'huong-dan-k7.md'} mục 4-9) rồi chạy lại build.")
        sys.exit(1)
    out(f"[1] Cấu trúc (K7 kiem-slide.py): OK ({len(rep['slides'])} slide" +
        (f", {len(nhac)} nhắc" if nhac else "") + ")")
    for x in nhac[:10]:
        out(f"  (nhắc) {x['vi_tri']} · {x['ma']}: {x['y']}")

    name = (rep.get("meta") or {}).get("output_name") or path.stem
    name = re.sub(r"[^\w.-]+", "_", name, flags=re.UNICODE)
    html_path = work / f"{name}.html"
    html_path.write_text(render_k7(rep), encoding="utf-8")
    out(f"[2] HTML: {html_path}")

    problems = []
    content_file = work / "content.md"
    if content_file.exists():
        missing = check_numbers(rep, content_file.read_text(encoding="utf-8"))
        if missing:
            soft = False  # lỗi không được hạ thành cảnh báo sau nhiều lần thử
            out(f"[3] Số liệu: {'CẢNH BÁO' if soft else 'LỖI'} – {len(missing)} số không thấy trong nguồn:")
            for tok, sl in list(missing.items())[:25]:
                out(f"  - \"{tok}\" (slide {', '.join(map(str, sorted(sl)))})")
            out("    Với từng số: chạy `report.py find WORK \"<số>\"`. Có trong nguồn dưới dạng khác → chép đúng như nguồn; "
                "số tự tính → thêm vào meta.computed: {\"value\": \"<số>\", \"formula\": \"<phép tính>\"}; "
                "không có căn cứ → XÓA khỏi báo cáo.")
            if not soft:
                problems.append("số liệu")
        else:
            out("[3] Số liệu: OK (mọi con số đều có trong nguồn hoặc meta.computed)")
        ferr = check_formulas(rep)
        if ferr:
            out(f"[3b] Phép tính: LỖI – {len(ferr)} số tự tính bị tính sai:")
            for e in ferr:
                out("  - " + e)
            out("    Sửa con số ở meta.computed VÀ ở mọi slide đang dùng số đó cho đúng kết quả trên.")
            problems.append("phép tính")
        elif rep["meta"].get("computed"):
            out("[3b] Phép tính: OK")
        cerr = check_consistency(rep)
        if cerr:
            out(f"[3d] Nhất quán: LỖI – {len(cerr)} tỷ lệ không khớp số đi kèm:")
            for e in cerr[:15]:
                out("  - " + e)
            out("    Sửa tỷ lệ cho đúng phép chia (làm tròn đúng), hoặc sửa số đi kèm cho đúng nguồn.")
            problems.append("nhất quán")
        leak = check_example_leak(rep, content_file.read_text(encoding="utf-8"))
        if leak:
            out(f"[3e] Chép từ ví dụ mẫu: LỖI – {len(leak)} cụm từ có trong ví dụ ATBM nhưng KHÔNG có trong nguồn:")
            for g, sl in leak[:12]:
                out(f"  - “{g}” (slide {', '.join(map(str, sorted(sl)))})")
            out("    Ví dụ chỉ để tham khảo cấu trúc. Thay bằng nội dung/tên đơn vị có trong nguồn, hoặc xóa.")
            problems.append("chép ví dụ")
        names = check_invented_names(rep, content_file.read_text(encoding="utf-8"))
        if names:
            out(f"[3g] Tên riêng không có trong nguồn: LỖI – {len(names)} tên:")
            for g, sl in names[:10]:
                out(f"  - “{g}” (slide {', '.join(map(str, sorted(sl)))})")
            out("    Tên đơn vị, địa danh, người phải lấy đúng như nguồn. Không tự đặt tên/diễn giải tên (vd nguồn ghi 'South' thì giữ 'South'). Sửa hoặc xóa.")
            problems.append("tên không có trong nguồn")
        serr = check_semantic_scope(rep, work)
        if serr:
            soft = False  # lỗi không được hạ thành cảnh báo sau nhiều lần thử
            out(f"[3f] Gắn số/trạng thái sai chỗ: {'CẢNH BÁO' if soft else 'LỖI'} – {len(serr)} chỗ không khớp bảng theo dõi:")
            for e in serr[:15]:
                out("  - " + e)
            out("    Số có trong nguồn nhưng gắn nhầm đơn vị/mục/trạng thái. Sửa theo nguồn (xem WORK/facts.md, `report.py find`), "
                "không đổi số cho vừa lời.")
            if not soft:
                problems.append("gắn sai đơn vị/trạng thái")
        elif list((work / "tracker").glob("*/tracker.json")) if (work / "tracker").exists() else False:
            out("[3f] Gắn số/trạng thái đúng đơn vị: OK")
        fmt_err = check_number_format(rep)
        if fmt_err:
            out(f"[3h] Định dạng số: NHẮC – {len(fmt_err)} số viết không nhất quán giữa các slide:")
            for e in fmt_err[:15]:
                out("  - " + e)
            out("    Cùng một số phải viết giống nhau mọi nơi trong báo cáo (có dấu chấm phân cách nghìn thì dùng xuyên suốt).")
            # Equivalent grouping styles are editorial, never a blocking error.
        unused = unused_source_numbers(rep, content_file.read_text(encoding="utf-8"))
        if unused:
            out(f"[3c] Số trong nguồn CHƯA dùng ({len(unused)}) – không phải lỗi; kiểm tra có bỏ sót ý quan trọng "
                "(kinh phí, thời hạn, tiến độ, mục tiêu) không, nếu có thì thêm vào slide phù hợp:")
            for tok, ctx in unused[:10]:
                out(f"  - {tok}: …{ctx}…")
            if len(unused) > 10:
                out(f"  … và {len(unused) - 10} số khác (xem bằng `report.py find`)")
    else:
        out(f"[3] Số liệu: BỎ QUA (không có {content_file}; chạy `report.py extract … --work {work}` để bật kiểm tra)")

    from export_pdf import find_browser, print_pdf, pdf_pages, previews
    from k7_build import check_overflow_k7
    browser = find_browser()
    if not browser:
        out("[4] Tràn chữ: BỎ QUA – không tìm thấy Chrome/Edge/Chromium (xem `report.py env`).")
    else:
        ov, e = check_overflow_k7(browser, html_path)
        if e:
            out(f"[4] Tràn chữ: BỎ QUA – {e}")
        elif ov:
            out(f"[4] Tràn chữ (K7 M7): LỖI ở {len(ov)} chỗ (khung K7 khoá sẵn, không tự thu nhỏ chữ được):")
            for o in ov:
                out(f"  - slide {o['slide']}: {o['y']}")
            out("    Cách sửa: rút gọn câu trong giới hạn ký tự của mẫu (HUONG-DAN-CHO-AI.md mục 5); "
                "bớt mục trong danh sách; tách sang slide khác. KHÔNG sửa CSS/HTML của khung.")
            problems.append("tràn chữ")
        else:
            out("[4] Tràn chữ: OK")

    if browser and not a.no_pdf:
        pdf_path = work / f"{name}.pdf"
        e = print_pdf(browser, html_path, pdf_path)
        if e:
            out(f"[5] PDF: LỖI – {e}")
            problems.append("PDF")
        else:
            n, n_slides = pdf_pages(pdf_path), len(rep["slides"])
            ok = n in (None, n_slides)
            out(f"[5] PDF: {pdf_path} ({n} trang" + ("" if ok else f" ≠ {n_slides} slide") + ")")
            if not ok:
                problems.append("số trang PDF")
            files, sheets = previews(pdf_path, work / "_preview", dpi=a.dpi)
            if files:
                out(f"[6] Ảnh xem trước: {work / '_preview'} ({len(files)} ảnh; ghép: "
                    f"{', '.join(str(s) for s in sheets) or 'không'})")
    else:
        out("[5] PDF: BỎ QUA")

    if problems:
        if attempts > MAX_ATTEMPTS:
            write_status(work, "Bước 4 – build", f"DỪNG SAU {attempts - 1} LẦN SỬA: vẫn còn {', '.join(problems)}",
                         f"KHÔNG chạy build nữa. Báo người dùng: bản nháp {html_path.name}, log {work / 'build.log'}, "
                         f"các lỗi còn lại ở trên. Để người dùng quyết định sửa tay hay đổi cách trình bày.")
            out(f"\nKẾT QUẢ: DỪNG – đã sửa {attempts - 1} lần vẫn còn lỗi ({', '.join(problems)}).")
            out(f"NEXT: KHÔNG gọi build lại nữa. Dừng ở đây, báo người dùng rõ: còn lỗi gì (xem trên), "
                f"bản nháp đang có ở {html_path}, chi tiết ở {work / 'build.log'}. Không tự ý rút gọn nội dung quan trọng "
                f"để né lỗi tràn chữ; để người dùng quyết định.")
            sys.exit(1)
        write_status(work, "Bước 4 – build", f"CẦN SỬA: {', '.join(problems)} (chạy lại build để xem chi tiết)",
                     f"Sửa report.json (ghi lại toàn bộ file) theo các dòng LỖI, rồi `R build {work}`.")
        out(f"\nKẾT QUẢ: CẦN SỬA ({', '.join(problems)})")
        out(f"NEXT: sửa {path} theo các dòng LỖI ở trên rồi chạy lại `report.py build {work}`."
            + (f" Còn {MAX_ATTEMPTS - attempts + 1} lần thử nữa trước khi PHẢI dừng và báo người dùng." if attempts >= MAX_ATTEMPTS - 1 else ""))
        sys.exit(1)
    attempts_file.unlink(missing_ok=True)
    write_status(work, "Bước 4 – build", f"XONG: {html_path.name} + PDF, {len(rep['slides'])} slide. "
                 "Nếu sửa report.json sau lúc này thì PHẢI build lại, nếu không PDF sẽ cũ hơn report.json.",
                 "Bước 5 (xem ảnh _preview, chỉ sửa khi thật cần) → bước 6 (docx nếu cần) → bước 7 trả lời người dùng.")
    out("\nKẾT QUẢ: XONG")
    out("NEXT: (nếu đọc được ảnh) mở các ảnh trong _preview/ kiểm tra bố cục; có chỗ xấu thì sửa report.json, build lại. "
        f"Cần Word thì chạy `report.py docx {work}`. Sau đó trả lời người dùng: đường dẫn HTML + PDF, số slide, "
        "các số tự tính (meta.computed) và điểm còn chưa chắc.")


def cmd_docx(a):
    from to_docx import build_docx
    path, work = resolve_json(a.target)
    rep, err = load_json(path)
    if err:
        raise SystemExit(err)
    name = re.sub(r"[^\w.-]+", "_", rep.get("meta", {}).get("output_name") or path.stem, flags=re.UNICODE)
    dst = Path(a.out).expanduser().resolve() if a.out else work / f"{name}.docx"
    build_docx(rep, dst)
    import docx
    d = docx.Document(dst)
    n_par = sum(1 for p in d.paragraphs if p.text.strip())
    out(f"Word: {dst} ({n_par} đoạn, {len(d.tables)} bảng, {len(rep['slides'])} slide)")


def cmd_calc(a):
    """Tính một biểu thức bằng số kiểu Việt Nam, in giá trị và dòng computed để chép vào meta.computed."""
    expr = a.expr
    py = re.sub(r"\d+(?:[.,]\d+)*", lambda m: repr(vn_num(m.group(0))), expr).replace("×", "*").replace("x", "*").replace("÷", "/")
    if not re.fullmatch(r"[\d.\s+\-*/()e]+", py):
        raise SystemExit("LỖI: chỉ dùng số và + - * / ( )")
    v = eval(py, {"__builtins__": {}})
    if a.percent: v *= 100
    d = a.decimals
    if d < 0:  # tự động: giữ số chữ số thập phân lớn nhất của các số đầu vào (tối thiểu 1 nếu kết quả lẻ)
        decs = [len(x.split(",")[1]) for x in re.findall(r"\d+,\d+", expr)]
        d = max(decs + ([1] if abs(v - round(v)) > 1e-9 else [0]))
    shown = f"{v:,.{d}f}".replace(",", " ").replace(".", ",").replace(" ", ".") if d else f"{round(v):,}".replace(",", ".")
    shown += "%" if a.percent else ""
    out(f"KẾT QUẢ: {shown}")
    out(json.dumps({"value": shown, "formula": f"{expr} = {shown}"}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("env").set_defaults(fn=cmd_env)
    p = sp.add_parser("extract")
    p.add_argument("files", nargs="+")
    p.add_argument("--work", required=True)
    p.add_argument("--dpi", type=int, default=60)
    p.add_argument("--no-images", action="store_true")
    p.add_argument("--date", help="ngày báo cáo DD/MM/YYYY (mặc định hôm nay)")
    p.set_defaults(fn=cmd_extract)
    p = sp.add_parser("calc", help="tính biểu thức, in dòng computed")
    p.add_argument("expr"); p.add_argument("--percent", action="store_true"); p.add_argument("--decimals", type=int, default=-1, help="số chữ số thập phân (mặc định tự động)")
    p.set_defaults(fn=cmd_calc)
    p = sp.add_parser("find")
    p.add_argument("work")
    p.add_argument("query")
    p.set_defaults(fn=cmd_find)
    p = sp.add_parser("new")
    p.add_argument("work")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_new)
    p = sp.add_parser("build")
    p.add_argument("target", help="WORK hoặc đường dẫn report.json")
    p.add_argument("--no-pdf", action="store_true")
    p.add_argument("--dpi", type=int, default=60, help="độ nét ảnh xem trước")
    p.set_defaults(fn=cmd_build)
    p = sp.add_parser("docx")
    p.add_argument("target")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_docx)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
