#!/usr/bin/env python3
"""report.json (K7, 12 mẫu) -> Word (.docx) kiểu đơn giản: đủ chữ, không trang trí.

Mỗi slide là một mục (Heading 1). Nội dung riêng của từng mẫu thành đoạn văn, gạch đầu dòng
hoặc bảng lưới mặc định. Chữ song ngữ {"vi","en"} lấy theo ngôn ngữ chọn (mặc định vi).
Cụm nhấn mạnh *...* thành chữ đậm. Cần python-docx.
Thường được gọi qua `report.py docx`. Dùng riêng:
  python3 to_docx.py <report.json> <out.docx> [vi|en]
"""
import json
import re
import sys
from pathlib import Path


def txt(value, lang="vi"):
    """Chữ của một ô K7: chuỗi thường hoặc {"vi": ..., "en": ...}."""
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("vi") or value.get("en") or "")
    return "" if value is None else str(value)


def add_runs(par, text):
    """Thêm chữ vào đoạn; *...* (cú pháp nhấn mạnh K7) thành chữ đậm."""
    for k, piece in enumerate(re.split(r"\*(.+?)\*", text)):
        if piece:
            par.add_run(piece).bold = (k % 2 == 1)
    return par


def plain(text):
    return text.replace("*", "")


class Writer:
    def __init__(self, doc, lang):
        self.doc, self.lang = doc, lang

    def t(self, value):
        return txt(value, self.lang)

    def para(self, value, style=None, prefix=""):
        text = self.t(value)
        if text:
            add_runs(self.doc.add_paragraph(style=style), prefix + text)

    def bullet(self, value, prefix=""):
        self.para(value, "List Bullet", prefix)

    def heading(self, value, level):
        text = plain(self.t(value))
        if text:
            self.doc.add_heading(text, level=level)

    def table(self, header, rows):
        header = [self.t(h) for h in header]
        rows = [[self.t(c) for c in r] for r in rows]
        cols = max([len(header)] + [len(r) for r in rows] or [1])
        table = self.doc.add_table(rows=0, cols=cols)
        table.style = "Table Grid"
        for k, row in enumerate(([header] if any(header) else []) + rows):
            cells = table.add_row().cells
            for c in range(cols):
                value = row[c] if c < len(row) else ""
                add_runs(cells[c].paragraphs[0], f"*{plain(value)}*" if k == 0 and any(header) and value else value)
        self.doc.add_paragraph()

    def label_items(self, items, title_key, desc_key, extra=None):
        for item in items or []:
            title, desc = self.t(item.get(title_key)), self.t(item.get(desc_key))
            more = self.t(item.get(extra)) if extra else ""
            head = " · ".join(x for x in (more, title) if x)
            self.bullet(f"*{plain(head)}*" + (f": {desc}" if desc else "") if head else desc)


def slide_body(w, s):
    mau = s.get("mau")
    if mau == "muc-luc":
        for item in s.get("muc") or []:
            w.bullet(w.t(item.get("t")) + (f": {w.t(item.get('d'))}" if item.get("d") else ""))
    elif mau in ("so-lieu", "hinh-so"):
        for item in s.get("so") or []:
            w.bullet(f"*{plain(w.t(item.get('so')))}* {w.t(item.get('nhan'))}")
    elif mau == "van-de":
        for key, label in (("vanDe", "Vấn đề"), ("giaiPhap", "Giải pháp")):
            part = s.get(key) or {}
            w.para(f"*{label}: {plain(w.t(part.get('t')))}*")
            for line in part.get("y") or []:
                w.bullet(line)
            if part.get("so"):
                w.bullet(f"*{plain(w.t(part.get('so')))}* {w.t(part.get('soNhan'))}")
    elif mau == "the":
        w.label_items(s.get("the"), "t", "d")
    elif mau == "bang":
        w.table(s.get("cot") or [], s.get("hang") or [])
    elif mau == "lop":
        for item in s.get("lop") or []:
            w.bullet(" · ".join(x for x in (w.t(item.get("ma")), w.t(item.get("t"))) if x))
        w.para(s.get("quanTri"), prefix="Quản trị: ")
        note = s.get("ghiChu") or {}
        w.para(note.get("t"))
        for line in note.get("y") or []:
            w.bullet(line)
    elif mau == "anh":
        w.para((s.get("anh") or {}).get("alt"), prefix="Ảnh: ")
        w.label_items(s.get("chuGiai"), "t", "d")
    elif mau == "lo-trinh":
        w.label_items(s.get("buoc"), "t", "d", extra="tg")
    elif mau == "cam-on":
        for item in s.get("lienHe") or []:
            w.bullet(f"{w.t(item.get('nhan'))}: {w.t(item.get('gt'))}")
    if mau == "hinh-so":
        w.para((s.get("anh") or {}).get("alt"), prefix="Hình: ")


def build_docx(rep, out_path, lang="vi"):
    import docx
    doc = docx.Document()
    w = Writer(doc, lang)
    meta = rep.get("meta", {})
    title = plain(txt(meta.get("ten") or meta.get("title"), lang))
    doc.core_properties.title = title
    doc.core_properties.author = str(meta.get("author") or "")
    for s in rep.get("slides", []):
        mau = s.get("mau")
        if mau == "bia":
            w.para(s.get("the"))
            doc.add_heading(plain(w.t(s.get("tieuDe"))) or title, 0)
            w.para(s.get("phu"))
            w.para(s.get("dong"))
            w.para(s.get("doiTac"), prefix="Đối tác: ")
            continue
        if mau == "chuong":
            w.heading(f"{w.t(s.get('so'))}. {w.t(s.get('tieuDe'))}".lstrip(". "), 1)
            w.para(s.get("phu"))
            continue
        head = w.t(s.get("dauMuc"))
        if head:
            w.para(head)
        number = w.t(s.get("soMuc"))
        w.heading((number + ". " if number else "") + w.t(s.get("tieuDe")), 1 if mau != "cam-on" else 2)
        w.para(s.get("phu"))
        slide_body(w, s)
        w.para(s.get("ketLuan"), prefix="*Kết luận:* ")
        w.para(s.get("nguon"))
        if s.get("loiThoai"):
            note = doc.add_paragraph()
            note.add_run("Lời thoại: " + plain(w.t(s.get("loiThoai")))).italic = True
    pending = meta.get("canXacNhan") or []
    if pending:
        doc.add_heading("Điểm cần xác nhận", 1)
        for item in pending:
            w.bullet(item)
    doc.save(out_path)
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    rep = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print("Word:", build_docx(rep, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "vi"))
