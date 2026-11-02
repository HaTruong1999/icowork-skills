#!/usr/bin/env python3
"""Kiểm bằng CODE: số/trạng thái trong báo cáo có gắn đúng ĐƠN VỊ, MỤC, TRẠNG THÁI so với bảng theo dõi không.

Bắt các lỗi mà kiểm "số có trong nguồn" bỏ lọt (con số đúng nhưng gán sai chỗ):
  S1  trạng thái «Hoàn thành/xong» cho một mục trong khi còn dòng chưa xong;
  S2  «đơn vị X chưa bắt đầu (mục N)» trong khi X đã/đang làm mục đó;
  S3  phân số a/b đứng cạnh tên đơn vị X nhưng không phải số của X (dòng, tổng mục, tổng chung của X);
  S4  mã dòng (vd 3.c) liệt kê cho đơn vị X nhưng dòng đó thuộc đơn vị khác;
  S5  «X xong a/b đầu việc» không khớp số dòng xong/tổng dòng của X.
Chỉ dùng dữ liệu đã đọc từ bảng (WORK/tracker/*/tracker.json); không có bảng thì không chạy. Không đoán nghĩa:
chỉ báo khi tên đơn vị + dấu hiệu xuất hiện rõ trong cùng một mệnh đề.
"""
import re
from collections import defaultdict

FRAC = re.compile(r"(?<![\d/.,])(\d{1,3}(?:\.\d{3})+|\d+)\s*/\s*(\d{1,3}(?:\.\d{3})+|\d+)(?![\d/])(\s*(?:đầu việc|việc|mục|dòng)\b)?", re.I)
ROWID = re.compile(r"(?<![\d.])(\d{1,2}\.[a-z])(?![\w.])", re.I)
DONE_WORD = re.compile(r"(?<!chưa )(?<!chưa\s)(hoàn thành|đã xong|xong)(?!\s*\d)", re.I)
NOT_DONE_NEAR = re.compile(r"chưa|đang|một phần|trễ|quá hạn|chậm|\d\s*/\s*\d", re.I)
NOT_STARTED = re.compile(r"chưa (bắt đầu|thực hiện|làm|triển khai)|not started", re.I)
SEG = re.compile(r"[.;|•\n]+(?!\d)")


def num(s): return float(s.replace(".", ""))


def key(u): return re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", u or "")).strip().lower()


class Table:
    def __init__(self, rows):
        keep = []
        for r in rows:
            if not r.get('st'):continue
            if re.match(r'^\s*(tổng|cộng|total)',str(r.get('task') or ''),re.I):continue
            if any(x['stt'].startswith(r['stt']+'.') for x in rows):continue
            keep.append(r)  # raw detail rows; duplicates are not confirmed extra work
        self.rows = keep
        self.by_unit = defaultdict(list)
        self.by_item = defaultdict(list)
        for r in self.rows:
            if r.get("unit"): self.by_unit[key(r["unit"])].append(r)
            self.by_item[r["stt"].split(".")[0]].append(r)
        self.names = {key(r["unit"]): r["unit"] for r in self.rows if r.get("unit")}
        self.id2unit = {r["stt"].lower(): key(r.get("unit", "")) for r in self.rows}

    def fractions_of(self, u):
        """Mọi phân số hợp lệ của đơn vị u: từng dòng, tổng từng mục, tổng chung (cùng đơn vị đo)."""
        ok = set(); per_item = defaultdict(lambda: [0.0, 0.0]); tot = defaultdict(lambda: [0.0, 0.0])
        for r in self.by_unit.get(u, []):
            for m in re.finditer(r"(\d{1,3}(?:\.\d{3})+|\d+)\s*/\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:\s*([A-Za-zÀ-ỹđ]+))?", r.get("result", "")):
                a, b = num(m.group(1)), num(m.group(2))
                if not b or a > b: continue
                ok.add((a, b)); unit = (m.group(3) or "").lower()
                it = r["stt"].split(".")[0]
                per_item[(it, unit)][0] += a; per_item[(it, unit)][1] += b
                tot[unit][0] += a; tot[unit][1] += b
        ok |= {tuple(v) for v in per_item.values()}
        return ok

    def global_fractions(self):
        """Phân số thuộc về TOÀN BỘ (tổng chung, tổng từng mục qua mọi đơn vị): không gán cho riêng đơn vị nào."""
        ok = set(); per_item = defaultdict(lambda: [0.0, 0.0]); tot = defaultdict(lambda: [0.0, 0.0])
        for r in self.rows:
            for m in re.finditer(r"(\d{1,3}(?:\.\d{3})+|\d+)\s*/\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:\s*([A-Za-zÀ-ỹđ]+))?", r.get("result", "")):
                a, b = num(m.group(1)), num(m.group(2))
                if not b or a > b: continue
                unit = (m.group(3) or "").lower(); it = r["stt"].split(".")[0]
                per_item[(it, unit)][0] += a; per_item[(it, unit)][1] += b; tot[unit][0] += a; tot[unit][1] += b
        return {tuple(v) for v in per_item.values()}

    def counts_of(self, u):
        """(xong, tổng) số dòng của đơn vị: tổng chung và theo từng mục."""
        out = set(); rows = self.by_unit.get(u, [])
        out.add((sum(r["st"] == "xong" for r in rows), len(rows)))
        by = defaultdict(list)
        for r in rows: by[r["stt"].split(".")[0]].append(r)
        for rs in by.values(): out.add((sum(r["st"] == "xong" for r in rs), len(rs)))
        return out


