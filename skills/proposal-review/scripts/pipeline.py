#!/usr/bin/env python3
"""Các bước tất định dùng chung cho driver iwork.py: chạy review.py, render ảnh trang, kiểm đầu ra.

Không gọi model hay API nào: nội dung review do model mặc định của phiên iWork viết theo TASK.md.
"""
import copy, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault('PYTHONUTF8', '1'); os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
try: VN_TZ = ZoneInfo('Asia/Ho_Chi_Minh')
except Exception: VN_TZ = datetime.timezone(datetime.timedelta(hours=7))   # Windows thiếu tzdata: Việt Nam không có giờ mùa hè nên UTC+7 là chính xác

S = Path(__file__).resolve().parent.parent
TODAY = datetime.datetime.now(VN_TZ).date().isoformat()


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, obj): Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf8')


def skill_hashes():
    return {str(p.relative_to(S)):sha(p) for p in sorted(S.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='.DS_Store'}


def audit_output(run,src,wd,manifest):
    from bs4 import BeautifulSoup
    output=run/('Danh_gia_'+src.stem+'.html');doc=BeautifulSoup(output.read_text(),'html.parser');final=json.loads((wd/'final.json').read_text())
    norm=lambda text:re.sub(r'\s+',' ',text).strip()
    lines=0
    for n,line in enumerate((wd/'answer.md').read_text().splitlines(),1):
        if not line.strip() or line.startswith('#'):continue
        expected=re.sub(r'\*\*(.+?)\*\*',r'\1',line[2:] if line.startswith('- ') else line)
        element=doc.select_one(f'[data-source-line="{n}"]')
        if element is None:raise ValueError(f'Missing review line {n}')
        element=copy.deepcopy(element)
        for child in list(element.select('[data-source-line]')):child.decompose()
        text=element.get_text('',strip=False)
        if re.match(r'\d+\.\s',expected):text=re.sub(r'^(\d+\.)(?=\S)',r'\1 ',text)
        if norm(text)!=norm(expected):raise ValueError(f'Changed review line {n}')
        lines+=1
    checks={'twelve_sections':len(doc.select('main>section'))==12,'eight_criteria':len(doc.select('.crit-row'))==8,'all_pages':len(doc.select('#tung-slide tbody tr'))==manifest['page_count'],'all_images':len(doc.select('#tung-slide img'))==manifest['page_count'],'all_final_issues':len(doc.select('article.issue'))==len(final['issues']),'all_actions':len(doc.select('#hanh-dong tbody tr'))==len(final['issues']),'one_checked_decision':len(doc.select('.decision-scale input[checked]'))==1,'editable_feedback':bool(doc.select_one('#msg > p[contenteditable=true]')),'editable_confirmation':len(doc.select('#xac-nhan .lines[contenteditable=true]'))==2,'compact_footer':doc.select_one('footer.foot').get_text()=='Đánh giá bằng Coding Assistant.'}
    result={'checks':checks,'content_lines_preserved':lines,'output_sha256':sha(output),'source_sha256':sha(src),'all_pass':all(checks.values())};save(run/'output-audit.json',result)
    if not result['all_pass']:raise ValueError('Output audit failed: '+str(checks))
    return result


def tool(run,src,cmd):
    env={**os.environ,'IWORK_DRIVER':'1'}
    p=subprocess.run([sys.executable,str(S/'scripts/review.py'),cmd,str(src)]+(['--today',TODAY] if cmd=='prepare' else []),capture_output=True,text=True, encoding='utf-8', errors='replace',timeout=90,env=env)
    # Bỏ dòng 'NEXT: ... review.py <lệnh> <đường dẫn>' của công cụ: agent hay chép lệnh đó (đường dẫn tuyệt đối, không ngoặc kép) và bị iWork hỏi quyền. Lệnh đúng luôn là next_command của driver.
    shown='\n'.join(l for l in p.stdout.splitlines() if not l.startswith('NEXT:'))
    (run/(cmd+'.log')).write_text(shown+'\n'+p.stderr)
    if p.returncode:
        # Lấy trọn thông báo lỗi (dòng ValueError/LỖI cuối), không cắt cụt: agent cần thấy đủ mọi mục phải sửa.
        lines=[l for l in (p.stderr+'\n'+p.stdout).splitlines() if l.strip()]
        msg=next((l.split(':',1)[1].strip() for l in reversed(lines) if re.match(r'(ValueError|RuntimeError|KeyError|SystemExit):',l)),None)
        msg=msg or next((l for l in reversed(lines) if l.startswith('LỖI')),None) or '\n'.join(lines[-15:])
        raise RuntimeError(cmd+': '+msg[:6000])


def render(run,src,wd):
    v=wd/'images';v.mkdir(exist_ok=True)
    if src.suffix=='.pdf':pdf=src
    else:
        with tempfile.TemporaryDirectory(prefix='full-form-render-') as tmp:
            exe=next((c for c in (shutil.which('soffice'),shutil.which('libreoffice'),'/Applications/LibreOffice.app/Contents/MacOS/soffice',r'C:\Program Files\LibreOffice\program\soffice.exe',r'C:\Program Files (x86)\LibreOffice\program\soffice.exe') if c and os.path.exists(c)),None)
            if not exe:raise ValueError('Máy chưa có LibreOffice nên không đọc được PPTX/DOCX. Báo người dùng cài LibreOffice hoặc đính kèm bản PDF của tài liệu; không tự cài.')
            subprocess.run([exe,'-env:UserInstallation='+Path(tmp,'profile').as_uri(),'--headless','--convert-to','pdf','--outdir',tmp,str(src)],check=True,capture_output=True,timeout=120)
            shutil.copyfile(Path(tmp)/(src.stem+'.pdf'),v/'source.pdf')
        pdf=v/'source.pdf'
    pages=[]
    import fitz
    with fitz.open(pdf) as doc:
        for n,p in enumerate(doc,1):
            image=v/f'page-{n:03}.png';p.get_pixmap(matrix=fitz.Matrix(600/p.rect.width,600/p.rect.width)).save(image)
            pages.append({'page':n,'image':str(image.resolve()),'sha256':sha(image)})
    manifest={'source_sha256':sha(src),'page_count':len(pages),'pages':pages};save(v/'manifest.json',manifest);return manifest
