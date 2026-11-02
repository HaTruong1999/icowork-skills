#!/usr/bin/env python3
"""Stable iWork entry point. Durable slide parts; exact quoted NEXT commands."""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from source_audit import check_audit, task as quality_task, sha, identity_errors, auto_audit, number_evidence
from k7_build import THEMES, DEFAULT_THEME, soften
# GUI apps on macOS often inherit a minimal PATH. Only add existing standard bins.
for directory in ('/opt/homebrew/bin', '/usr/local/bin'):
    if Path(directory).is_dir() and directory not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + directory
ENGINE = ROOT / 'scripts' / 'report.py'
IVIEW_NOTICE = 'GỢI Ý: File HTML có thể được chia sẻ bằng link thông qua iView trên Go Connect.'
# Một lần build đầu + 3 vòng sửa. Đếm số lần build lỗi liên tiếp, đặt lại khi build đạt.
MAX_FAILED_BUILDS = 4

def local(value):
    """Đường dẫn tương đối với cwd nếu nằm trong workspace, để lệnh/đường dẫn không phát sinh hỏi quyền."""
    path = Path(str(value))
    if path.is_absolute():
        try: return path.resolve().relative_to(Path.cwd().resolve())
        except ValueError: pass
    return value

LAUNCHER = '''import os, runpy, sys
# Tệp do driver tạo: chạy lại đúng driver của skill để agent không phải nhớ/gõ đường dẫn skill (dễ gõ sai, và đường dẫn ngoài workspace làm iWork hỏi quyền).
DRIVER = {driver!r}
sys.argv = [DRIVER, 'advance', os.path.dirname(os.path.abspath(__file__))]
runpy.run_path(DRIVER, run_name='__main__')
'''

def write_launcher(work):
    path = Path(work) / 'advance.py'
    text = LAUNCHER.format(driver=str(ROOT / 'iwork.py'))
    if not path.is_file() or path.read_text(encoding='utf-8') != text:
        path.write_text(text, encoding='utf-8')
    return path

def command(*args):
    if args and args[0] in ('resume', 'build', 'advance', 'finish') and len(args) == 2 and Path(str(args[1])).is_dir():
        exe = 'python' if os.name == 'nt' else 'python3'
        return f'{exe} "{local(write_launcher(args[1]))}"'
    if args and args[0] in ('resume', 'build'):
        args = ('advance', *args[1:])
    exe = 'python' if os.name == 'nt' else 'python3'
    quote = lambda value: '"' + str(value).replace('"', '\\"') + '"'
    return ' '.join([exe, quote(ROOT / 'iwork.py'), *[quote(local(x)) for x in args]])

# Tệp/thư mục driver hoặc agent được phép có ở gốc WORK. Mọi thứ khác là file lạ.
ALLOWED = {'content.md', 'facts.md', 'notes.md', 'plan.json', 'parts', 'iwork-state.json', 'job-step.json',
           'STATUS.md', 'TASK.md', 'build.log', 'build-history', 'report.json', 'sources', 'tracker', '_preview',
           'coverage-required.json', 'quality-audit.template.json', 'quality-audit.json', 'delivery.json', 'advance.py',
           '_work', '.build_attempts', 'metadata.json', '.iwork-state.sha256', 'tom-tat.md'}

LOGO_TYPES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp'}

def identity_meta(state):
    """meta.nhanDien từ logo/chân trang người dùng đưa lúc start. Ảnh nhúng thẳng (data URI) để agent không phải đọc base64."""
    nd = {}
    if state.get('logo') and Path(state['logo']).is_file():
        import base64
        path = Path(state['logo'])
        nd.update(kieu='anh', anh=f'data:{LOGO_TYPES[path.suffix.lower()]};base64,' + base64.b64encode(path.read_bytes()).decode(),
                  ten='Logo', tuDoiTrang=True)
    if 'chan_trang' in state:
        nd['chanTrang'] = state['chan_trang']
    return nd

def length_hint(slide, issue):
    """Lỗi M2 (quá dài): kèm chữ hiện tại và số ký tự phải bớt, để agent không phải tự đếm ký tự có dấu."""
    m = re.match(r'slide \d+ · (.+?) · (vi|en)$', str(issue.get('vi_tri', '')))
    n = re.search(r'Dài (\d+)/(\d+)', str(issue.get('y', '')))
    if issue.get('ma') != 'M2' or not m or not n:
        return issue
    value = slide
    for key in m.group(1).split('.'):
        value = value[int(key)] if isinstance(value, list) and key.isdigit() and int(key) < len(value) else (value.get(key) if isinstance(value, dict) else None)
    if isinstance(value, dict):
        value = value.get(m.group(2))
    if not isinstance(value, str):
        return issue
    cut = int(n.group(1)) - int(n.group(2))
    return {**issue, 'hien_tai': value, 'can_bot': f'bớt ít nhất {cut} ký tự (tối đa {n.group(2)}, không tính dấu *); viết lại câu ngắn hơn, không viết tắt khó hiểu'}

def stray_files(work):
    if not work.is_dir():
        return []
    return sorted(p.name for p in work.iterdir()
                  if p.name not in ALLOWED and p.suffix.lower() not in ('.html', '.pdf', '.docx'))

def footer(work):
    """Dòng trạng thái cuối mọi lệnh: agent hay tự dừng vì tưởng đã xong, nên nhắc ngay trong output công cụ."""
    state_path = work / 'iwork-state.json'
    if not state_path.exists():
        return
    state = json.loads(state_path.read_text(encoding='utf-8'))
    if str(state.get('phase', '')).startswith('complete'):
        return
    stray = stray_files(work)
    if stray:
        print('CẢNH BÁO FILE LẠ trong WORK: ' + ', '.join(stray)
              + '. Chỉ ghi notes.md, plan.json, parts/NN.json, quality-audit.json; xoá file thừa hoặc chuyển nội dung vào đúng file.')
    try:
        verify_state(work)
    except SystemExit:
        print('=== DỪNG: tệp trạng thái bị sửa ngoài driver. Báo người dùng; không tự sửa tiếp. ===')
        return
    if state.get('failed_builds', 0) >= MAX_FAILED_BUILDS:
        if ship_draft(work):
            return
        print('=== DỪNG: hết lượt build. Báo người dùng bản nháp, build.log và lỗi còn lại; không tuyên bố hoàn tất. ===')
        return
    nxt = command('finish', work) if state.get('phase') == 'quality' else command('advance', work)
    print(f'=== CHƯA XONG (phase={state.get("phase", "authoring")}). Làm ngay việc ở trên rồi chạy {nxt} '
          'trong cùng lượt. Không trả lời hay hỏi người dùng cho tới khi thấy HOÀN TẤT. ===')
    print('(Chỉ chạy đúng lệnh trên. KHÔNG ls/find/cd/rm/2>/dev/null: iWork sẽ hỏi quyền và dừng chờ. Đọc tệp bằng công cụ read, ghi bằng write, xoá/đổi tên không cần.)')
    print(RESUME_RULE.format(nxt=nxt))

RESUME_RULE = ('QUY TẮC CỨNG: chưa thấy dòng HOÀN TẤT nghĩa là CHƯA XONG. Không tự viết báo cáo/tóm tắt/tệp kết quả (chỉ driver tạo HTML và PDF), không nói "đã hoàn tất". '
               'Nếu mất ngữ cảnh, không chắc đang ở bước nào, hoặc thấy câu "Continue if you have next steps": chạy lại đúng {nxt} để làm tiếp. Không đọc mã nguồn skill (iwork.py, k7_build.py, SKILL.md…) để "tìm hiểu": lệnh đó luôn đúng.')

def ship_draft(work):
    """Hết lượt build mà đã có HTML/PDF: vẫn giao bản mới nhất, đặt tên *_BAN_NHAP và ghi rõ lỗi còn lại,
    để người dùng không phải nhắn thêm mà cũng không nhầm với bản đã qua kiểm."""
    report = work / 'report.json'
    if not report.is_file():
        return False
    rep = load(report); name = rep['meta']['output_name']
    sources = [work / (name + ext) for ext in ('.html', '.pdf')]
    if any(not p.is_file() or p.stat().st_size == 0 for p in sources):
        return False
    outputs = []
    for p in sources:
        target = p.with_name(p.stem + '_BAN_NHAP' + p.suffix)
        shutil.move(str(p), str(target)); outputs.append(target)
    state = load(work / 'iwork-state.json')
    warnings = build_log_errors(work)
    state.update(phase='complete_with_warnings'); write_json(work / 'iwork-state.json', state)
    write_json(work / 'delivery.json', {'state': 'draft-with-warnings', 'slides': len(rep['slides']), 'outputs': [str(local(p)) for p in outputs],
                                        'warnings': warnings, 'uncertainties': ['Bản nháp: còn lỗi kiểm chưa sửa hết (xem warnings); cần người xem lại trước khi dùng.']})
    (work / 'STATUS.md').write_text('# HOÀN TẤT (BẢN NHÁP CÓ CẢNH BÁO)\n' + str(work / 'delivery.json') + '\n')
    tidy_workspace(work, {p.name for p in outputs} | {'iwork-state.json', 'delivery.json'})
    print('HOÀN TẤT (BẢN NHÁP CÓ CẢNH BÁO): ' + str(local(work / 'delivery.json')))
    print('TỆP: ' + ' · '.join(str(local(p)) for p in outputs))
    print('Hết lượt tự sửa nên driver giao bản mới nhất, đặt tên *_BAN_NHAP. Báo người dùng ĐÂY LÀ BẢN NHÁP chưa qua kiểm, kèm các lỗi còn lại:')
    for w in warnings[:12]:
        print('  - ' + w)
    return True

def run(*args):
    result = subprocess.run([sys.executable, str(ENGINE), *map(str, args)], capture_output=True, text=True)
    if result.stdout: print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('NEXT:')), end='\n')
    if result.stderr: print(result.stderr, end='', file=sys.stderr)
    if result.returncode: raise SystemExit(result.returncode)

def write_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)
    if path.name == 'iwork-state.json':
        # Dấu kiểm của chính driver: agent sửa tay state (vd đặt lại bộ đếm build) sẽ bị phát hiện.
        (path.parent / '.iwork-state.sha256').write_text(sha(path) + '\n', encoding='utf-8')

def verify_state(work):
    state, mark = work / 'iwork-state.json', work / '.iwork-state.sha256'
    if state.exists() and mark.exists() and mark.read_text(encoding='utf-8').strip() != sha(state):
        raise SystemExit('DỪNG: iwork-state.json đã bị sửa ngoài driver (vd đặt lại bộ đếm build). '
                         'Không sửa tay tệp trạng thái; báo người dùng tình trạng hiện tại và lỗi còn lại.')

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError) as error: raise SystemExit(f'LỖI {path}: {error}')

def fact_computations(work):
    """Reuse only computations actually emitted by the source extraction tools."""
    result = []
    decoder = json.JSONDecoder()
    for line in (work / 'facts.md').read_text(encoding='utf-8').splitlines():
        if '→ computed: ' not in line: continue
        obj, _ = decoder.raw_decode(line.split('→ computed: ', 1)[1])
        if obj not in result: result.append(obj)
        # Group totals expose a fraction as value and a percentage in prose.
        fraction = re.fullmatch(r'([\d.]+)\s*/\s*([\d.]+)', str(obj.get('value', '')))
        ratio = re.search(r'\(([\d,]+%)\)', line)
        if fraction and ratio:
            result.append({'value': ratio[1], 'formula': f'{fraction[1]} / {fraction[2]} = {ratio[1]}'})
    return result

def workpath(value):
    """Chuẩn hoá thư mục WORK. Agent hay thêm tên thư mục phiên làm tiền tố (vd 261030-0943-j0303x/report-output)
    nên sinh thư mục lồng nhau; bỏ tiền tố đó nếu thư mục lồng chưa tồn tại."""
    cwd = Path.cwd().resolve()
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = cwd / path
    path = Path(os.path.normpath(path))
    if path.name == '_work' and (path.parent / 'iwork-state.json').is_file() and not (path / 'iwork-state.json').is_file():
        path = path.parent    # launcher nằm trong _work sau khi HOÀN TẤT; trạng thái ở thư mục cha
    try:
        parts = path.relative_to(cwd).parts
        if len(parts) > 1 and parts[0] == cwd.name and not (cwd / parts[0]).exists():
            path = cwd.joinpath(*parts[1:])
    except ValueError:
        pass
    return path.resolve()

