#!/usr/bin/env python3
"""Lối tắt cho lệnh gõ nhầm. Launcher thật nằm trong thư mục làm việc (review-output/next.py), nhưng model đôi khi ghép nhầm đường dẫn
thành <skill>/scripts/next.py. Tệp không tồn tại trong thư mục skill bị iWork coi là "ngoài thư mục làm việc" và hỏi quyền, nên tạo sẵn
tệp này: tìm phiên review ở thư mục hiện tại rồi chạy đúng `iwork.py next`."""
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
cwd = Path.cwd()
candidates = [cwd / 'review-output', cwd, *sorted(cwd.glob('*/review-output'))]
work = next((c for c in candidates if (c / 'session.json').is_file()), None)
if work is None:
    raise SystemExit('Chưa có phiên review ở thư mục này: chạy lệnh init trước, rồi dùng lệnh next_command mà init in ra.')
driver = str(here / 'iwork.py')
sys.argv = [driver, 'next', '--work', str(work)]
runpy.run_path(driver, run_name='__main__')
