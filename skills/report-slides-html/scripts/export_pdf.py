#!/usr/bin/env python3
"""HTML -> PDF bằng Chrome/Edge/Chromium headless, kèm kiểm tra tràn chữ và ảnh xem trước.

Không cần cài thư viện Python nào: chỉ cần một trình duyệt nhân Chromium trên máy.
Thường được gọi qua `report.py build`. Dùng riêng:
  python3 export_pdf.py <file.html> [<file.pdf>]
"""
import glob
import html as htmlmod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
    "microsoft-edge", "microsoft-edge-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser():
    env = os.environ.get("REPORT_BROWSER")
    if env and os.path.exists(env):
        return env
    for c in CANDIDATES:
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p:
            return p
    # Chromium do Playwright tải về (nếu có)
    for pat in ["~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
                "~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                "~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome",
                "~/AppData/Local/ms-playwright/chromium-*/chrome-win*/chrome.exe"]:
        hits = sorted(glob.glob(os.path.expanduser(pat)))
        if hits:
            return hits[-1]
    return None


def _run(browser, args, timeout=180):
    with tempfile.TemporaryDirectory(prefix="rsh-chrome-") as prof:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               "--hide-scrollbars", "--disable-extensions", f"--user-data-dir={prof}"] + args
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              encoding="utf-8", errors="replace")


def check_overflow(browser, html_path):
    """Trả về (danh sách tràn, danh sách tự thu nhỏ, lỗi).
    Tràn: {"slide": n, "parts": [...]}; tự thu nhỏ: {"slide": n, "scale": 92} (% cỡ chữ vùng nội dung)."""
    r = _run(browser, ["--window-size=1400,900", "--virtual-time-budget=8000", "--dump-dom",
                       Path(html_path).resolve().as_uri()])
    tag = re.search(r"<html[^>]*>", r.stdout)
    m = tag and re.search(r'\sdata-overflow="([^"]*)"', tag.group(0))
    if not m:
        return None, None, "Không đọc được kết quả kiểm tra tràn chữ (trình duyệt không chạy script?)."
    f = re.search(r'\sdata-fit="([^"]*)"', tag.group(0))
    fit = json.loads(htmlmod.unescape(f.group(1)) or "[]") if f else []
    sp = re.search(r'\sdata-sparse="([^"]*)"', tag.group(0))
    check_overflow.sparse = json.loads(htmlmod.unescape(sp.group(1)) or "[]") if sp else []
    return json.loads(htmlmod.unescape(m.group(1)) or "[]"), fit, None


def print_pdf(browser, html_path, pdf_path):
    pdf_path = Path(pdf_path).resolve()
    if pdf_path.exists():
        pdf_path.unlink()
    r = _run(browser, ["--no-pdf-header-footer", "--print-to-pdf-no-header", "--virtual-time-budget=8000",
                       "--run-all-compositor-stages-before-draw", f"--print-to-pdf={pdf_path}",
                       Path(html_path).resolve().as_uri()])
    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        return f"In PDF thất bại: {r.stderr[-400:]}"
    return None


def pdf_pages(pdf_path):
    try:
        import fitz
        return fitz.open(pdf_path).page_count
    except Exception:
        pass
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        return int(m.group(1)) if m else None
    return None


def previews(pdf_path, out_dir, dpi=60):
    """Ảnh PNG từng trang PDF (để agent tự xem lại). Dùng render_pdf của extract.py."""
    sys.path.insert(0, str(Path(__file__).parent))
    from extract import render_pdf, contact_sheets
    out_dir = Path(out_dir)
    shutil.rmtree(out_dir, ignore_errors=True)
    files = render_pdf(Path(pdf_path), out_dir, dpi)
    sheets = contact_sheets(files, out_dir / "sheets") if files else []
    return files, sheets


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    b = find_browser()
    if not b:
        raise SystemExit("Không tìm thấy Chrome/Edge/Chromium. Cài Chrome hoặc đặt biến REPORT_BROWSER=<đường dẫn>.")
    ov, fit, e = check_overflow(b, src)
    print("Tràn chữ:", e or (ov or "không"), "| tự thu nhỏ:", fit or "không")
    e = print_pdf(b, src, dst)
    print(e or f"PDF: {dst} ({pdf_pages(dst)} trang)")
