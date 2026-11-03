#!/usr/bin/env python3
"""Lối tắt cho lệnh gõ nhầm. Launcher thật nằm trong thư mục làm việc (report-output/advance.py), nhưng model đôi khi gõ nhầm thành
<skill>/advance.py. Tệp không tồn tại trong thư mục skill bị iWork coi là "ngoài thư mục làm việc" và hỏi quyền, nên tạo sẵn tệp này:
tìm thư mục báo cáo ở thư mục hiện tại rồi chạy đúng `iwork.py advance`."""
import runpy
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
cwd = Path.cwd()
candidates = [cwd / 'report-output', cwd, *sorted(cwd.glob('report-output*')), *sorted(cwd.glob('*/report-output'))]
work = next((c for c in candidates if (c / 'iwork-state.json').is_file()), None)
if work is None:
    raise SystemExit('Chưa có báo cáo ở thư mục này: chạy lệnh start trước, rồi dùng lệnh mà start in ra.')
driver = str(here / 'iwork.py')
sys.argv = [driver, 'advance', str(work)]
runpy.run_path(driver, run_name='__main__')