def segments(text):
    return [s for s in SEG.split(text) if s.strip()]


def check_text(t, text, where, errs):
    """Một chuỗi chữ của báo cáo. where = mô tả vị trí (vd 'slide 3')."""
    for seg in segments(text):
        low = seg.lower()
        hits = sorted((m.start(), m.end(), u) for u in t.names for m in re.finditer(rf"(?<![\w]){re.escape(u)}(?![\wÀ-ỹ])", low))
        # bỏ tên đơn vị nằm trọn trong tên dài hơn (vd 'vnpt it' trong 'vnpt it (tt attt)' đã bị bỏ ngoặc nên không xảy ra)
        hits = [h for h in hits if not any(o != h and o[0] <= h[0] and h[1] <= o[1] for o in hits)]
        for idx, (s, e, u) in enumerate(hits):
            end = hits[idx + 1][0] if idx + 1 < len(hits) else len(seg)
            clause = seg[e:min(end, e + 90)]
            cl = clause.lower()
            name = t.names[u]
            # S2: chưa bắt đầu – chỉ báo khi MÂU THUẪN chắc chắn
            # Cắt mệnh đề tại dấu phẩy liệt kê gần nhất (không phải phẩy thập phân, vd "82,8") trước khi tìm
            # "chưa bắt đầu": văn bản hay viết tắt tên đơn vị trong danh sách (vd "VNPT Net 150/450 · VNP, TTP
            # chưa bắt đầu") – nếu "VNP"/"TTP" không khớp tên đầy đủ trong bảng, ranh giới mệnh đề cũ sẽ chạy
            # tới hết đoạn và gán nhầm "chưa bắt đầu" của đơn vị liệt kê sau dấu phẩy ngược về đơn vị đang xét.
            cut = re.search(r"(?<!\d),(?!\d)", cl)
            scope_cl = cl[:cut.start()] if cut else cl
            if NOT_STARTED.search(scope_cl):
                items = set(re.findall(r"(?:mục|m)\s*(\d{1,2})\b", scope_cl)) | \
                        {i.split(".")[0] for i in ROWID.findall(clause[:cut.start() if cut else len(clause)])}
                rows = t.by_unit.get(u, [])
                if items:      # có nêu mục: các dòng của đơn vị ở mục đó đều phải chưa bắt đầu
                    scope = [r for r in rows if r["stt"].split(".")[0] in items]
                    if scope and any(r["st"] != "chua" for r in scope):
                        bad = [f"{r['stt']} ({r['status']})" for r in scope if r["st"] != "chua"][:4]
                        errs.append(f"{where}: «{name} … chưa bắt đầu (mục {', '.join(sorted(items))})» nhưng nguồn: " + ", ".join(bad))
                elif rows and not any(r["st"] == "chua" for r in rows):   # không nêu mục: đơn vị phải có ít nhất 1 dòng chưa bắt đầu
                    errs.append(f"{where}: «{name} … chưa bắt đầu» nhưng nguồn không có dòng nào của {name} ở trạng thái chưa bắt đầu")
            # S3/S5: phân số đứng ngay sau tên đơn vị (≤ 40 ký tự, chưa có mục khác chen vào)
            allowed = None
            for m in FRAC.finditer(clause[:45]):
                a, b = num(m.group(1)), num(m.group(2))
                if b == 0 or a > b: continue
                before = seg[max(0, e - 60):e + m.start()].lower()   # cả phần đứng trước tên đơn vị trong mệnh đề
                if re.search(r"(?:mục|\bm)\s*\d{1,2}\b|\b\d{1,2}\.[a-z]\b", before): continue   # phân số này thuộc một mục/dòng cụ thể, không phải của riêng đơn vị
                tail = clause[m.end():m.end() + 14].lower()
                if m.group(3) or re.match(r"\s*(đầu việc|việc|mục|dòng)", tail):   # S5: đếm đầu việc – chỉ khi liền sau tên đơn vị
                    gap = clause[:m.start()].lower()
                    if re.fullmatch(r"[\s:·\-–,()]*(?:đã\s+)?(?:xong|hoàn thành)?[\s:·\-–,()]*", gap) and (a, b) not in t.counts_of(u) and b <= 40:
                        errs.append(f"{where}: «{name} … {m.group(1)}/{m.group(2)} đầu việc» – nguồn: {name} xong " +
                                    " hoặc ".join(f"{x:g}/{y:g}" for x, y in sorted(t.counts_of(u))[:3]))
                    continue
                if b <= 12 and a <= 31: continue   # có thể là ngày dd/mm
                mine = t.fractions_of(u); glob = t.global_fractions()
                if (a, b) in mine or (a, b) in glob: continue
                owners = [t.names[v] for v in t.by_unit if v != u and (a, b) in t.fractions_of(v)]
                if owners:   # số có thật nhưng là của đơn vị khác → gán nhầm
                    errs.append(f"{where}: «{name} … {m.group(1)}/{m.group(2)}» – số này là của {owners[0]}, không phải của {name}")
            # S4: mã dòng liệt kê cho đơn vị
            for rid in ROWID.findall(clause[:60]):
                owner = t.id2unit.get(rid.lower())
                if owner and owner != u:
                    errs.append(f"{where}: mã dòng {rid} gán cho {name} nhưng nguồn ghi dòng {rid} thuộc {t.names.get(owner, owner)}")

    # S9: "Mục N ... Chưa bắt đầu/Chưa thực hiện" KHÔNG gắn với tên đơn vị nào (vd nhãn trên biểu đồ/thẻ:
    # "Mục 2 · Vá lỗ hổng mức cao – Chưa bắt đầu") – S2 ở trên chỉ bắt khi có tên đơn vị đứng trước, bỏ sót dạng này.
    # Chỉ xét trong CÙNG một mệnh đề (ranh giới dấu câu/phẩy/· /;), không để lố sang câu kế có "Mục khác"/tên đơn vị khác.
    CLAUSE = re.compile(r"[,.;·|•\n]+")   # giữ ':' lại (vd "VNPT TTP: mục 9 chưa thực hiện" – tên đơn vị + ':' + trạng thái là một mệnh đề)
    for seg in CLAUSE.split(text):
        ms = list(re.finditer(r"\bmục\s*(\d{1,2})\b", seg, re.I))
        if len(ms) != 1: continue   # mệnh đề nhắc >1 mục thì không rõ "chưa bắt đầu" nói về mục nào, bỏ qua
        it = ms[0].group(1)
        if any(re.search(rf"(?<![\w]){re.escape(u)}(?![\wÀ-ỹ])", seg.lower()) for u in t.names): continue   # có tên đơn vị riêng trong mệnh đề (trước hoặc sau): là claim theo đơn vị, để S2 xử lý
        tail = seg[ms[0].end():]
        if not NOT_STARTED.search(tail): continue
        rows = t.by_item.get(it, [])
        started = [x for x in rows if x["st"] != "chua"]
        if rows and started:
            errs.append(f"{where}: «Mục {it} … chưa bắt đầu/chưa thực hiện» nhưng nguồn có {len(started)}/{len(rows)} dòng đã/đang làm: " +
                        ", ".join(f"{x['stt']} ({x['status']})" for x in started[:3]))


