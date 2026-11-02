#!/usr/bin/env python3
"""Sự thật tính sẵn cho MỌI tài liệu (không chỉ bảng theo dõi). Gọi từ `report.py extract`.

Ghi WORK/facts.md:
  - Nếu file là bảng theo dõi tiến độ (có cột STT…): dùng tracker.py (đếm hoàn thành, quá hạn, cộng phân số…).
  - Mọi tài liệu: phân số X/Y kèm %, các mốc thời gian (đã qua / sắp tới so với ngày báo cáo), số tiền,
    tổng các cột số trong bảng của tài liệu. Mỗi số tự tính kèm dòng `computed` để chép vào meta.computed.
"""
import datetime as dt, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

def vn(x, d=1):
    if abs(x - round(x)) < 1e-9: return f"{int(round(x)):,}".replace(",", ".")
    return f"{x:.{d}f}".replace(".", ",")

def num(s): return float(s.replace(".", "").replace(",", "."))

FRAC = re.compile(r"(?<![\d/.,QqTt])(\d{1,3}(?:\.\d{3})+|\d+)\s*/\s*(\d{1,3}(?:\.\d{3})+|\d+)(?![\d/])(\s*[A-Za-zÀ-ỹđĐ]+(?:\s+[A-Za-zÀ-ỹđĐ]+)?)?")
DATE = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})/(20\d\d)(?![\d/])")
MONEY = re.compile(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*(tỷ|triệu|nghìn tỷ)\s*(đồng|VNĐ|VND|đ)\b", re.I)
SEC = re.compile(r"^## (Trang|Slide|Toàn văn|Mục)\s*(\d*)", re.M)

def sections(content):
    """[(nhãn vị trí, đoạn chữ)] theo '## Trang n' / '## Slide n'."""
    out, last, lab = [], 0, "đầu tài liệu"
    for m in SEC.finditer(content):
        out.append((lab, content[last:m.start()])); lab = f"{m.group(1).lower()} {m.group(2)}".strip(); last = m.end()
    out.append((lab, content[last:]))
    return [(l, t) for l, t in out if t.strip()]

def generic_facts(content, today):
    F = []
    add = lambda kind, text, value="", formula="": F.append(dict(kind=kind, text=text, value=value, formula=formula))
    for where, t in sections(content):
        flat = re.sub(r"\s+", " ", t)
        for m in FRAC.finditer(flat):
            a, b = num(m.group(1)), num(m.group(2))
            if not b or a > b or b in (2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030) or (b <= 12 and a <= 31 and not m.group(3)): continue
            ctx = flat[max(0, m.start() - 50):m.end() + 10].strip()
            add("ti-le", f"{where}: {m.group(1)}/{m.group(2)}{(m.group(3) or '').rstrip()} = {vn(100 * a / b)}%  («…{ctx}…»)",
                f"{vn(100 * a / b)}%", f"{m.group(1)} / {m.group(2)} = {vn(100 * a / b)}%")
        for m in DATE.finditer(flat):
            try: d = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError: continue
            ctx = flat[max(0, m.start() - 70):m.end() + 5].strip()
            if re.search(r"(trước|hạn|chậm nhất|đến ngày|hoàn thành|dự kiến|kế hoạch)\W{0,3}[^.]{0,25}$", flat[max(0, m.start() - 40):m.start()], re.I):
                rel = "ĐÃ QUA" if d < today else "sắp tới"
                add("moc", f"{where}: mốc {m.group(0)} ({rel} so với {today.strftime('%d/%m/%Y')}) «…{ctx}…»", m.group(0))
        for m in MONEY.finditer(flat):
            ctx = flat[max(0, m.start() - 60):m.end()].strip()
            add("tien", f"{where}: {m.group(0)} «…{ctx}…»", m.group(0))
    # bảng trong content.md: dòng có ' | ' -> cộng cột số
    for where, t in sections(content):
        rows = [[c.strip() for c in l.split("|")] for l in t.splitlines() if l.count("|") >= 2]
        if len(rows) < 4: continue
        ncol = max(len(r) for r in rows)
        for c in range(ncol):
            col = [r[c] if c < len(r) else "" for r in rows]
            vals = []
            for v in col[1:]:
                if re.fullmatch(r"\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:,\d+)?", v): vals.append(v)
            if len(vals) >= 3 and len(vals) >= 0.6 * (len(col) - 1):
                xs = [num(v) for v in vals]
                if xs == [float(i) for i in range(1, len(xs) + 1)]: continue
                add("tong-cot", f"{where}: bảng, cột «{col[0][:40]}»: {' + '.join(vals)} = {vn(sum(xs))}", vn(sum(xs)), f"{' + '.join(vals)} = {vn(sum(xs))}")
    return F

def main():
    work, today_s, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    d, m, y = map(int, today_s.split("/")); today = dt.date(y, m, d)
    content = open(os.path.join(work, "content.md"), encoding="utf8").read()
    lines = [f"# Sự thật tính sẵn (ngày báo cáo {today_s}) – do script tính. CHÉP NGUYÊN số và dòng computed; muốn số khác thì dùng `report.py calc`.", ""]
    tracker_used = False
    for f in files:
        if f.lower().endswith((".pdf", ".xlsx", ".csv", ".docx")):
            tw = os.path.join(work, "tracker", re.sub(r"[^0-9A-Za-z_.-]+", "_", os.path.basename(f))[:40])
            r = subprocess.run([sys.executable, os.path.join(HERE, "tracker.py"), f, tw, "--date", today_s], capture_output=True, text=True)
            if r.returncode != 0 and "KHÔNG PHẢI BẢNG THEO DÕI" not in (r.stdout + r.stderr):
                raise SystemExit(f"LỖI đọc bảng {os.path.basename(f)}: {r.stderr or r.stdout}")
            if r.returncode == 0 and os.path.exists(os.path.join(tw, "facts.md")):
                tracker_used = True
                lines += [f"## BẢNG THEO DÕI: {os.path.basename(f)}", open(os.path.join(tw, "facts.md"), encoding="utf8").read().split("\n", 2)[-1], ""]
    G = generic_facts(content, today)
    lines.append("## Số liệu trong toàn bộ nguồn")
    for i, f in enumerate(G, 1):
        lines.append(f"- G{i} [{f['kind']}] {f['text']}" + (f"  → computed: {{\"value\": \"{f['value']}\", \"formula\": \"{f['formula']}\"}}" if f["formula"] else ""))
    open(os.path.join(work, "facts.md"), "w", encoding="utf8").write("\n".join(lines) + "\n")
    print(f"facts.md: {'có bảng theo dõi; ' if tracker_used else ''}{len(G)} số liệu chung")

if __name__ == "__main__":
    main()