def doctor(files):
    required = {'PIL': 'Pillow'}
    extensions = {Path(f).suffix.lower() for f in files}
    if '.xlsx' in extensions: required['openpyxl'] = 'openpyxl'
    if '.docx' in extensions: required['docx'] = 'python-docx'
    if '.pptx' in extensions: required['pptx'] = 'python-pptx'
    poppler = bool(shutil.which('pdftotext') and shutil.which('pdftoppm'))
    fitz_ok = importlib.util.find_spec('fitz') is not None
    if '.pdf' in extensions and not poppler:
        required['fitz'] = 'PyMuPDF'
    missing = [package for module, package in required.items() if importlib.util.find_spec(module) is None]
    if missing:
        exe = 'python' if os.name == 'nt' else 'python3'
        raise SystemExit('THIẾU THƯ VIỆN. Chạy: ' + ' '.join([exe, '-m', 'pip', 'install', *missing]))
    if '.pdf' in extensions and not (poppler or fitz_ok):
        raise SystemExit('THIẾU BỘ ĐỌC PDF. Cài PyMuPDF hoặc Poppler rồi chạy lại.')

def story_errors(slides, plan, content):
    errors = []
    chapters = [(i + 1, str(s.get('so', '')).strip()) for i, s in enumerate(slides) if s.get('mau') == 'chuong']
    if len(chapters) >= 2:      # một chương duy nhất chỉ là trang ngăn, đánh số theo deck phẳng
        numbers = []
        for _, value in chapters:
            match = re.fullmatch(r'0*(\d+)', value)
            if not match:
                errors.append('Số chương phải là số nguyên liên tục.'); break
            numbers.append(int(match.group(1)))
        if numbers and numbers != list(range(1, len(numbers) + 1)):
            errors.append('Số chương không liên tục từ 01.')
        current = None
        for i, s in enumerate(slides, 1):
            if s.get('mau') == 'chuong':
                m = re.fullmatch(r'0*(\d+)', str(s.get('so', '')).strip()); current = int(m.group(1)) if m else None; continue
            if s.get('mau') in ('bia', 'cam-on', 'muc-luc') or s.get('soMuc'):
                continue
            label = s.get('dauMuc'); label = label.get('vi', '') if isinstance(label, dict) else str(label or '')
            m = re.match(r'\s*(\d+)', label)
            if current is None and m:
                errors.append(f'Slide {i} nằm trước chương đầu nhưng dauMuc bắt đầu bằng số ({label}); dùng nhãn chữ không số (vd "Tóm tắt điều hành").')
            elif current is not None and not m:
                errors.append(f'Slide {i} thuộc chương {current} nhưng dauMuc "{label}" không bắt đầu bằng {current}.')
            elif current is not None and int(m.group(1)) != current:
                errors.append(f'Slide {i} thuộc chương {current} nhưng dauMuc "{label}" bắt đầu bằng {m.group(1)}; không có số mục lệch chương.')
    else:
        numbered = [(i, s) for i, s in enumerate(slides, 1) if s.get('mau') not in ('bia', 'cam-on', 'muc-luc', 'chuong')]
        wrong = [f'slide {i} (parts/{i:02d}.json): soMuc "{str(s.get("soMuc", "")).strip()}" → cần "{k}"'
                 for k, (i, s) in enumerate(numbered, 1) if str(s.get('soMuc', '')).strip() != str(k)]
        wrong += [f'slide {i} (parts/{i:02d}.json): dauMuc "{s.get("dauMuc")}" bắt đầu bằng số → bỏ số, chỉ để nhãn chữ'
                  for i, s in numbered if re.match(r'\s*\d', str(s.get('dauMuc', {}).get('vi', '') if isinstance(s.get('dauMuc'), dict) else s.get('dauMuc', '')))]
        if wrong:
            errors.append('Deck không có trang chương: slide nội dung (trừ bìa, mục lục, cảm ơn) đặt soMuc phẳng liên tục "1", "2", "3"…; dauMuc chỉ là nhãn chữ. Sửa đúng các chỗ sau:\n  · ' + '\n  · '.join(wrong))
    for item in plan.get('meta', {}).get('computed', []):
        formula = str(item.get('formula', '')) if isinstance(item, dict) else ''
        if not re.search(r'\d\s*[+\-*/]\s*\d', formula) or re.search(r'\bsource\b|nguồn|content\.md', formula, re.I):
            errors.append('meta.computed chỉ nhận phép tính số học; không dùng trích dẫn nguồn để hợp thức hoá số.')
            break
    slide_text = json.dumps(slides, ensure_ascii=False)
    low = content.lower()
    # Ba luật dưới đây rút từ một báo cáo ATBM cụ thể: chỉ áp khi nguồn thật sự có cụm đó, không chặn tài liệu khác.
    if 'vùng còn lại' not in low and 'vùng' not in low:
        return errors
    merged = re.search(r'tích hợp[^\n]{0,90}\d+[\s.]*vùng còn lại', slide_text, re.I)
    if merged and not re.search(r'tích hợp[^\n]{0,90}phiếu sự cố', slide_text, re.I) and re.sub(r'\s+', ' ', merged.group(0).lower()) not in re.sub(r'\s+', ' ', low):
        errors.append('Không ghép mục tiêu tích hợp thiết bị với "vùng còn lại" của kết nối phiếu sự cố; tách thành hai công việc.')
    for claim in re.finditer(r'hoàn thành\s+(vùng\s*\d+\s*(?:,|và)\s*vùng\s*\d+)', slide_text, re.I):
        if claim.group(1).lower() not in content.lower():
            errors.append('Không được đổi "các vùng còn lại" thành tên vùng cụ thể khi nguồn không nêu.')
            break
    compact_content = re.sub(r'\s+', ' ', content.lower())
    for claim in re.finditer(r'hoàn thành\s+tích hợp[^"}]{0,100}vùng[^"}]{0,50}', slide_text, re.I):
        normalized = re.sub(r'\s+', ' ', claim.group(0).lower()).strip(' .,;')
        if normalized not in compact_content:
            errors.append('Không khẳng định hoàn thành tích hợp cho các vùng cụ thể khi nguồn chỉ nêu mục tiêu 2.000 thiết bị.')
            break
    return errors

def authored_hash(work):
    import hashlib
    paths=[work/'plan.json',*sorted((work/'parts').glob('*.json'))]
    return hashlib.sha256(''.join(str(p.relative_to(work))+':'+sha(p) for p in paths if p.exists()).encode()).hexdigest()

ICON_HINTS = (('tien-te|ngan-sach|chi-phi|kinh-phi|tai-chinh|von|tien|gia|hoa-don|thanh-toan', 'tiet-kiem'),
              ('nhan-su|to-chuc|doi-ngu|nhan-vien|con-nguoi|user|team', 'nguoi'),
              ('thoi-gian|han|deadline|tien-do|dong-ho|clock', 'dong-ho'), ('ke-hoach|lich|tuan|thang|calendar', 'lich'),
              ('canh-bao|rui-ro|su-co|loi|nguy|warning|alert', 'canh-bao'), ('hoan-thanh|dat|xong|check|done|thanh-cong|duyet', 'dung'),
              ('mang|network|ket-noi|tich-hop|link', 'ket-noi'), ('may-ao|vm|server|may-chu|ha-tang|datacenter|vcenter|esxi', 'may-chu'),
              ('cloud|dam-may', 'dam-may'), ('bao-mat|an-ninh|attt|khoa|lock|security', 'bao-mat'),
              ('du-lieu|data|csdl|database|sao-luu|backup|luu-tru', 'du-lieu'), ('bao-cao|thong-ke|so-lieu|kpi|chart|ty-le|phan-tram', 'bieu-do'),
              ('tang|tang-truong|growth', 'tang'), ('giam|suy-giam', 'giam'), ('muc-tieu|target|chinh-xac', 'muc-tieu'),
              ('hop-tac|doi-tac|partner', 'hop-tac'), ('khach|doanh-nghiep', 'khach-hang'), ('ma-nguon|code|phan-mem|ung-dung|app', 'ma-nguon'),
              ('cai-dat|cau-hinh|ky-thuat|setting|tool|cong-cu|van-hanh', 'cai-dat'), ('email|thu|mail', 'email'), ('dao-tao|hoc|nghien-cuu|tai-lieu', 'nghien-cuu'))

# Trường hợp lệ của từng danh sách trong mẫu. Trường ngoài danh sách bị khung bỏ qua âm thầm (mất nội dung), nên phải bắt.
COMMON_KEYS = {'mau', 'nhan', 'dauMuc', 'soMuc', 'tieuDe', 'phu', 'ketLuan', 'nguon', 'loiThoai', 'nen'}
SLIDE_KEYS = {'bia': {'the', 'dong', 'doiTac', 'anh'}, 'muc-luc': {'muc'}, 'chuong': {'so'}, 'so-lieu': {'so'}, 'van-de': {'vanDe', 'giaiPhap'},
              'the': {'the'}, 'bang': {'cot', 'hang'}, 'lop': {'lop', 'quanTri', 'ghiChu'}, 'anh': {'anh', 'vung', 'chuGiai'},
              'hinh-so': {'anh', 'so'}, 'lo-trinh': {'buoc'}, 'cam-on': {'lienHe'}}
ITEM_KEYS = {('so-lieu', 'so'): {'so', 'nhan', 'icon'}, ('hinh-so', 'so'): {'so', 'nhan', 'icon'}, ('the', 'the'): {'t', 'd', 'icon', 'logo'},
             ('lo-trinh', 'buoc'): {'t', 'd', 'tg', 'icon'}, ('muc-luc', 'muc'): {'t', 'd'}, ('lop', 'lop'): {'ma', 't', 'noi'},
             ('anh', 'chuGiai'): {'t', 'd'}, ('cam-on', 'lienHe'): {'nhan', 'gt'}}
D_LIMIT = {('the', 'the'): 80, ('lo-trinh', 'buoc'): 40, ('muc-luc', 'muc'): 40, ('anh', 'chuGiai'): 44}

def _vi(value):
    return str(value.get('vi', '')) if isinstance(value, dict) else str(value or '')

def normalize_shapes(slide):
    """Khung dựng slide bằng JS: sai kiểu dữ liệu (hàng bảng là object, thẻ là chuỗi) làm JS dừng, mọi slide sau đó trắng.
    Đổi về đúng kiểu khi suy ra được chắc chắn; không đổi chữ."""
    fixes = []
    if slide.get('mau') == 'bang' and isinstance(slide.get('hang'), list):
        rows = []
        for r in slide['hang']:
            if isinstance(r, dict):
                inner = next((v for v in r.values() if isinstance(v, list)), None)
                r = inner if inner is not None else list(r.values())
            elif not isinstance(r, list):
                r = [r]
            rows.append(r)
        if rows != slide['hang']:
            slide['hang'] = rows; fixes.append('hang: mỗi hàng phải là mảng ô (đã đổi từ object)')
        cols = len(slide.get('cot') or [])
        for r in slide['hang']:
            if cols and len(r) != cols:
                r[:] = (r + [''] * cols)[:cols]; fixes.append(f'hang: đưa hàng về {cols} ô')
    if slide.get('mau') == 'van-de' and isinstance(slide.get('giaiPhap'), dict):
        extra = [k for k in ('so', 'soNhan') if k in slide['giaiPhap']]
        for k in extra: del slide['giaiPhap'][k]     # mẫu chỉ có số ở vế vấn đề; khung vẽ số ở vế giải pháp chữ xanh trên nền xanh (gần như vô hình)
        if extra: fixes.append('giaiPhap: bỏ so/soNhan (mẫu không có, hiện mờ không đọc được)')
    single = {('muc-luc', 'muc'): 't', ('the', 'the'): 't', ('lo-trinh', 'buoc'): 't', ('lop', 'lop'): 't', ('anh', 'chuGiai'): 't', ('cam-on', 'lienHe'): 'gt'}
    for (mau, field), key in single.items():
        if slide.get('mau') == mau and isinstance(slide.get(field), list) and any(isinstance(x, str) for x in slide[field]):
            slide[field] = [{key: x} if isinstance(x, str) else x for x in slide[field]]; fixes.append(f'{field}: chuỗi → object {{{key}}}')
    return fixes

