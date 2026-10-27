#!/usr/bin/env python3
"""Stable iWork entry point. Durable slide parts; exact quoted NEXT commands."""
import argparse
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from source_audit import check_audit, task as quality_task, sha, identity_errors
# GUI apps on macOS often inherit a minimal PATH. Only add existing standard bins.
for directory in ('/opt/homebrew/bin', '/usr/local/bin'):
    if Path(directory).is_dir() and directory not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + directory
ENGINE = ROOT / 'scripts' / 'report.py'

def command(*args):
    return shlex.join([sys.executable, str(ROOT / 'iwork.py'), *map(str, args)])

def run(*args):
    result = subprocess.run([sys.executable, str(ENGINE), *map(str, args)], capture_output=True, text=True)
    if result.stdout: print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('NEXT:')), end='\n')
    if result.stderr: print(result.stderr, end='', file=sys.stderr)
    if result.returncode: raise SystemExit(result.returncode)

def write_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)

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
    return Path(value).expanduser().resolve()

def doctor(files):
    required = {'PIL': 'Pillow'}
    extensions = {Path(f).suffix.lower() for f in files}
    if '.xlsx' in extensions: required['openpyxl'] = 'openpyxl'
    if '.docx' in extensions: required['docx'] = 'python-docx'
    if '.pptx' in extensions: required['pptx'] = 'python-pptx'
    if '.pdf' in extensions and not (shutil.which('pdftotext') and shutil.which('pdftoppm')):
        required['fitz'] = 'PyMuPDF'
    missing = [package for module, package in required.items() if importlib.util.find_spec(module) is None]
    if missing:
        raise SystemExit('THIẾU THƯ VIỆN. Chạy: ' + shlex.join([sys.executable, '-m', 'pip', 'install', *missing]))
    if '.pdf' in extensions and not all(shutil.which(x) for x in ('pdftotext', 'pdftoppm', 'pdftocairo')):
        raise SystemExit('THIẾU POPPLER để đọc chính xác bảng PDF. Cài Poppler vào PATH rồi chạy lại. Không bỏ qua bước đọc bảng.')

def authored_hash(work):
    import hashlib
    paths=[work/'plan.json',*sorted((work/'parts').glob('*.json'))]
    return hashlib.sha256(''.join(str(p.relative_to(work))+':'+sha(p) for p in paths if p.exists()).encode()).hexdigest()

def resume(work):
    state = load(work / 'iwork-state.json')
    if state.get('phase')=='complete':
        print('HOÀN TẤT. '+str(work/'delivery.json'));return
    (work / 'STATUS.md').write_text(
        '# iWork — đang soạn báo cáo\n'
        'Entry point duy nhất: iwork.py ở gốc skill, không phải scripts/report.py.\n'
        'Ghi plan.json và từng parts/NN.json theo lệnh resume. Không sửa report.json.\n'
        f'Tiếp tục: {command("resume", work)}\n', encoding='utf-8')
    if state.get('phase')=='quality' and (work/'report.json').exists():
        if state.get('authored_sha256')!=authored_hash(work):
            print('Parts/plan đã đổi. NEXT: '+command('build',work));return
        quality_task(work,command('finish',work));return
    plan = work / 'plan.json'
    if not plan.exists():
        print(f'ĐỌC: {work / "content.md"}\nĐỌC: {work / "facts.md"}\nĐỌC: {ROOT / "references/writing_guide.md"}')
        print(f'GHI {plan}: {{"meta":{{"title":"…","author":"…","date":"…","computed":[]}},"outline":["tên từng slide"]}}. Số slide theo nguồn, không giới hạn ý.')
        print('NEXT: lưu plan.json rồi chạy: ' + command('resume', work))
        return
    outline = load(plan).get('outline', [])
    if not outline or not all(isinstance(x, str) and x.strip() for x in outline):
        raise SystemExit('LỖI: plan.json cần outline là danh sách tiêu đề slide không rỗng.')
    if (work / 'parts' / '00.json').exists():
        raise SystemExit('LỖI: parts bắt đầu từ 01.json (bìa), không phải 00.json. Đánh lại số các phần theo outline; không bỏ mất bìa.')
    for index, title in enumerate(outline, 1):
        path = work / 'parts' / f'{index:02d}.json'
        if not path.exists():
            print(f'GHI MỘT SLIDE NGAY: {path}\nTiêu đề dự kiến: {title}\nCấu trúc: một object slide theo references/schema.md; không bọc trong slides[].')
            print('Không viết lại các slide trước. Lưu xong gọi tiếp: ' + command('resume', work))
            return
        data = load(path)
        if not isinstance(data, dict) or not data.get('title'): raise SystemExit(f'LỖI: {path} phải là object slide có title.')
    print('ĐÃ ĐỦ PHẦN. NEXT: ' + command('build', work))

