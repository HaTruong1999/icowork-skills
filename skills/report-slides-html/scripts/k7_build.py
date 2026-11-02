"""Cầu nối giữa report.py (trích nguồn + kiểm chứng số liệu) và bộ slide K7 (giao diện khoá sẵn).

Mỗi giao diện là một thư mục đủ bộ trong k7/ (Tao-slide.html, cong-cu/, khung/), giữ nguyên bản gốc
của nhóm thiết kế. Skill report-slides-html mang k7/chung/ (không logo VNPT AI, chân trang "iView");
skill report-slides-html-vnptai mang k7/vnpt-ai/ (logo VNPT AI). Cả hai có nút sửa logo trong trang.
Phần duy nhất skill thêm vào mỗi Tao-slide.html là hook data-k7-check cuối tệp, để headless Chrome đọc
được kết quả K7.kiem() (vốn chỉ gọi tay qua console). Không đổi logic kiểm, không đổi giao diện.

Giao diện chọn bằng khoá "theme" ở gốc report.json (driver ghi theo `start --giao-dien`). Khoá này
bị bỏ ra trước khi kiểm/dựng để khung không thấy trường lạ.
"""
import json
import re
import runpy
from pathlib import Path

K7_ROOT = Path(__file__).resolve().parent.parent / "k7"
# Mỗi skill chỉ mang giao diện của mình (report-slides-html: chung; report-slides-html-vnptai: vnpt-ai).
# Code giống hệt nhau giữa hai skill; giao diện mặc định là thư mục có mặt trong k7/.
THEMES = tuple(sorted(d.name for d in K7_ROOT.iterdir() if (d / "Tao-slide.html").is_file()))
DEFAULT_THEME = "chung" if "chung" in THEMES else THEMES[0]
_kiem_modules = {}


def theme_of(deck):
    theme = (deck or {}).get("theme") or DEFAULT_THEME
    if theme not in THEMES:
        raise ValueError(f'Giao diện "{theme}" không có; chọn một trong {", ".join(THEMES)}')
    return theme


def theme_dir(theme):
    return K7_ROOT / theme


def _deck_only(deck):
    return {k: v for k, v in deck.items() if k != "theme"}


def _kiem(theme):
    if theme not in _kiem_modules:
        _kiem_modules[theme] = runpy.run_path(str(theme_dir(theme) / "cong-cu" / "kiem-slide.py"), run_name="k7_kiem_slide")
    return _kiem_modules[theme]["kiem"]


SOFT_OVER = 1.12   # vượt giới hạn ký tự tới 12% chỉ là nhắc: tràn thật do M7 (đo bằng trình duyệt) quyết định


def soften(issues, tolerance=SOFT_OVER):
    """Hạ lỗi M2 "Dài n/g" vượt nhẹ xuống nhắc. Bắt agent đếm ký tự tiếng Việt để bớt 1–2 ký tự là cách nhanh nhất làm model
    suy nghĩ lặp tới hết hạn mức; layout thật được M7 kiểm sau khi dựng, nên giới hạn ký tự ở đây chỉ là ước lượng."""
    out = []
    for x in issues:
        m = x.get("ma") == "M2" and x.get("muc") == "loi" and re.search(r"Dài (\d+)/(\d+)", str(x.get("y", "")))
        if m and int(m.group(1)) <= int(int(m.group(2)) * tolerance + 0.999):
            x = {**x, "muc": "nhac", "y": x["y"] + " (vượt nhẹ, chấp nhận nếu không tràn khi hiển thị)"}
        out.append(x)
    return out


def kiem_k7(deck):
    """Chạy nguyên kiem-slide.py của giao diện đã chọn (C1-C3, M1-M10). Không kiểm số liệu với nguồn - đó là việc của report.py."""
    return soften(_kiem(theme_of(deck))(_deck_only(deck)))


def _an_toan(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace("</", "<\\/").replace("<!--", "<\\!--")


def render_k7(deck):
    """Y hệt cong-cu/dung-slide.py: thay khối <script id="deck"> trong khung đã khoá, không tự vẽ HTML."""
    khung = (theme_dir(theme_of(deck)) / "Tao-slide.html").read_text(encoding="utf-8")
    data = _deck_only(deck)
    html = re.sub(r'(<script type="application/json" id="deck">)[\s\S]*?(</script>)',
                  lambda m: m.group(1) + _an_toan(data) + m.group(2), khung, count=1)
    ten = (data.get("meta") or {}).get("ten")
    ten = ten.get("vi") if isinstance(ten, dict) else ten
    html = re.sub(r"<title>.*?</title>", lambda m: "<title>" + str(ten or "Slide").replace("<", "") + "</title>", html, count=1)
    return html


def check_overflow_k7(browser, html_path):
    check_overflow_k7.empty = []
    """Đọc data-k7-check do hook ghi, lọc đúng mã M7 (tràn khung).
    Trả về (danh sách tràn, lỗi hoặc None). Không tự thu nhỏ chữ: khung khoá sẵn, tràn thì phải viết ngắn lại."""
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
    # Khung dựng slide bằng JS: một slide sai kiểu dữ liệu làm JS dừng, slide đó và mọi slide sau để trống (PDF trắng).
    check_overflow_k7.empty = [int(n) for n in re.findall(
        r'<section[^>]*id="slide-(\d+)"(?:(?!</section>).)*?<div class="khung"></div>', r.stdout, re.S)]
    return overflow, None