def compose_loi_thoai(s):
    """Lời thoại tự tổng hợp từ CHỮ TRÊN SLIDE (không thêm thông tin ngoài slide): đủ từng ý, từng con số, nguồn và kết luận,
    chia đoạn bằng xuống dòng. Model không phải viết nên không thể bịa."""
    cl = lambda x: re.sub(r'\s+', ' ', _vi(x).replace('*', '')).strip()
    end = lambda x: x if not x or x[-1] in '.!?…' else x + '.'
    objs = lambda key: [x for x in (s.get(key) or []) if isinstance(x, dict)]
    ys = lambda node: [cl(y) for y in (node.get('y') or [])] if isinstance(node, dict) else []
    mau, title = s.get('mau'), cl(s.get('tieuDe'))
    paras = []                                   # (độ ưu tiên, đoạn): đoạn ưu tiên thấp bị bỏ trước khi quá 1500 ký tự
    add = lambda text, pri=1: paras.append((pri, text)) if text and text != '.' else None
    ordinal = lambda k: 'Thứ nhất' if k == 1 else f'Thứ {k}'
    if mau == 'bia':
        add('Kính chào quý vị.', 0); add(end('Hôm nay xin trình bày: ' + title), 0); add(end(cl(s.get('phu'))), 1)
        add(end('Đơn vị, thời gian: ' + cl(s.get('dong'))) if cl(s.get('dong')) else '', 2)
    elif mau == 'muc-luc':
        items = objs('muc'); add(end(f'Nội dung báo cáo gồm {len(items)} phần'), 0)
        for k, m in enumerate(items, 1): add(end(f'Phần {k}: {cl(m.get("t"))}' + (' — ' + cl(m.get('d')) if cl(m.get('d')) else '')), 1)
    elif mau == 'chuong':
        add(end(f'Chuyển sang phần {cl(s.get("so"))}: {title}'), 0); add(end(cl(s.get('phu'))), 1)
    elif mau in ('so-lieu', 'hinh-so'):
        add(end(title), 0); add(end(cl(s.get('phu'))), 2)
        for k, x in enumerate(objs('so'), 1): add(end(f'{ordinal(k)}, {cl(x.get("nhan"))}: {cl(x.get("so"))}' if cl(x.get('nhan')) else f'{ordinal(k)}, {cl(x.get("so"))}'), 1)
    elif mau == 'van-de':
        vd, gp = s.get('vanDe') or {}, s.get('giaiPhap') or {}
        add(end(title), 0)
        if isinstance(vd, dict):
            add(end('Về vấn đề: ' + cl(vd.get('t'))), 1)
            for y in ys(vd): add(end('- ' + y), 1)
            if cl(vd.get('so')): add(end(f'Con số đáng chú ý: {cl(vd.get("so"))} {cl(vd.get("soNhan"))}'.strip()), 1)
        if isinstance(gp, dict):
            add(end('Về giải pháp: ' + cl(gp.get('t'))), 1)
            for y in ys(gp): add(end('- ' + y), 1)
    elif mau == 'the':
        add(end(title), 0); add(end(cl(s.get('phu'))), 2)
        for k, x in enumerate(objs('the'), 1): add(end(f'{ordinal(k)}, {cl(x.get("t"))}' + (': ' + cl(x.get('d')) if cl(x.get('d')) else '')), 1)
    elif mau == 'bang':
        cols = [cl(c) for c in (s.get('cot') or [])]; rows = [r for r in (s.get('hang') or []) if isinstance(r, list) and r]
        add(end(title), 0); add(end(cl(s.get('phu'))), 2); add(end('Bảng gồm các cột: ' + ', '.join(cols)), 2)
        for r in rows:
            cells = [(cols[k] if k < len(cols) else '') + ': ' + cl(c) for k, c in enumerate(r[1:], 1) if cl(c)]
            add(end(f'{cl(r[0])} — ' + '; '.join(cells)), 1)
    elif mau == 'lop':
        add(end(title), 0)
        for x in objs('lop'): add(end(f'Lớp {cl(x.get("ma"))}: {cl(x.get("t"))}' + (' (lớp trọng tâm)' if x.get('noi') else '')), 1)
        if cl(s.get('quanTri')): add(end('Quản trị chung: ' + cl(s.get('quanTri'))), 1)
        gc = s.get('ghiChu') or {}
        if isinstance(gc, dict) and cl(gc.get('t')): add(end(cl(gc.get('t')) + ': ' + '; '.join(ys(gc))), 1)
    elif mau == 'lo-trinh':
        add(end(title), 0); add(end(cl(s.get('phu'))), 2)
        for k, x in enumerate(objs('buoc'), 1):
            add(end(f'Bước {k}' + (f' ({cl(x.get("tg"))})' if cl(x.get('tg')) else '') + f': {cl(x.get("t"))}' + (' — ' + cl(x.get('d')) if cl(x.get('d')) else '')), 1)
    elif mau == 'anh':
        add(end(title), 0)
        for x in objs('chuGiai'): add(end(cl(x.get('t')) + (': ' + cl(x.get('d')) if cl(x.get('d')) else '')), 1)
    elif mau == 'cam-on':
        add('Xin chân thành cảm ơn quý vị đã lắng nghe.', 0); add(end('Liên hệ: ' + '; '.join(cl(x.get('gt')) for x in objs('lienHe') if cl(x.get('gt')))) if objs('lienHe') else '', 1)
    else: add(end(title), 0)
    if mau not in ('bia', 'cam-on'):
        add(end('Điều cần nhớ: ' + cl(s.get('ketLuan'))) if cl(s.get('ketLuan')) else '', 0)
        nguon = re.sub(r'^\s*Nguồn\s*:?\s*', '', cl(s.get('nguon')))
        add(end('Nguồn số liệu: ' + nguon) if nguon else '', 2)
    limit = 1500
    while paras and sum(len(t) + 1 for _, t in paras) > limit:       # bỏ đoạn ưu tiên thấp nhất, từ cuối lên
        worst = max(p for p, _ in paras)
        if worst == 0: break
        idx = max(k for k, (p, _) in enumerate(paras) if p == worst); paras.pop(idx)
    text = '\n'.join(t for _, t in paras)
    return text if len(text) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'

CHAPTER_STOP = {'của', 'và', 'các', 'cho', 'với', 'trong', 'một', 'những', 'được', 'về', 'tại', 'theo', 'này', 'khi', 'từ', 'đến', 'phần', 'nhóm', 'vnpt', 'chương'}

def _words_of(text, min_len=3):
    return {w for w in re.findall(r'\w{%d,}' % min_len, str(text).lower()) if w not in CHAPTER_STOP}

def _slide_text(node):
    """Gom mọi chuỗi chữ của một slide (bỏ tên mẫu, icon)."""
    if isinstance(node, dict): return ' '.join(_slide_text(v) for k, v in node.items() if k not in ('mau', 'icon', 'nen', 'loiThoai'))
    if isinstance(node, list): return ' '.join(_slide_text(v) for v in node)
    return _vi(node) if isinstance(node, dict) else str(node or '')

def source_structure(work):
    """Cấu trúc của FILE NGUỒN: {số slide nguồn: chữ}, và {số phần: số slide nguồn là slide ngăn phần}. Slide ngăn phần là slide rất ngắn
    mở đầu bằng số phần ("01 ĐỊNH HƯỚNG…", "03 CAM KẾT…"), không phải mục con kiểu "2.1 …". Trả ({}, {}) nếu nguồn không rõ ràng."""
    path = work / 'content.md'
    if not path.is_file(): return {}, {}
    text = path.read_text(encoding='utf-8')
    if len(re.findall(r'(?m)^# NGUỒN \d+', text)) != 1: return {}, {}      # nhiều nguồn: số slide trùng nhau, không dùng
    parts = re.split(r'(?m)^## (?:Slide|Trang)\s+(\d+)\s*$', text)
    sections = {int(parts[i]): re.sub(r'\s+', ' ', parts[i + 1]).strip() for i in range(1, len(parts) - 1, 2)}
    dividers = {}
    for n, flat in sections.items():
        m = re.match(r'^0?(\d{1,2})\s+(?!\d)(?!\.)\S', flat)
        if m and len(flat) <= 260 and int(m.group(1)) not in dividers: dividers[int(m.group(1))] = n
    return sections, dividers