def check_status_rows(t, rep, errs):
    """S1: status_table: nhãn 'Hoàn thành' cho mục còn dòng chưa xong."""
    for i, s in enumerate(rep.get("slides", []), 1):
        for row in s.get("rows") or []:
            for b in row.get("blocks", []):
                for blk in (b.get("blocks", []) if b.get("type") == "stack" else [b]):
                    if blk.get("type") != "status_table": continue
                    for r in blk.get("rows", []):
                        stt = str(r.get("status", "")); txt = f"{r.get('item', '')} {r.get('desc', '')}"
                        items = set(re.findall(r"(?:\bmục\s*|\bM)(\d{1,2})(?![\d/])", txt, re.I)) | {x for g in re.findall(r"\bmục\s*((?:\d{1,2}\s*[,–\-và]+\s*)+\d{1,2})(?![\d/])", txt, re.I) for x in re.findall(r"\d{1,2}", g)}
                        # S7: "xong a/b đầu việc" cho (các) mục phải khớp số dòng thật của (các) mục đó
                        for cm in re.finditer(r"(\d+)\s*/\s*(\d+)\s*(?:đầu việc|dòng|việc)", txt, re.I):
                            rows_ = [x for it in items for x in t.by_item.get(it, [])]
                            if any(re.search(r"đầu việc", f"{x.get('task', '')} {x.get('result', '')}", re.I) for x in rows_) or \
                               any(re.search(r"đầu việc", f"{x.get('task', '')} {x.get('result', '')}", re.I) for x in t.rows if x["stt"].split(".")[0] in items):
                                continue   # nguồn tự định nghĩa "đầu việc" (vd checklist 7+9+8 việc), không phải số dòng của bảng
                            if items and rows_ and int(cm.group(2)) != len(rows_):
                                errs.append(f"slide {i}: «{cm.group(0)}» cho Mục {', '.join(sorted(items))} nhưng (các) mục này có {len(rows_)} dòng"
                                            f" (xong {sum(x['st'] == 'xong' for x in rows_)})")
                        # S8: nhãn "Chưa bắt đầu" cho mục thì mọi dòng của mục phải chưa bắt đầu
                        if NOT_STARTED.search(stt) and not re.search(r"(?:mục|\bm)\s*\d|\d\.[a-z]|một phần|:|\(|có (đầu việc|dòng|đơn vị)|một số|chậm", stt, re.I):
                            for it in items:
                                rows_ = t.by_item.get(it, [])
                                # A named organization restricts the claim to its rows.
                                named = [u for u in t.names if any(re.search(rf"(?<![\w]){re.escape(alias)}(?![\w])", stt.lower()) for alias in (u, re.sub(r"^vnpt\s+", "", u)) if len(alias) >= 4)]
                                if named: rows_ = [x for x in rows_ if key(x.get('unit')) in named]
                                started = [x for x in rows_ if x["st"] != "chua"]
                                if rows_ and started:
                                    errs.append(f"slide {i}: nhãn «{stt}» cho Mục {it} nhưng nguồn có {len(started)}/{len(rows_)} dòng đã/đang làm: " +
                                                ", ".join(f"{x['stt']} ({x['status']})" for x in started[:3]))
                        if not DONE_WORD.search(stt) or NOT_DONE_NEAR.search(stt) or re.search(r"(?:mục|\bm)\s*\d", stt, re.I): continue
                        rng = re.search(r"mục\s*(\d{1,2})\s*[,–\-và]+\s*(\d{1,2})", txt, re.I)
                        for it in items:
                            rows = t.by_item.get(it, [])
                            left = [x for x in rows if x["st"] != "xong"]
                            if rows and left:
                                errs.append(f"slide {i}: nhãn «{stt}» cho Mục {it} nhưng nguồn còn {len(left)}/{len(rows)} dòng chưa xong: " +
                                            ", ".join(f"{x['stt']} ({x['status']})" for x in left[:3]))