def start(a):
    work = workpath(a.work)
    if (work / 'iwork-state.json').exists():
        previous = load(work / 'iwork-state.json')
        files = [str(workpath(f)) for f in a.files]
        if previous['files'] != files: raise SystemExit('WORK đã thuộc nguồn khác; chọn thư mục kết quả mới.')
        resume(work); return
    if not work.is_relative_to(Path.cwd().resolve()):raise SystemExit(f'WORK phải nằm trong workspace hiện tại {Path.cwd()}; dùng thư mục con tương đối mới, không đoán thư mục cạnh input.')
    files = [str(workpath(f)) for f in a.files]
    for f in files:
        if not Path(f).is_file(): raise SystemExit('Không thấy input: ' + f)
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
    write_json(work / 'iwork-state.json', {'files': files, 'date': date, 'source_hashes':{f:sha(f) for f in files}, 'author_override':getattr(a,'author',None)})
    print('NGÀY GỢI Ý TỪ ĐẦU NGUỒN: ' + date + ' (đối chiếu tiêu đề nguồn trước khi dùng).')
    resume(work)

def build(a):
    work = workpath(a.work); state = load(work / 'iwork-state.json'); plan = load(work / 'plan.json')
    if (work / 'parts' / '00.json').exists():
        raise SystemExit('LỖI: parts bắt đầu từ 01.json (bìa). Sửa số phần theo outline trước khi build; không bỏ mất bìa 00.json.')
    if not (work / 'content.md').is_file() or not (work / 'facts.md').is_file():
        raise SystemExit('Thiếu content.md/facts.md; không được build khi mất dữ liệu nguồn.')
    outline = plan.get('outline', [])
    if not outline: raise SystemExit('Thiếu outline trong plan.json')
    expected={f'{i:02d}.json' for i in range(1,len(outline)+1)}
    extra={p.name for p in (work/'parts').glob('*.json')}-expected
    if extra:raise SystemExit('Có parts ngoài outline sẽ bị bỏ mất: '+', '.join(sorted(extra))+'. Bổ sung outline đúng nội dung; không âm thầm bỏ slide.')
    slides = [load(work / 'parts' / f'{i:02d}.json') for i in range(1, len(outline)+1)]
    meta = dict(plan.get('meta', {}))
    computed = fact_computations(work)
    for item in meta.get('computed', []):
        if item not in computed: computed.append(item)
    meta['computed'] = computed
    meta.setdefault('date', state['date']);meta.setdefault('output_name', work.name)
    meta['output_name'] = re.sub(r'[^\w.-]+', '_', meta['output_name'], flags=re.UNICODE)
    meta['sources'] = [Path(f).name for f in state['files']]
    rep = {'meta': meta, 'slides': slides}
    if plan.get('theme'): rep['theme'] = plan['theme']
    errors=identity_errors(rep,(work/'content.md').read_text(),state.get('author_override',''))
    if errors:raise SystemExit('LỖI NGUỒN GỐC: '+'; '.join(errors))
    for path,digest in state.get('source_hashes',{}).items():
        if not Path(path).is_file() or sha(path)!=digest:raise SystemExit('Nguồn đã thay đổi; tạo lượt mới, không dùng facts cũ.')
    state['phase']='building';write_json(work/'iwork-state.json',state)
    write_json(work / 'report.json', rep)
    result = subprocess.run([sys.executable, str(ENGINE), 'build', str(work)], capture_output=True, text=True)
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
            if 'LỖI' in line: print('\n'.join(lines[i+1:i+9]))
    if result.returncode:
        print(f'Chi tiết: {work / "build.log"}. Sửa đúng parts/NN.json hoặc plan.json rồi chạy: {command("build", work)}')
        raise SystemExit(result.returncode)
    outputs = [work / (meta['output_name'] + suffix) for suffix in ('.html', '.pdf')]
    for output in outputs:
        if not output.is_file() or output.stat().st_size == 0 or output.stat().st_mtime_ns < (work/'report.json').stat().st_mtime_ns:
            raise SystemExit(f'CHƯA HOÀN THÀNH: thiếu đầu ra mới {output}. Xem build.log; không trả file cũ.')
    if not outputs[1].read_bytes().startswith(b'%PDF-'):
        raise SystemExit('CHƯA HOÀN THÀNH: đầu ra PDF không hợp lệ.')
    print(f'ĐẦU RA: {outputs[0]}\nPDF: {outputs[1]}')
    state.update(phase='quality',report_sha256=sha(work/'report.json'),authored_sha256=authored_hash(work));write_json(work/'iwork-state.json',state)
    quality_task(work,command('finish',work))