def place_by_source(work, slides, chapter_idx, k, name):
    """Vị trí chèn chương số k (đếm từ 1) theo cấu trúc file nguồn: slide báo cáo đầu tiên tương ứng với slide nguồn đứng SAU slide ngăn phần k,
    với điều kiện slide đứng trước nó tương ứng với nội dung TRƯỚC slide ngăn đó. Trả (vị trí, lý do) hoặc (None, lý do không chắc)."""
    sections, dividers = source_structure(work)
    if k not in dividers: return None, 'nguồn không có slide ngăn phần ' + str(k)
    D = dividers[k]
    want = _words_of(name)
    if want and len(want & _words_of(sections[D])) / len(want) < 0.5: return None, 'slide ngăn phần ở nguồn không khớp tên phần trong mục lục'
    import math
    content_src = {n: _words_of(t) for n, t in sections.items() if n not in dividers.values() and len(t) > 150}
    df = {}
    for w in content_src.values():
        for t in w: df[t] = df.get(t, 0) + 1
    idf = lambda t: math.log((1 + len(content_src)) / (1 + df.get(t, 0))) + 0.1   # từ chung cho mọi slide (Hải Phòng, thành phố…) gần như không có trọng số
    start = chapter_idx[-1] + 1
    mapped = {}
    for i in range(start, len(slides)):
        x = slides[i]
        if not isinstance(x, dict) or x.get('mau') in ('chuong', 'cam-on', 'muc-luc', 'bia'): continue
        r = _words_of(_slide_text(x))
        if len(r) < 5: continue
        total = sum(idf(t) for t in r)
        ranked = sorted(((sum(idf(t) for t in r & w) / total, n) for n, w in content_src.items()), reverse=True)
        if ranked and ranked[0][0] >= 0.5 and (len(ranked) < 2 or ranked[0][0] - ranked[1][0] >= 0.08): mapped[i] = ranked[0][1]   # chỉ nhận khi khớp rõ một slide nguồn
    after = [i for i, n in mapped.items() if n > D]
    before = [i for i, n in mapped.items() if n < D]
    if not after or not before: return None, 'không đối chiếu được slide báo cáo với slide nguồn quanh ranh giới phần'
    # điểm đổi chiều: slide đầu của phần mới phải là slide ứng với nguồn SAU slide ngăn; chọn vị trí ít "lệch thứ tự" nhất
    # (chịu được 1 slide tóm tắt gộp nhiều slide nguồn nên đối chiếu nhầm), và phải hơn hẳn vị trí tốt thứ hai.
    errs = sorted((sum(1 for i, n in mapped.items() if i < b and n > D) + sum(1 for i, n in mapped.items() if i >= b and n < D), b)
                  for b in after if b >= chapter_idx[-1] + 2)
    if not errs: return None, 'chương trước sẽ không còn slide nào'
    best_err, p = errs[0]
    if best_err > max(1, len(mapped) // 5) or (len(errs) > 1 and errs[1][0] - best_err < 1): return None, 'thứ tự slide báo cáo không khớp thứ tự nguồn'
    return p, f'theo cấu trúc file nguồn: slide ngăn phần {k} ở slide nguồn {D}'

def _load_deck(work):
    """(plan, outline, slides) của bộ parts liên tục 01..N khớp outline; None nếu chưa đủ điều kiện."""
    plan_path = work / 'plan.json'
    if not plan_path.is_file() or not (work / 'parts').is_dir(): return None
    plan = load(plan_path); outline = plan.get('outline')
    if not isinstance(outline, list): return None
    numbers = sorted(int(p.stem) for p in (work / 'parts').glob('*.json') if p.stem.isdigit())
    if not numbers or numbers != list(range(1, numbers[-1] + 1)) or len(outline) != len(numbers): return None
    try: slides = [load(work / 'parts' / f'{n:02d}.json') for n in numbers]
    except SystemExit: return None
    return plan, outline, slides

def _save_deck(work, plan, outline, slides):
    for n, x in enumerate(slides, 1): write_json(work / 'parts' / f'{n:02d}.json', x)
    for stale in (work / 'parts').glob('*.json'):
        if stale.stem.isdigit() and int(stale.stem) > len(slides): stale.unlink()
    plan['outline'] = outline; write_json(work / 'plan.json', plan)

def add_missing_chapters(work):
    """CẤU TRÚC CÁC PHẦN QUYẾT ĐỊNH TRƯỚC, mục lục sinh ra từ đó (không phải ngược lại). Nguồn cấu trúc: các slide ngăn phần của FILE NGUỒN
    ("01 …", "02 …", "03 …"). Nếu nguồn có nhiều phần hơn số slide chương trong báo cáo (model bỏ sót), thêm slide chương còn thiếu,
    đặt theo đối chiếu nội dung với nguồn. Chỉ thêm khi chắc; không chắc thì không đoán, ghi vào meta.canXacNhan.
    Không có cấu trúc ở nguồn thì không làm gì: các phần là những chương model đã viết."""
    deck = _load_deck(work)
    if deck is None: return None
    plan, outline, slides = deck
    sections, dividers = source_structure(work)
    if len(dividers) < 2: return None
    chapters = lambda: [i for i, x in enumerate(slides) if isinstance(x, dict) and x.get('mau') == 'chuong']
    if not chapters() or len(chapters()) >= len(dividers): return None
    toc = next((x for x in slides if isinstance(x, dict) and x.get('mau') == 'muc-luc' and isinstance(x.get('muc'), list)), None)
    names_in_toc = [_vi(m.get('t')).strip() for m in (toc or {}).get('muc', []) if isinstance(m, dict)]
    added, msgs = [], []
    meta = plan.setdefault('meta', {}); notes = meta.setdefault('canXacNhan', [])
    cut = lambda t, n: t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'
    while len(chapters()) < len(dividers):
        k = len(chapters()) + 1
        src_title = re.sub(r'^\s*0?\d{1,2}\s+', '', sections[dividers[k]])
        src_title = re.sub(r'\s*>\s*Ghi chú người nói:.*$', '', src_title).strip()
        src_title = re.sub(r'\s*\d+\s*$', '', src_title).strip()                  # số trang cuối slide ngăn
        name = names_in_toc[k - 1] if k - 1 < len(names_in_toc) and names_in_toc[k - 1] else src_title
        best, why = place_by_source(work, slides, chapters(), k, name if names_in_toc[k - 1:k] else '')
        if best is None:
            msgs.append(f'Nguồn có phần {k} "{cut(src_title, 60)}" nhưng báo cáo chưa có slide ngăn chương và driver không xác định chắc vị trí ({why}): người trình bày thêm slide chương này đúng chỗ.')
            break
        width = len(str(slides[chapters()[0]].get('so', ''))) or 1
        new = {'mau': 'chuong', 'so': str(k).zfill(width), 'tieuDe': cut(name, 48)}
        before = _vi(slides[best].get('tieuDe')).strip()
        slides.insert(best, new); outline.insert(best, new['tieuDe']); added.append(new['tieuDe'])
        notes.append(f'Slide ngăn chương {k} "{new["tieuDe"]}" do driver tự thêm trước slide {best + 1} "{before[:50]}" ({why}): kiểm lại vị trí.')
    msgs = [x for x in msgs if x not in notes]; notes.extend(msgs)
    if not added and not msgs: return None
    _save_deck(work, plan, outline, slides)
    out = []
    if added: out.append('thêm slide ngăn chương còn thiếu theo cấu trúc file nguồn: ' + '; '.join(added))
    if msgs: out.append('KHÔNG thêm chương vì chưa chắc vị trí (đã ghi vào canXacNhan)')
    return ' | '.join(out)

def sync_toc_with_chapters(work):
    """Mục lục là sản phẩm SUY RA từ các slide chương, không phải thứ để chương chạy theo. Khung K7 chỉ cho mục lục khi có 3–6 phần:
    ít hơn 3 chương thì bỏ slide mục lục (ghi vào canXacNhan). Từ 3–6 chương thì phần dựng lại mục lục nằm ở autofix_parts."""
    deck = _load_deck(work)
    if deck is None: return None
    plan, outline, slides = deck
    chapters = [x for x in slides if isinstance(x, dict) and x.get('mau') == 'chuong']
    idx = next((i for i, x in enumerate(slides) if isinstance(x, dict) and x.get('mau') == 'muc-luc'), None)
    if idx is None or len(chapters) >= 3: return None
    notes = plan.setdefault('meta', {}).setdefault('canXacNhan', [])
    notes.append(f'Đã bỏ slide mục lục: báo cáo chỉ có {len(chapters)} phần (khung K7 chỉ dùng mục lục từ 3 phần trở lên).')
    del slides[idx]; del outline[idx]
    _save_deck(work, plan, outline, slides)
    return f'bỏ slide mục lục vì báo cáo chỉ có {len(chapters)} chương'

def cover_label(doc, date=''):
    """Bìa có nhãn nhỏ (viên thuốc viền) ở trên tiêu đề; để trống thì chỉ còn hình oval rỗng. Điền loại tài liệu + năm lấy từ chính slide/nguồn."""
    title = (_vi(doc.get('tieuDe')) + ' ' + _vi(doc.get('phu'))).lower()
    kind = next((name for key, name in (('đề xuất', 'Đề xuất'), ('báo cáo', 'Báo cáo'), ('kế hoạch', 'Kế hoạch'), ('tổng kết', 'Tổng kết'), ('kiến nghị', 'Kiến nghị')) if key in title), 'Báo cáo điều hành')
    year = re.search(r'(20\d\d)', _vi(doc.get('dong')) + ' ' + _vi(doc.get('tieuDe')) + ' ' + str(date or ''))
    return kind + (' · ' + year.group(1) if year else '')

def merge_extra_text(slide):
    """Mẫu thẻ/bước/mục lục chỉ có t và d. Model hay thêm `nhan`/`mota`: gộp vào d khi còn chỗ để không mất chữ."""
    fixes = []
    for (mau, field), allowed in ITEM_KEYS.items():
        if slide.get('mau') != mau or not isinstance(slide.get(field), list) or 'd' not in allowed:
            continue
        for k, item in enumerate(slide[field]):
            if not isinstance(item, dict): continue
            for extra in [x for x in item if x not in allowed and isinstance(item[x], (str, dict)) and _vi(item[x]).strip()]:
                if isinstance(item[extra], dict) or isinstance(item.get('d'), dict): continue   # song ngữ: để báo lỗi cho model quyết
                merged = (_vi(item[extra]).strip().rstrip('.:') + (': ' + _vi(item.get('d')).strip() if _vi(item.get('d')).strip() else ''))
                if len(merged) <= D_LIMIT.get((mau, field), 80):
                    item['d'] = merged; del item[extra]; fixes.append(f'{mau}.{field}.{k}: gộp "{extra}" vào d')
    return fixes

def unknown_key_errors(slide):
    """Mã M11: trường không thuộc mẫu sẽ bị bỏ khỏi slide mà không báo lỗi nào."""
    mau = slide.get('mau'); errors = []
    if mau not in SLIDE_KEYS: return errors
    for key in slide:
        if key not in COMMON_KEYS | SLIDE_KEYS[mau]:
            errors.append(f'Mẫu "{mau}" không có trường "{key}": nội dung này sẽ KHÔNG hiện trên slide. Đưa vào trường đúng của mẫu hoặc bỏ.')
    for (m, field), allowed in ITEM_KEYS.items():
        if m != mau or not isinstance(slide.get(field), list): continue
        for k, item in enumerate(slide[field]):
            if isinstance(item, dict):
                for key in item:
                    if key not in allowed:
                        errors.append(f'{field}.{k}: mẫu "{mau}" chỉ có {", ".join(sorted(allowed))}; trường "{key}" sẽ KHÔNG hiện trên slide. Gộp chữ vào trường đúng.')
    return errors

def nearest_icon(name, icons):
    import difflib
    key = re.sub(r'[^a-z0-9]+', '-', str(name).lower().replace('đ', 'd')).strip('-')
    for words, icon in ICON_HINTS:
        if icon in icons and any(w in key for w in words.split('|')):
            return icon
    close = difflib.get_close_matches(key, list(icons), 1, 0.5)
    return close[0] if close else ('bieu-do' if 'bieu-do' in icons else sorted(icons)[0])

def _strip_number(label):
    return re.sub(r'^\s*\d+(\.\d+)*\s*[·.\-–:)]?\s*', '', label).strip()

def _map_label(value, fn):
    if isinstance(value, dict):
        return {k: (fn(v) if k == 'vi' and isinstance(v, str) else v) for k, v in value.items()}
    return fn(str(value or ''))

def autofix_parts(work, outline, icons, source_label='', date=''):
    """Sửa tự động các lỗi cơ học mà model hay mắc (tên icon lạ, số chương/số mục lệch) để không tốn lượt build.
    Chỉ đổi trường cơ học; không đụng tới chữ, số liệu hay ý của slide. Trả về danh sách việc đã sửa."""
    fixes = []
    paths = [work / 'parts' / f'{i:02d}.json' for i in range(1, len(outline) + 1)]
    docs = {}
    for path in paths:
        if path.is_file():
            try: docs[path] = json.loads(path.read_text(encoding='utf-8'))
            except ValueError: pass
    changed = set()
    def walk(node, path):
        if isinstance(node, dict):
            if isinstance(node.get('icon'), str) and node['icon'] not in icons:
                new = nearest_icon(node['icon'], icons)
                fixes.append(f'{path.name}: icon "{node["icon"]}" không có trong thư viện → "{new}"'); node['icon'] = new; changed.add(path)
            for v in node.values(): walk(v, path)
        elif isinstance(node, list):
            for v in node: walk(v, path)
    for path, doc in docs.items(): walk(doc, path)
    for path, doc in docs.items():
        if doc.get('mau') not in ('bia', 'chuong', 'cam-on', 'muc-luc') and not _vi(doc.get('dauMuc')).strip():
            label = _vi(doc.get('nhan')).strip() or re.sub(r'\*', '', _vi(doc.get('tieuDe'))).strip()
            if label:
                if len(label) > 32: label = label[:32].rsplit(' ', 1)[0]
                doc['dauMuc'] = label; changed.add(path); fixes.append(f'{path.name}: thiếu dauMuc → "{label}"')
        if source_label and doc.get('mau') in ('so-lieu', 'hinh-so', 'van-de') and not _vi(doc.get('nguon')).strip():
            doc['nguon'] = ('Nguồn: ' + source_label)[:130]; changed.add(path); fixes.append(f'{path.name}: thiếu nguon → "{doc["nguon"]}"')
        if doc.get('mau') == 'bia' and not _vi(doc.get('the')).strip():
            doc['the'] = cover_label(doc, date); changed.add(path); fixes.append(f'{path.name}: bìa thiếu nhãn nhỏ → "{doc["the"]}"')
        for note in merge_extra_text(doc) + normalize_shapes(doc):
            fixes.append(f'{path.name}: {note}'); changed.add(path)
    if len(docs) == len(paths):                     # đánh số chỉ làm được khi đủ cả bộ
        slides = [docs[p] for p in paths]
        chapters = [s for s in slides if s.get('mau') == 'chuong']
        if len(chapters) >= 2:
            for k, s in enumerate(chapters, 1):
                if str(s.get('so', '')).strip().lstrip('0') != str(k):
                    s['so'] = str(k); changed.add(paths[slides.index(s)]); fixes.append(f'{paths[slides.index(s)].name}: số chương → {k}')
        current = None
        for path, s in zip(paths, slides):
            if s.get('mau') == 'chuong':
                m = re.fullmatch(r'0*(\d+)', str(s.get('so', '')).strip()); current = int(m.group(1)) if m else None; continue
            if s.get('mau') in ('bia', 'cam-on', 'muc-luc'): continue
            if len(chapters) >= 2:
                if s.get('soMuc'):                   # có chương thì không dùng soMuc phẳng
                    del s['soMuc']; changed.add(path); fixes.append(f'{path.name}: bỏ soMuc (deck có chương)')
                if 'dauMuc' in s:
                    label = s['dauMuc'].get('vi', '') if isinstance(s['dauMuc'], dict) else str(s['dauMuc'] or '')
                    want = (f'{current} · {_strip_number(label)}' if current is not None else _strip_number(label))
                    if label.strip() != want:
                        s['dauMuc'] = _map_label(s['dauMuc'], lambda _v, w=want: w); changed.add(path); fixes.append(f'{path.name}: dauMuc → "{want}"')
            else:
                flat = [(p, x) for p, x in zip(paths, slides) if x.get('mau') not in ('bia', 'cam-on', 'muc-luc', 'chuong')]
                k = [p for p, _ in flat].index(path) + 1
                if str(s.get('soMuc', '')).strip() != str(k):
                    s['soMuc'] = str(k); changed.add(path); fixes.append(f'{path.name}: soMuc → "{k}"')
                if 'dauMuc' in s:
                    label = s['dauMuc'].get('vi', '') if isinstance(s['dauMuc'], dict) else str(s['dauMuc'] or '')
                    if re.match(r'\s*\d', label):
                        s['dauMuc'] = _map_label(s['dauMuc'], _strip_number); changed.add(path); fixes.append(f'{path.name}: dauMuc bỏ số đầu')
    if len(docs) == len(paths):
        slides = [docs[p] for p in paths]
        chapters = [(p, s) for p, s in zip(paths, slides) if s.get('mau') == 'chuong']
        for path, s in zip(paths, slides):
            toc_t = [_vi(m.get('t')) for m in s.get('muc', []) if isinstance(m, dict)] if isinstance(s.get('muc'), list) else []
            matches = len(toc_t) == len(chapters) and all(_words_of(t) & _words_of(_vi(c.get('tieuDe'))) for t, (_, c) in zip(toc_t, chapters))   # mục lục viết gọn vẫn đúng phần nào thì giữ chữ của model
            if s.get('mau') == 'muc-luc' and isinstance(s.get('muc'), list) and 3 <= len(chapters) <= 6 and not matches:
                s['muc'] = [{'t': _vi(c.get('tieuDe')).replace('*', '').strip()[:28].rsplit(' ', 1)[0] if len(_vi(c.get('tieuDe')).replace('*', '').strip()) > 28 else _vi(c.get('tieuDe')).replace('*', '').strip(),
                             **({'d': _vi(c['phu']).strip()[:40].rsplit(' ', 1)[0] if len(_vi(c['phu']).strip()) > 40 else _vi(c['phu']).strip()} if _vi(c.get('phu')).strip() else {})} for _, c in chapters]
                changed.add(path); fixes.append(f'{path.name}: mục lục dựng lại từ {len(chapters)} slide chương (mục lục suy ra từ chương)')
    for path in changed:
        write_json(path, docs[path])
    return fixes

def fix_plan(work):
    """Model hay viết outline là danh sách object ({"tieuDe":…}) hoặc quên các khoá phụ: chuẩn hoá về danh sách tiêu đề."""
    plan_path = work / 'plan.json'
    if not plan_path.is_file():
        return None
    try: plan = json.loads(plan_path.read_text(encoding='utf-8'))
    except ValueError: return None
    if not isinstance(plan, dict): return None
    notes = []; old = {}
    if not isinstance(plan.get('meta'), dict):
        old = plan.pop('metadata', None) if isinstance(plan.get('metadata'), dict) else {}
        plan['meta'] = {k: v for k, v in old.items() if k in ('ten', 'ban', 'computed', 'canXacNhan')}
        if old: notes.append('metadata → meta')
    meta = plan['meta']
    if not (meta.get('ten') and _vi(meta.get('ten')).strip()):
        guess = _vi(meta.get('title') or old.get('title') or '').strip()
        if not guess:
            first = (plan.get('outline') or [''])[0]
            guess = _vi(first.get('tieuDe') or first.get('title') if isinstance(first, dict) else first).strip()
        meta['ten'] = {'vi': guess or 'Báo cáo điều hành'}; notes.append('thêm meta.ten')
    meta.setdefault('computed', [])
    if notes: write_json(plan_path, plan)
    outline = plan.get('outline')
    if not isinstance(outline, list) or all(isinstance(x, str) for x in outline):
        return ('plan.json: ' + ', '.join(notes)) if notes else None
    titles = []
    for k, item in enumerate(outline, 1):
        if isinstance(item, dict):
            value = next((item[key] for key in ('tieuDe', 'title', 'tenSlide', 'ten', 'tên', 't', 'name', 'noiDung') if item.get(key)), None)
            if value is None: value = next((v for v in item.values() if isinstance(v, (str, dict)) and v), f'Slide {k}')
            item = value
        titles.append(_vi(item).strip() or f'Slide {k}')
    plan['outline'] = titles; write_json(plan_path, plan)
    return 'outline chuyển thành danh sách tiêu đề' + (' ; ' + ', '.join(notes) if notes else '')

def extend_outline(work):
    """Model viết nhiều slide hơn outline (parts liên tục 01..M): nới outline theo tieuDe của các slide đó thay vì báo lỗi."""
    plan_path = work / 'plan.json'
    if not plan_path.is_file() or not (work / 'parts').is_dir():
        return None
    plan = load(plan_path); outline = plan.get('outline')
    if not isinstance(outline, list):
        return None
    numbers = sorted(int(p.stem) for p in (work / 'parts').glob('*.json') if p.stem.isdigit())
    if not numbers or numbers != list(range(1, numbers[-1] + 1)) or numbers[-1] <= len(outline):
        return None
    for n in range(len(outline) + 1, numbers[-1] + 1):
        try: slide = load(work / 'parts' / f'{n:02d}.json')
        except SystemExit: return None
        title = slide.get('tieuDe') if isinstance(slide, dict) else None
        outline.append((title.get('vi') if isinstance(title, dict) else str(title or '')).strip() or f'Slide {n}')
    plan['outline'] = outline; write_json(plan_path, plan)
    return f'outline nới thành {len(outline)} slide theo các parts đã ghi'

def split_long_tables(work):
    """Bảng `bang` nhận 2–5 hàng. Model hay dồn cả bảng theo dõi (10–13 dòng) vào một slide rồi lặp suy nghĩ để chọn bỏ dòng nào:
    driver tự chia thành nhiều slide bảng cân bằng, giữ nguyên từng hàng (không bỏ, không sửa chữ)."""
    plan_path = work / 'plan.json'
    if not plan_path.is_file() or not (work / 'parts').is_dir(): return None
    plan = load(plan_path); outline = plan.get('outline')
    if not isinstance(outline, list): return None
    numbers = sorted(int(p.stem) for p in (work / 'parts').glob('*.json') if p.stem.isdigit())
    if not numbers or numbers != list(range(1, numbers[-1] + 1)): return None
    slides = []
    for n in numbers:
        try: slides.append(load(work / 'parts' / f'{n:02d}.json'))
        except SystemExit: return None
    if not any(isinstance(x, dict) and x.get('mau') == 'bang' and isinstance(x.get('hang'), list) and len(x['hang']) > 5 for x in slides): return None
    titles = list(outline) + [''] * (len(slides) - len(outline))
    out_slides, out_titles, added = [], [], 0
    for slide, title in zip(slides, titles):
        rows = slide.get('hang') if isinstance(slide, dict) and slide.get('mau') == 'bang' else None
        if not isinstance(rows, list) or len(rows) <= 5:
            out_slides.append(slide); out_titles.append(title); continue
        count = -(-len(rows) // 5); size, extra = divmod(len(rows), count); start = 0
        base = re.sub(r'\s*\(\d+/\d+\)\s*$', '', _vi(slide.get('tieuDe')).strip())
        if len(base) > 40:                            # cắt ở ranh giới từ, không để lại dấu ngoặc mở dở
            cut = base[:40]
            cut = cut[:cut.rfind('(')] if cut.count('(') > cut.count(')') else cut.rsplit(' ', 1)[0]
            base = cut.strip(' ,;:-–—(')
        for k in range(count):
            take = size + (1 if k < extra else 0)
            piece = {**slide, 'hang': rows[start:start + take]}; start += take
            piece['tieuDe'] = f'{base} ({k + 1}/{count})'
            out_slides.append(piece); out_titles.append(piece['tieuDe'])
        added += count - 1
    for i, slide in enumerate(out_slides, 1): write_json(work / 'parts' / f'{i:02d}.json', slide)
    plan['outline'] = out_titles; write_json(plan_path, plan)
    return f'chia bảng quá 5 hàng thành nhiều slide bảng (thêm {added} slide, giữ nguyên mọi hàng)'

def part_inventory_errors(work, outline):
    """Reject ambiguous or out-of-plan part names before the model continues."""
    parts = work / 'parts'
    expected = {f'{i:02d}.json' for i in range(1, len(outline) + 1)}
    actual = {p.name for p in parts.glob('*.json')}
    extra = sorted(actual - expected)
    errors = []
    if extra:
        errors.append('Có parts ngoài outline: ' + ', '.join(extra) + '. Chỉ dùng tên tuần tự 01.json, 02.json…; sửa plan hoặc đánh lại số, không tạo 02b.json.')
    seen = {}
    for name in sorted(actual & expected):
        data = load(parts / name)
        signature = json.dumps(data, ensure_ascii=False, sort_keys=True)
        if signature in seen:
            errors.append(f'{name} trùng hoàn toàn với {seen[signature]}. Sửa outline/nội dung và đánh lại số trước khi tiếp tục.')
        else:
            seen[signature] = name
    return errors

SIGNATURES = {'bia': 'the, tieuDe, phu, dong, doiTac(tuỳ chọn)', 'muc-luc': 'muc[]{t,d}', 'chuong': 'so, tieuDe, phu',
              'so-lieu': 'so[]{so,nhan,icon}, ketLuan, nguon', 'van-de': 'vanDe{t,y[],so,soNhan}, giaiPhap{t,y[]}, nguon',
              'the': 'the[]{t,d,icon}', 'bang': 'cot[] (tên cột), hang[][] = mảng các hàng, mỗi hàng là MỘT MẢNG ô, vd [["A","1","x"],["B","2","y"]] (không dùng object)', 'lop': 'lop[]{ma,t,noi}, quanTri, ghiChu{t,y[]}',
              'anh': 'anh{src,alt}, vung[]{x,y,w,h}, chuGiai[]{t,d}', 'hinh-so': 'anh{src,alt}, so[]{so,nhan,icon}, nguon',
              'lo-trinh': 'buoc[]{t,d,tg,icon}', 'cam-on': 'tieuDe, phu, lienHe[]{nhan,gt}'}

def cheatsheet(theme):
    """Bảng 12 mẫu K7 gọn (trường, số mục, giới hạn ký tự, icon) in một lần ở `start`, thay cho việc đọc cả huong-dan-k7.md."""
    try:
        rules = json.loads((ROOT / 'k7' / theme / 'khung' / 'quy-tac-mau.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return ''
    lines = ['BẢNG MẪU K7 (đủ để viết slide; chỉ dùng đúng các trường dưới đây, trường lạ bị khung bỏ). Chung: mau, tieuDe ≤64 (một câu kết luận; bọc 1 cụm bằng *dấu sao*), nhan ≤28, dauMuc ≤32, ketLuan ≤100, nguon ≤130 (bắt buộc ở so-lieu/hinh-so/van-de).']
    for name, spec in rules['mau'].items():
        counts = ', '.join(f'{k} {lo}-{hi} mục' for k, (lo, hi) in spec.get('ds', {}).items())
        limits = ', '.join(f'{k}≤{v}' for k, v in spec.get('gh', {}).items() if k != 'tieuDe')
        lines.append(f'- {name}: {SIGNATURES.get(name, "")}' + (f' · {counts}' if counts else '') + (f' · {limits}' if limits else ''))
    icons = rules.get('icon')
    lines.append('Icon hợp lệ (mỗi thẻ/ô/bước một icon đúng nghĩa): ' + (', '.join(icons) if icons else 'xem huong-dan-k7.md mục 6'))
    return '\n'.join(lines)

BRIEF_MIN_CHARS = 24000

def make_brief(work, budget=14000):
    """Nguồn dài (vd 36 slide, 63K ký tự): đọc cả content.md làm đầy ngữ cảnh rồi bị nén giữa chừng. Dựng bản tóm tắt ~14K ký tự
    (đầu mỗi slide/trang + số dòng trong content.md để đọc chi tiết khi cần). Driver vẫn kiểm số liệu với content.md đầy đủ."""
    src = work / 'content.md'
    if not src.is_file(): return None
    text = src.read_text(encoding='utf-8')
    if len(text) <= BRIEF_MIN_CHARS: return None
    lines = text.splitlines()
    heads = [i for i, l in enumerate(lines) if re.match(r'##\s+\S', l)]
    if len(heads) < 4: return None
    per = max(220, min(700, budget // len(heads)))
    out = ['# Tóm tắt nguồn (driver tạo tự động)', 'Mỗi mục: đầu nội dung + số dòng trong content.md. Cần số liệu hoặc ý chi tiết của một mục thì read content.md đúng khoảng dòng đó.', '']
    out += [l for l in lines[:heads[0]] if l.strip()][:14]
    for k, h in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        body = ' / '.join(x.strip() for x in lines[h + 1:end] if x.strip())
        if len(body) > per: body = body[:per - 1].rsplit(' ', 1)[0] + '…'
        out.append(f'{lines[h].strip()} (content.md dòng {h + 1}-{end}): {body}')
    (work / 'tom-tat.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
    return work / 'tom-tat.md'

def resume(work):
    verify_state(work)
    state = load(work / 'iwork-state.json')
    if str(state.get('phase','')).startswith('complete'):
        if reopen_if_needed(work, state):
            state = load(work / 'iwork-state.json')
        else:
            print('HOÀN TẤT. '+str(local(work/'delivery.json')))
            print(IVIEW_NOTICE);return
    (work / 'STATUS.md').write_text(
        '# iWork — đang soạn báo cáo\n'
        'Entry point duy nhất: iwork.py ở gốc skill, không phải scripts/report.py.\n'
        'Ghi plan.json và từng parts/NN.json theo lệnh resume. Không sửa report.json.\n'
        f'Tiếp tục: {command("resume", work)}\n', encoding='utf-8')
    if state.get('phase')=='quality' and (work/'report.json').exists():
        if state.get('authored_sha256')!=authored_hash(work):
            print('Parts/plan đã đổi. NEXT: '+command('build',work));return
        settle_quality(work, argparse.Namespace(work=str(work)));return
    plan = work / 'plan.json'
    if not plan.exists():
        brief = make_brief(work)
        if brief:
            print(f'ĐỌC (một lần): {local(brief)} (nguồn dài nên đã tóm tắt) và {local(work / "facts.md")}. Chỉ khi cần số liệu/ý chi tiết của một slide mới read {local(work / "content.md")} đúng khoảng dòng ghi trong tóm tắt (offset/limit); KHÔNG đọc cả tệp. Không cần đọc huong-dan-k7.md: bảng mẫu K7 in ngay dưới đây.')
        else:
            print(f'ĐỌC (một lần): {local(work / "content.md")}, {local(work / "facts.md")}. Không cần đọc huong-dan-k7.md: bảng mẫu K7 in ngay dưới đây.')
        print('KHÔNG đọc mã nguồn skill (iwork.py, scripts/*.py, SKILL.md, references/): không cần và làm đầy ngữ cảnh.')
        sheet = cheatsheet(state.get('giao_dien', DEFAULT_THEME))
        if sheet: print(sheet)
        print(f'GHI {local(work / "notes.md")}: thông điệp chính, ngày nguồn và các số liệu cần dùng kèm vị trí trong nguồn (tối đa 25 dòng). Đây là bộ nhớ để làm tiếp nếu bị ngắt; các lô sau đọc notes.md thay vì đọc lại toàn bộ nguồn.')
        print(f'GHI {local(plan)}: {{"meta":{{"ten":{{"vi":"…","en":"…"}},"ban":"Bản 1 · dd/mm/yyyy","computed":[]}},"outline":["tên từng slide"]}}. Số slide theo nguồn, không giới hạn ý.')
        print('NEXT: lưu plan.json rồi chạy: ' + command('resume', work))
        return
    note = fix_plan(work)
    if note: print('TỰ SỬA: ' + note)
    outline = load(plan).get('outline', [])
    if not outline or not all(isinstance(x, str) and x.strip() for x in outline):
        raise SystemExit('LỖI: plan.json cần outline là danh sách tiêu đề slide không rỗng.')
    if (work / 'parts' / '00.json').exists():
        raise SystemExit('LỖI: parts bắt đầu từ 01.json (bìa), không phải 00.json. Đánh lại số các phần theo outline; không bỏ mất bìa.')
    inventory_errors = part_inventory_errors(work, outline)
    if inventory_errors:
        raise SystemExit('LỖI CẤU TRÚC PARTS:\n- ' + '\n- '.join(inventory_errors))
    missing = []
    for index, title in enumerate(outline, 1):
        path = work / 'parts' / f'{index:02d}.json'
        if not path.exists():
            missing.append((path, title))
            continue
        data = load(path)
        if not isinstance(data, dict) or not data.get('mau') or not data.get('tieuDe'):
            raise SystemExit(f'LỖI: {path} phải là object slide có "mau" (tên 1 trong 12 mẫu) và "tieuDe".')
    if missing:
        batch = missing[:6]
        print(f'GHI NGAY LÔ {len(batch)} SLIDE SAU:')
        for path, title in batch:
            print(f'- {local(path)}\n  Tiêu đề dự kiến: {title}')
        print('Mỗi file là một object theo 1 trong 12 mẫu của references/huong-dan-k7.md mục 5, có "mau" và "tieuDe"; không bọc trong slides[].')
        print('Ghi các file của lô bằng công cụ write (nhiều lệnh write trong CÙNG MỘT bước), KHÔNG dùng shell/python/heredoc để ghi tệp; muốn kiểm thì chạy advance. Chữ: ' + ('song ngữ {"vi","en"}.' if state.get('song_ngu') else 'chỉ tiếng Việt, chuỗi thường, không viết loiThoai (driver tự tổng hợp).') + ' Tên icon chỉ lấy trong danh sách mục 6 (sai tên driver tự đổi icon gần nghĩa nhất).')
        print('Đọc lại notes.md; chỉ mở lại đoạn nguồn cần cho lô này.')
        print('Ghi xong CẢ LÔ rồi chạy NGAY TRONG CÙNG LƯỢT: ' + command('resume', work))
        print('KHÔNG DỪNG ĐỂ TRẢ LỜI NGƯỜI DÙNG khi phase chưa complete.')
        return
    print('ĐÃ ĐỦ PHẦN. NEXT: ' + command('build', work))
    print('Chạy build NGAY TRONG CÙNG LƯỢT; không dừng để báo tiến độ.')

def start(a):
    work = workpath(a.work)
    if (work / 'iwork-state.json').exists():
        previous = load(work / 'iwork-state.json')
        files = [str(workpath(f)) for f in a.files]
        if previous['files'] != files: raise SystemExit('WORK đã thuộc nguồn khác; chọn thư mục kết quả mới.')
        if a.logo or a.chan_trang is not None:
            # Gắn/đổi logo sau khi đã làm: giữ nguyên nội dung, chỉ build lại.
            logo = workpath(a.logo) if a.logo else None
            if logo and (not logo.is_file() or logo.suffix.lower() not in LOGO_TYPES):
                raise SystemExit('Logo phải là tệp ảnh ' + '/'.join(sorted(LOGO_TYPES)) + ': ' + str(logo))
            scratch = work / '_work'
            if scratch.is_dir():   # đã finish: đưa lại các tệp cần cho build ra gốc WORK
                for item in list(scratch.iterdir()):
                    if not (work / item.name).exists(): shutil.move(str(item), str(work / item.name))
            if logo:
                (work / 'sources').mkdir(exist_ok=True)
                kept = work / 'sources' / ('logo' + logo.suffix.lower()); shutil.copy2(logo, kept); previous['logo'] = str(kept)
            if a.chan_trang is not None:
                previous['chan_trang'] = a.chan_trang
            previous.update(phase='authoring', failed_builds=0)
            for key in ('failed_authored_sha256', 'authored_sha256'): previous.pop(key, None)
            write_json(work / 'iwork-state.json', previous)
            print('ĐÃ CẬP NHẬT LOGO/CHÂN TRANG. Nội dung giữ nguyên; chạy lại để build, kiểm chất lượng và finish: ' + command('advance', work))
            return
        resume(work); return
    if not work.is_relative_to(Path.cwd().resolve()):raise SystemExit(f'WORK phải nằm trong workspace hiện tại {Path.cwd()}; dùng thư mục con tương đối mới, không đoán thư mục cạnh input.')
    files = [str(workpath(f)) for f in a.files]
    for f in files:
        if not Path(f).is_file(): raise SystemExit('Không thấy input: ' + f)
    logo = workpath(a.logo) if a.logo else None
    if logo and (not logo.is_file() or logo.suffix.lower() not in LOGO_TYPES):
        raise SystemExit('Logo phải là tệp ảnh ' + '/'.join(sorted(LOGO_TYPES)) + ': ' + str(logo))
    doctor(files)
    work.mkdir(parents=True, exist_ok=True)
    (work / 'parts').mkdir(exist_ok=True)
    args = ['extract', *files, '--work', str(work)]
    if a.date: args += ['--date', a.date]
    run(*args)
    # Prefer the explicit date or date at the beginning of source, not an arbitrary deadline.
    date = a.date
    if not date:
        head = (work / 'content.md').read_text(encoding='utf-8')[:1600]
        match = re.search(r'(?<!\d)(\d{1,2}/\d{1,2}/20\d{2})(?!\d)', head)
        date = match.group(1) if match else datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
    # Recompute facts against source report date when available.
    result = subprocess.run([sys.executable, str(ROOT/'scripts/facts.py'), str(work), date, *files], capture_output=True, text=True)
    if result.returncode: raise SystemExit(result.stderr or result.stdout)
    state = {'files': files, 'date': date, 'source_hashes':{f:sha(f) for f in files}, 'author_override':getattr(a,'author',None),
             'giao_dien': a.giao_dien, 'song_ngu': bool(a.song_ngu)}
    if logo:
        (work / 'sources').mkdir(exist_ok=True)
        kept = work / 'sources' / ('logo' + logo.suffix.lower()); shutil.copy2(logo, kept)
        state['logo'] = str(kept)
    if a.chan_trang is not None:
        state['chan_trang'] = a.chan_trang
    write_json(work / 'iwork-state.json', state)
    print(f'GIAO DIỆN: {a.giao_dien}' + (' · logo: ' + logo.name if logo else '') + ' (driver tự gắn; không khai nhanDien trong plan.json).')
    print('NGÀY GỢI Ý TỪ ĐẦU NGUỒN: ' + date + ' (đối chiếu tiêu đề nguồn trước khi dùng).')
    print('NGÔN NGỮ: ' + ('song ngữ Việt–Anh, mọi ô chữ viết {"vi":…,"en":…}, nên có loiThoai.' if state['song_ngu'] else 'CHỈ TIẾNG VIỆT: mọi ô chữ là chuỗi thường, KHÔNG viết bản en. KHÔNG viết loiThoai: driver tự tổng hợp lời thoại từ chữ trên slide.'))
    resume(work)

def add_coverage_slides(work, unmet):
    """Bảng theo dõi nhiều dòng mà slide chưa nêu hết mã dòng: driver tự dựng slide phụ lục từ chính các dòng nguồn
    (mã dòng, đơn vị, kết quả, hạn), thay vì bắt model tự quyết dồn bao nhiêu dòng vào slide nào (cách đó làm model lặp suy nghĩ)."""
    rows = [r for r in unmet if r.get('kind') == 'row']
    if len(rows) < 2 or not (work / 'plan.json').is_file(): return None
    plan = load(work / 'plan.json'); outline = list(plan.get('outline', []))
    paths = [work / 'parts' / f'{i:02d}.json' for i in range(1, len(outline) + 1)]
    if not outline or not all(p.is_file() for p in paths): return None
    def cut(text, n):
        text = re.sub(r'\s+', ' ', str(text or '')).strip()
        return text if len(text) <= n else text[:n - 1].rsplit(' ', 1)[0].rstrip(' ,;:/') + '…'
    count = -(-len(rows) // 5)
    size, extra = divmod(len(rows), count)       # chia đều, mỗi slide 2–5 hàng
    slides, start = [], 0
    for k in range(count):
        take = size + (1 if k < extra else 0); chunk = rows[start:start + take]; start += take
        slides.append({'mau': 'bang', 'nhan': 'Phụ lục', 'dauMuc': 'Phụ lục', 'tieuDe': f'Phụ lục: hạng mục theo dõi ({k + 1}/{count})',
                       'phu': 'Các hạng mục còn lại, giữ nguyên mã dòng, đơn vị, kết quả và hạn theo nguồn.',
                       'cot': ['Mã', 'Đơn vị', 'Kết quả', 'Hạn'],
                       'hang': [[cut(r['row'], 16), cut(r.get('unit'), 80), cut(r.get('result') or '—', 80), cut(r.get('due') or '—', 80)] for r in chunk]})
    existing = [load(p) for p in paths]
    at = len(existing) - 1 if existing and isinstance(existing[-1], dict) and existing[-1].get('mau') == 'cam-on' else len(existing)
    merged = existing[:at] + slides + existing[at:]
    titles = outline[:at] + [s['tieuDe'] for s in slides] + outline[at:]
    for i, slide in enumerate(merged, 1): write_json(work / 'parts' / f'{i:02d}.json', slide)
    plan['outline'] = titles; write_json(work / 'plan.json', plan)
    return f'thêm {count} slide phụ lục cho {len(rows)} dòng theo dõi chưa được nêu (dựng từ nguồn, không cần model viết)'

def reopen_if_needed(work, state):
    """Sau HOÀN TẤT người dùng báo lỗi (trang trắng, tràn chữ) hoặc parts đã được sửa: kiểm lại đầu ra thật và dựng lại khi cần,
    để agent không phải tự soi HTML bằng python -c (hộp xin quyền, lạc hướng). True = đã mở lại để dựng."""
    scratch = work / '_work'
    if scratch.is_dir():
        for item in list(scratch.iterdir()):
            if not (work / item.name).exists(): shutil.move(str(item), str(work / item.name))
    reason = None
    if not (work / 'plan.json').is_file() or not (work / 'report.json').is_file():
        reason = None
    elif state.get('authored_sha256') != authored_hash(work):
        reason = 'parts/plan đã đổi sau khi hoàn tất'
    else:
        try:
            name = load(work / 'report.json')['meta']['output_name']
            html, pdf = work / (name + '.html'), work / (name + '.pdf')
            if not html.is_file() or not pdf.is_file():
                reason = 'thiếu tệp đầu ra'
            else:
                from export_pdf import find_browser
                from k7_build import check_overflow_k7
                browser = find_browser()
                if browser:
                    _, err = check_overflow_k7(browser, html)
                    empty = getattr(check_overflow_k7, 'empty', [])
                    if not err and empty: reason = f'slide {empty[0]} trở đi bị TRẮNG'
        except (SystemExit, KeyError, OSError): reason = None
    if reason:
        print(f'KIỂM LẠI ĐẦU RA: {reason}. Driver mở lại để sửa lỗi cơ học và dựng lại.')
        state.update(phase='authoring', failed_builds=0); state.pop('failed_authored_sha256', None); state.pop('auto_cover', None)
        write_json(work / 'iwork-state.json', state)
        (work / 'delivery.json').unlink(missing_ok=True)
        return True
    keep = {'iwork-state.json', 'delivery.json', '.iwork-state.sha256'}
    if (work / 'report.json').is_file():
        name = load(work / 'report.json')['meta']['output_name']
        keep |= {name + ext for ext in ('.html', '.pdf', '.docx')}
        tidy_workspace(work, keep)
    return False

def settle_quality(work, a):
    """Driver tự lập audit từ bằng chứng đã kiểm rồi finish; model chỉ được giao phần bao phủ không tự đáp ứng được."""
    audit, unmet = auto_audit(work)
    state = load(work / 'iwork-state.json')
    if unmet and not state.get('auto_cover'):
        note = add_coverage_slides(work, unmet)
        if note:
            plan = load(work / 'plan.json')
            import importlib.util as _u
            rules = json.loads((ROOT / 'k7' / state.get('giao_dien', DEFAULT_THEME) / 'khung' / 'quy-tac-mau.json').read_text(encoding='utf-8'))
            label = ', '.join(Path(f).name for f in state.get('files', []))
            autofix_parts(work, plan['outline'], set(rules.get('icon', [])), label, state.get('date', ''))
            state['auto_cover'] = True; write_json(work / 'iwork-state.json', state)
            print('TỰ SỬA: ' + note + '. Dựng lại ngay.')
            build(a); return
    quality_task(work, command('finish', work), unmet)
    if unmet:
        print('BUILD ĐẠT nhưng còn ' + str(len(unmet)) + ' yêu cầu bao phủ chưa thấy trong slide. Đọc ' + str(local(work / 'TASK.md')) + ', sửa parts rồi chạy: ' + command('advance', work))
        return
    write_json(work / 'quality-audit.json', audit)
    finish(a)

def build(a):
    work = workpath(a.work); verify_state(work); state = load(work / 'iwork-state.json'); plan = load(work / 'plan.json')
    failed_builds = state.get('failed_builds', 0)
    if failed_builds >= MAX_FAILED_BUILDS:
        raise SystemExit(f'DỪNG: đã build lỗi {failed_builds} lần liên tiếp. Báo người dùng bản nháp và {work / "build.log"}; không tự thử tiếp hoặc tuyên bố hoàn tất.')
    digest = authored_hash(work)
    if state.get('failed_authored_sha256') == digest:
        raise SystemExit('REPAIR_REQUIRED: Nội dung chưa đổi sau build lỗi; sửa đúng trường trong job-step.json/build.log rồi advance. Log không phải cache.')

    def fail(message):
        """Lỗi kiểm trước render cũng tính là một lần build lỗi, để không lặp vô hạn."""
        state.update(failed_authored_sha256=digest, failed_builds=failed_builds + 1)
        write_json(work / 'iwork-state.json', state)
        left = MAX_FAILED_BUILDS - failed_builds - 1
        raise SystemExit(message + (f'\nCòn {left} lần build trước khi phải dừng.' if left > 0 else '\nĐã hết lượt build: dừng và báo người dùng.'))

    if (work / 'parts' / '00.json').exists():
        fail('LỖI: parts bắt đầu từ 01.json (bìa). Sửa số phần theo outline trước khi build; không bỏ mất bìa 00.json.')
    if not (work / 'content.md').is_file() or not (work / 'facts.md').is_file():
        raise SystemExit('Thiếu content.md/facts.md; không được build khi mất dữ liệu nguồn.')
    outline = plan.get('outline', [])
    if not outline: fail('Thiếu outline trong plan.json')
    inventory_errors = part_inventory_errors(work, outline)
    if inventory_errors: fail('LỖI CẤU TRÚC PARTS:\n- ' + '\n- '.join(inventory_errors))
    missing = [f'{i:02d}.json' for i in range(1, len(outline)+1) if not (work/'parts'/f'{i:02d}.json').is_file()]
    if missing: fail('Thiếu parts theo outline: ' + ', '.join(missing) + '. Chạy resume và hoàn thành toàn bộ lô trước khi build.')
    slides = [load(work / 'parts' / f'{i:02d}.json') for i in range(1, len(outline)+1)]
    if not state.get('song_ngu'):      # lời thoại gợi ý dựng từ chữ trên slide, ghi vào report.json (không ghi vào parts nên không lệch khi sửa slide)
        for slide in slides:
            if isinstance(slide, dict) and not _vi(slide.get('loiThoai')).strip(): slide['loiThoai'] = compose_loi_thoai(slide)
    content_text = (work / 'content.md').read_text(encoding='utf-8') if (work / 'content.md').exists() else ''
    narrative_errors = story_errors(slides, plan, content_text)
    if narrative_errors:
        fail('LỖI CẤU TRÚC BÁO CÁO:\n- ' + '\n- '.join(narrative_errors))
    meta = dict(plan.get('meta', {}))
    computed = fact_computations(work)
    for item in meta.get('computed', []):
        if item not in computed: computed.append(item)
    meta['computed'] = computed
    meta.setdefault('date', state['date']);meta.setdefault('output_name', work.name)
    meta.setdefault('id', re.sub(r'[^a-z0-9-]+', '-', work.name.lower()))
    if not meta.get('ten'): fail('LỖI: plan.json thiếu meta.ten (vd {"vi":"…","en":"…"}) - viết lại plan.json trước khi build.')
    meta['output_name'] = re.sub(r'[^\w.-]+', '_', meta['output_name'], flags=re.UNICODE)
    meta['sources'] = [Path(f).name for f in state['files']]
    rep = {'meta': meta, 'slides': slides}
    rep['theme'] = state.get('giao_dien', DEFAULT_THEME)
    identity = identity_meta(state)
    if identity and not meta.get('nhanDien'):
        meta['nhanDien'] = identity
    errors=identity_errors(rep,(work/'content.md').read_text(),state.get('author_override',''))
    if errors: fail('LỖI NGUỒN GỐC: '+'; '.join(errors))
    for src_path, src_digest in state.get('source_hashes', {}).items():
        if not Path(src_path).is_file() or sha(src_path) != src_digest: raise SystemExit('Nguồn đã thay đổi; tạo lượt mới, không dùng facts cũ.')
    state['phase']='building';write_json(work/'iwork-state.json',state)
    write_json(work / 'report.json', rep)
    result = subprocess.run([sys.executable, str(ENGINE), 'build', str(work)], capture_output=True, text=True,
                            env={**os.environ, 'REPORT_WORKFLOW_DRIVER': '1', 'REPORT_SONG_NGU': '1' if state.get('song_ngu') else '0'})
    raw_log = result.stdout + result.stderr
    # Keep engine evidence, but route the native agent back to parts/plan only.
    log = '\n'.join(line for line in raw_log.splitlines() if not line.startswith('NEXT:'))
    if result.returncode:
        log += f'\nNEXT: Sửa parts/NN.json hoặc plan.json; không sửa report.json. Chạy: {command("build", work)}\n'
    else:
        log += '\nNEXT: Xem ảnh _preview, đối chiếu nguồn rồi trả HTML/PDF. Chỉ build lại nếu sửa parts/plan.\n'
    if (work / 'build.log').exists():
        archive = work / 'build-history'; archive.mkdir(exist_ok=True)
        shutil.copy2(work / 'build.log', archive / f'{len(list(archive.glob("*.log")))+1:03}.log')
    (work / 'build.log').write_text(log, encoding='utf-8')
    (work / 'STATUS.md').write_text(f'# iWork\nKết quả: {"CẦN SỬA" if result.returncode else "BUILD ĐẠT; CẦN XEM PREVIEW"}\nSửa parts/NN.json hoặc plan.json, không sửa report.json.\nTiếp tục: {command("build", work)}\n', encoding='utf-8')
    # The log is durable; don't fill the model context with every unused source number.
    lines = log.splitlines()
    for i,line in enumerate(lines):
        if line.startswith(('[1]', '[3]', '[3b]', '[3d]', '[3e]', '[3f]', '[3g]', '[4]', '[5]', 'KẾT QUẢ:')):
            print(line)
            if 'LỖI' in line: print('\n'.join(lines[i+1:i+36]))
    if result.returncode:
        failed_builds += 1
        state.update(failed_authored_sha256=digest, failed_builds=failed_builds)
        write_json(work/'iwork-state.json', state)
        left = MAX_FAILED_BUILDS - failed_builds
        print(f'Chi tiết: {work / "build.log"}. Sửa đúng parts/NN.json hoặc plan.json rồi chạy: {command("build", work)}'
              + (f' Còn {left} lần build trước khi phải dừng.' if left > 0 else ' Đã hết lượt build: dừng và báo người dùng.'))
        raise SystemExit(result.returncode)
    outputs = [work / (meta['output_name'] + suffix) for suffix in ('.html', '.pdf')]
    for output in outputs:
        if not output.is_file() or output.stat().st_size == 0 or output.stat().st_mtime_ns < (work/'report.json').stat().st_mtime_ns:
            raise SystemExit(f'CHƯA HOÀN THÀNH: thiếu đầu ra mới {output}. Xem build.log; không trả file cũ.')
    if not outputs[1].read_bytes().startswith(b'%PDF-'):
        raise SystemExit('CHƯA HOÀN THÀNH: đầu ra PDF không hợp lệ.')
    print(f'ĐẦU RA: {outputs[0]}\nPDF: {outputs[1]}')
    state.pop('failed_authored_sha256', None)
    state.update(phase='quality',report_sha256=sha(work/'report.json'),authored_sha256=authored_hash(work),failed_builds=0);write_json(work/'iwork-state.json',state)
    settle_quality(work, a)

def tidy_workspace(work, keep_names):
    """Move every pipeline scaffolding file/folder into work/_work, leaving only the final deliverables (and the small state files needed to resume/report status) visible at the top level."""
    scratch = work / '_work'
    scratch.mkdir(exist_ok=True)
    for item in list(work.iterdir()):
        if item.name in keep_names or item == scratch: continue
        dest = scratch / item.name
        if dest.exists(): shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(item), str(dest))

def plan_notes(work):
    """Các điểm cần xác nhận (meta.canXacNhan) của plan, kể cả do driver ghi, để đưa vào delivery.json."""
    try: return [str(x) for x in (json.loads((work / 'plan.json').read_text(encoding='utf-8')).get('meta', {}).get('canXacNhan') or [])]
    except (OSError, ValueError, AttributeError): return []

def finish(a):
    work=workpath(a.work);verify_state(work);state=load(work/'iwork-state.json');audit=load(work/'quality-audit.json')
    if state.get('authored_sha256')!=authored_hash(work):raise SystemExit('Parts/plan đã đổi sau build; chạy lại '+command('advance',work)+' trước finish.')
    errors=check_audit(work,audit)
    if errors:raise SystemExit('CHƯA ĐẠT:\n- '+'\n- '.join(errors))
    report=load(work/'report.json');name=report['meta']['output_name']
    outputs=[work/(name+ext) for ext in ('.html','.pdf')]
    if any(not p.exists() or p.stat().st_mtime_ns<(work/'report.json').stat().st_mtime_ns for p in outputs):raise SystemExit('Đầu ra thiếu hoặc cũ; chạy lại '+command('advance',work)+' trước finish.')
    state.update(phase='complete',report_sha256=sha(work/'report.json'));write_json(work/'iwork-state.json',state)
    content=(work/'content.md').read_text(encoding='utf-8') if (work/'content.md').exists() else ''
    write_json(work/'delivery.json',{'state':'complete','slides':len(report['slides']),'outputs':[str(local(p)) for p in outputs],'audit':str(local(work/'quality-audit.json')),'uncertainties':list(audit.get('uncertainties',[]))+plan_notes(work)+([] if state.get('song_ngu') else ['Lời thoại do driver tự tổng hợp từ chữ trên slide (không thêm thông tin ngoài slide); nên đọc lại và chỉnh trước khi trình bày.']),'doi_chieu_so':number_evidence(report,content)})
    (work/'STATUS.md').write_text('# HOÀN TẤT\n'+str(work/'delivery.json')+'\n')
    docx = work / (name + '.docx')
    keep = {p.name for p in outputs} | {'iwork-state.json', 'delivery.json'} | ({docx.name} if docx.exists() else set())
    tidy_workspace(work, keep)
    print('HOÀN TẤT: '+str(local(work/'delivery.json')))
    print('TỆP: ' + ' · '.join(str(local(p)) for p in outputs) + '  (trích dẫn cho người dùng bằng đường dẫn tương đối này)')
    print(IVIEW_NOTICE)
    print(f'SAU KHI XONG, nếu người dùng báo lỗi tệp (trang trắng, tràn chữ, sai số) hoặc muốn sửa chữ: KHÔNG tự soi HTML bằng python -c/grep/cat. Sửa parts bằng công cụ edit (nếu cần) rồi chạy python3 "{local(work/"_work"/"advance.py")}": driver tự kiểm đầu ra thật và dựng lại.')

def advance(a):
    """Checkpoint each batch; never render structurally invalid parts."""
    work = workpath(a.work)
    verify_state(work)
    state = load(work/'iwork-state.json')
    step = {'phase': state.get('phase', 'authoring'), 'authored_sha256': authored_hash(work), 'errors': []}
    if str(state.get('phase', '')).startswith('complete'):
        if not reopen_if_needed(work, state):
            resume(work)
            return
        state = load(work/'iwork-state.json')
        step['phase'] = state.get('phase', 'authoring'); step['authored_sha256'] = authored_hash(work)
    if not (work/'plan.json').exists():
        resume(work)
        return
    note = fix_plan(work) or extend_outline(work)
    if note: print('TỰ SỬA: ' + note)
    note = split_long_tables(work)
    if note: print('TỰ SỬA: ' + note)
    note = add_missing_chapters(work)
    if note: print('TỰ SỬA: ' + note)
    note = sync_toc_with_chapters(work)
    if note: print('TỰ SỬA: ' + note)
    plan = load(work/'plan.json')
    outline = plan.get('outline', [])
    if not isinstance(outline, list) or not outline:
        raise SystemExit('plan.outline phải là danh sách không rỗng.')
    step['errors'].extend(part_inventory_errors(work, outline))
    spec = importlib.util.spec_from_file_location('k7_preflight', ROOT/'k7'/state.get('giao_dien', DEFAULT_THEME)/'cong-cu/kiem-slide.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    label = ', '.join(Path(f).name for f in state.get('files', [])) + (f' ({state["date"]})' if state.get('date') else '')
    fixes = autofix_parts(work, outline, set(checker.ICON), label, state.get('date', ''))
    if fixes:
        print('TỰ SỬA (lỗi cơ học, không đổi nội dung):\n  · ' + '\n  · '.join(fixes[:15]) + ('\n  · …' if len(fixes) > 15 else ''))
        step['authored_sha256'] = authored_hash(work)
    paths = sorted((work/'parts').glob('*.json'))
    for path in paths:
        slide = load(path)
        if not isinstance(slide, dict):
            step['errors'].append({'file': str(path), 'code': 'C1', 'message': 'Slide phải là object.'})
            continue
        for issue in soften(checker.kiem({'meta': plan.get('meta', {}), 'slides': [slide]})):
            if issue['muc'] == 'loi':
                step['errors'].append({'file': str(local(path)), **length_hint(slide, issue)})
        for message in unknown_key_errors(slide):
            step['errors'].append({'file': str(local(path)), 'muc': 'loi', 'ma': 'M11', 'vi_tri': path.stem, 'y': message})
        if slide.get('mau') in ('anh', 'hinh-so'):
            image = slide.get('anh')
            if not isinstance(image, dict) or not image.get('src'):
                step['errors'].append({'file': str(path), 'code': 'IMAGE_SCHEMA', 'message': 'anh phải là object có src và alt; không dùng chuỗi.'})
    if step['errors']:
        step.update(status='repairable_error', action='Sửa đúng file/trường lỗi rồi gọi advance; không hỏi người dùng.')
        write_json(work/'job-step.json', step)
        (work/'STATUS.md').write_text(
            '# iWork — cần tự sửa\n'
            'Đọc job-step.json, sửa đúng file/trường được liệt kê; không hỏi người dùng.\n'
            f'Tiếp tục: {command("advance", work)}\n',
            encoding='utf-8',
        )
        print(json.dumps(step, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    missing = [i for i in range(1, len(outline)+1) if not (work/'parts'/f'{i:02d}.json').exists()]
    if missing:
        step.update(status='authoring', missing=missing[:6], action='Ghi toàn bộ lô còn thiếu (tối đa 6 slide) rồi advance; không hỏi người dùng.')
        write_json(work/'job-step.json', step)
        resume(work)
        return
    try:
        if state.get('phase') == 'quality' and state.get('authored_sha256') == authored_hash(work):
            resume(work)
            step.update(status='quality', action='Đối chiếu nguồn/preview, ghi audit rồi finish.')
        else:
            build(a)
            step.update(status='quality', action='Đối chiếu nguồn/preview, ghi audit rồi finish.')
    except SystemExit as error:
        message = error.code if isinstance(error.code, str) else ''
        blocked = message.startswith('DỪNG') or load(work/'iwork-state.json').get('failed_builds', 0) >= MAX_FAILED_BUILDS
        step.update(status='blocked' if blocked else 'repairable_error',
                    action=('Hết lượt sửa: không build tiếp; driver giao bản nháp mới nhất kèm cảnh báo.' if blocked
                            else 'Sửa đúng các lỗi dưới đây trong parts/plan rồi advance; không hỏi người dùng.'),
                    errors=[message] if message else build_log_errors(work), log=str(work / 'build.log'))
        write_json(work/'job-step.json', step)
        print(json.dumps({k: step[k] for k in ('status', 'action', 'errors', 'log')}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    if str(load(work/'iwork-state.json').get('phase','')).startswith('complete'):
        return   # đã giao và dọn WORK: không để job-step.json lại ở gốc
    write_json(work/'job-step.json', step)

def build_log_errors(work, limit=40):
    """Các dòng LỖI trong build.log cùng chi tiết thụt lề ngay sau đó, để job-step.json tự đủ thông tin."""
    path = work / 'build.log'
    if not path.exists():
        return ['Build lỗi nhưng không có build.log.']
    out, keep = [], False
    for line in path.read_text(encoding='utf-8').splitlines():
        if 'LỖI' in line:
            keep = True; out.append(line.strip())
        elif keep and line.startswith((' ', '\t')) and line.strip():
            out.append(line.strip())
        else:
            keep = False
        if len(out) >= limit:
            out.append('… xem thêm trong build.log'); break
    return out or ['Build lỗi; xem build.log.']

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action', required=True)
    q=sub.add_parser('start'); q.add_argument('files',nargs='+');q.add_argument('--work',required=True);q.add_argument('--date');q.add_argument('--author',help='Chỉ khi người dùng cung cấp rõ tác giả/đơn vị')
    q.add_argument('--giao-dien', dest='giao_dien', choices=THEMES, default=DEFAULT_THEME,
                   help='Giao diện có trong skill này (k7/); mặc định ' + DEFAULT_THEME)
    q.add_argument('--song-ngu', dest='song_ngu', action='store_true', help='Viết cả bản tiếng Anh và lời thoại (mặc định chỉ tiếng Việt, nhanh hơn một nửa)')
    q.add_argument('--logo', help='Tệp ảnh logo người dùng đưa (PNG/JPG/SVG/WEBP); driver tự gắn vào mọi slide')
    q.add_argument('--chan-trang', dest='chan_trang', help='Chữ chân trang thay mặc định (vd "VNPT · Nội bộ")')
    q.set_defaults(fn=start)
    q=sub.add_parser('resume');q.add_argument('work');q.set_defaults(fn=lambda a:resume(workpath(a.work)))
    q=sub.add_parser('build');q.add_argument('work');q.set_defaults(fn=build)
    q=sub.add_parser('finish');q.add_argument('work');q.set_defaults(fn=finish)
    q=sub.add_parser('advance');q.add_argument('work');q.set_defaults(fn=advance)
    a=p.parse_args()
    code = 0
    try:
        a.fn(a)
    except SystemExit as error:
        code = error.code
        if isinstance(code, str):
            print(code); code = 1
    footer(workpath(a.work))
    raise SystemExit(code or 0)
if __name__=='__main__': main()
