"""Cầu nối giữa report.py (trích nguồn + kiểm chứng số liệu) và bộ slide K7
(giao diện khoá sẵn, chưa chốt chính thức - xem k7/DOC-TRUOC.md gốc).

K7 sống nguyên trong thư mục con k7/ (Tao-slide-VNPT-AI.html, cong-cu/, khung/),
không sửa logic bên trong K7 - chỉ gọi vào. Hook data-k7-check trong
k7/Tao-slide-VNPT-AI.html là phần duy nhất report-slides-html-k7 thêm vào bản K7 gốc
(để headless Chrome đọc được kết quả K7.kiem(), vốn chỉ gọi tay qua console).
"""
import json
import re
import runpy
from pathlib import Path

K7 = Path(__file__).resolve().parent.parent / "k7"
TEMPLATE = K7 / "Tao-slide-VNPT-AI.html"
_kiem_module = None


def _kiem():
    global _kiem_module
    if _kiem_module is None:
        _kiem_module = runpy.run_path(str(K7 / "cong-cu" / "kiem-slide.py"), run_name="k7_kiem_slide")
    return _kiem_module["kiem"]


def kiem_k7(deck):
    """Chạy nguyên kiem-slide.py của K7 (M1-M10, cấu trúc + định dạng). Không kiểm số liệu với nguồn - đó là việc của report.py."""
    return _kiem()(deck)


def _an_toan(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("</", "<\\/").replace("<!--", "<\\!--")


def render_k7(deck):
    """Y hệt cong-cu/dung-slide.py: thay khối <script id="deck"> trong khung đã khoá, không tự vẽ HTML."""
    khung = TEMPLATE.read_text(encoding="utf-8")
    html = re.sub(r'(<script type="application/json" id="deck">)[\s\S]*?(</script>)',
                  lambda m: m.group(1) + _an_toan(deck) + m.group(2), khung, count=1)
    ten = (deck.get("meta") or {}).get("ten")
    ten = ten.get("vi") if isinstance(ten, dict) else ten
    html = re.sub(r"<title>.*?</title>", "<title>" + str(ten or "Slide VNPT AI").replace("<", "") + "</title>", html, count=1)
    return html


def check_overflow_k7(browser, html_path):
    """Đọc data-k7-check do hook riêng ghi (xem k7/Tao-slide-VNPT-AI.html, cuối tệp), lọc đúng mã M7 (tràn khung).
    Trả về (danh sách tràn ['slide N: ...'], lỗi hoặc None) - không có bước tự thu nhỏ chữ như report-slides-html
    gốc, vì K7 là giao diện khoá sẵn, không được sửa CSS/kích thước theo slide."""
    from export_pdf import _run
    r = _run(browser, ["--window-size=1400,900", "--virtual-time-budget=8000", "--dump-dom",
                       Path(html_path).resolve().as_uri()])
    tag = re.search(r"<html[^>]*>", r.stdout)
    import html as htmlmod
    m = tag and re.search(r'\sdata-k7-check="([^"]*)"', tag.group(0))
    if not m:
        err = tag and re.search(r'\sdata-k7-check-error="([^"]*)"', tag.group(0))
        if err:
            return [], htmlmod.unescape(err.group(1))
        return [], "Không đọc được kết quả kiểm tra tràn chữ (hook data-k7-check không chạy)."
    ds = json.loads(htmlmod.unescape(m.group(1)) or "[]")
    overflow = [x for x in ds if x.get("ma") == "M7"]
    return overflow, None