def tidy_workspace(work, keep_names):
    """Move every pipeline scaffolding file/folder into work/_work, leaving only the final deliverables (and the small state files needed to resume/report status) visible at the top level."""
    scratch = work / '_work'
    scratch.mkdir(exist_ok=True)
    for item in list(work.iterdir()):
        if item.name in keep_names or item == scratch: continue
        dest = scratch / item.name
        if dest.exists(): shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(item), str(dest))

def finish(a):
    work=workpath(a.work);state=load(work/'iwork-state.json');audit=load(work/'quality-audit.json')
    if state.get('authored_sha256')!=authored_hash(work):raise SystemExit('Parts/plan đã đổi sau build; build lại trước finish.')
    errors=check_audit(work,audit)
    if errors:raise SystemExit('CHƯA ĐẠT:\n- '+'\n- '.join(errors))
    report=load(work/'report.json');name=report['meta']['output_name']
    outputs=[work/(name+ext) for ext in ('.html','.pdf')]
    if any(not p.exists() or p.stat().st_mtime_ns<(work/'report.json').stat().st_mtime_ns for p in outputs):raise SystemExit('Đầu ra thiếu hoặc cũ; build lại trước finish')
    state.update(phase='complete',report_sha256=sha(work/'report.json'));write_json(work/'iwork-state.json',state)
    write_json(work/'delivery.json',{'state':'complete','slides':len(report['slides']),'outputs':list(map(str,outputs)),'audit':str(work/'quality-audit.json'),'uncertainties':audit.get('uncertainties',[])})
    (work/'STATUS.md').write_text('# HOÀN TẤT\n'+str(work/'delivery.json')+'\n')
    docx = work / (name + '.docx')
    keep = {p.name for p in outputs} | {'iwork-state.json', 'delivery.json'} | ({docx.name} if docx.exists() else set())
    tidy_workspace(work, keep)
    print('HOÀN TẤT: '+str(work/'delivery.json'))

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action', required=True)
    q=sub.add_parser('start'); q.add_argument('files',nargs='+');q.add_argument('--work',required=True);q.add_argument('--date');q.add_argument('--author',help='Chỉ khi người dùng cung cấp rõ tác giả/đơn vị');q.set_defaults(fn=start)
    q=sub.add_parser('resume');q.add_argument('work');q.set_defaults(fn=lambda a:resume(workpath(a.work)))
    q=sub.add_parser('build');q.add_argument('work');q.set_defaults(fn=build)
    q=sub.add_parser('finish');q.add_argument('work');q.set_defaults(fn=finish)
    a=p.parse_args();a.fn(a)
if __name__=='__main__': main()