NUMW = {"một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5, "sáu": 6, "bảy": 7, "tám": 8, "chín": 9, "mười": 10}
STOPK = set("của và các những đã đang được cho theo với trong tại rà soát thực hiện triển khai việc mục nhóm".split())


def kw(t): return {w for w in re.findall(r"[a-zà-ỹđ]+", t.lower()) if len(w) > 2 and w not in STOPK}


def check_done_claims(t, text, where, errs):
    """S6: câu nói 'N nhóm/mục đã xong' hoặc '(Đã) hoàn thành <việc>' trái với bảng theo dõi."""
    done_items = [it for it, rs in t.by_item.items() if rs and all(r["st"] == "xong" for r in rs)]
    for m in re.finditer(r"(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(nhóm|mục|hạng mục)(?:\s+việc)?\s+(?:đã\s+)?(xong|hoàn thành)", text, re.I):
        n = int(m.group(1)) if m.group(1).isdigit() else NUMW[m.group(1).lower()]
        if n > len(done_items):
            errs.append(f"{where}: «{m.group(0)}» nhưng bảng theo dõi chỉ có {len(done_items)} mục xong hết mọi dòng" +
                        (f" (mục {', '.join(done_items)})" if done_items else ""))


def check_semantics(rep, rows, texts_of_slide):
    t = Table(rows)
    errs = []
    if not t.rows: return errs
    check_status_rows(t, rep, errs)
    for i, s in enumerate(rep.get("slides", []), 1):
        for text in texts_of_slide(s):
            check_text(t, text, f"slide {i}", errs)
            check_done_claims(t, text, f"slide {i}", errs)
    seen = set(); out = []
    for e in errs:
        if e not in seen: seen.add(e); out.append(e)
    return out
