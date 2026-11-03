#!/usr/bin/env python3
"""Driver từng bước cho phiên iWork. Nội dung do model mặc định của phiên viết; driver không gọi model hay API nào."""
import argparse, datetime, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo
S=Path(__file__).resolve().parent.parent
for directory in ('/opt/homebrew/bin', '/usr/local/bin'):
    if Path(directory).is_dir() and directory not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + directory

def fold(s):
    """Cùng cách chuẩn hoá với review.py để so khớp nguyên văn."""
    s=re.sub(r"[\"“”‘’'`«»]","",unicodedata.normalize("NFC",s or "").lower())
    s=s.replace("…","...").replace("–","-").replace("—","-")
    return re.sub(r"\s+"," ",re.sub(r"\s*\|\s*"," ",s)).strip()

def verbatim_core(m,quote,content,min_words=5,min_chars=25):
    """Đoạn liền mạch dài nhất trong `quote` mà CÓ THẬT nguyên văn trong tài liệu.
    Model hay ghép nhiều ô bảng bằng dấu | hoặc chữa lại câu nên nguyên văn bị REJECT; phần có thật của nó vẫn là bằng chứng hợp lệ,
    nên driver tự cắt về đúng phần đó thay vì bắt model sửa (bước đó là chỗ model hay nghĩ quá dài rồi bị cắt)."""
    folded=fold(content);best=''
    for seg in re.split(r'…|\.\.\.|\|',quote):
        words=seg.split()
        for i in range(len(words)):
            for j in range(len(words),i+min_words-1,-1):
                run=' '.join(words[i:j])
                if len(run)<=len(best):break
                if len(run)>=min_chars and fold(run).strip(' .,;:-') in folded:best=run;break
    return best

def shrink_quotes(m,wd,v,bad):
    """Thay quote của các mục REJECT vì 'không tìm thấy nguyên văn' bằng phần nguyên văn có thật. Trả về số mục đã sửa."""
    path=wd/'candidates.json';c=json.loads(path.read_text());content=(wd/'content.md').read_text(encoding='utf8')
    index={x['id']:i for i,x in enumerate(v['issues'])};done=0;before={}
    for x in bad:
        if not str(x.get('reason','')).startswith('không tìm thấy nguyên văn'):continue
        i=index.get(x['id'])
        if i is None or i>=len(c['issues']):continue
        core=verbatim_core(m,c['issues'][i].get('quote') or '',content)
        if core:before[x['id']]=c['issues'][i]['quote'];c['issues'][i]['quote']=core;done+=1
    if done:save(wd/'quotes-original.json',before);save(path,c)
    return done

def bootstrap():
    """Thiếu thư viện (bs4, PyMuPDF) thì chạy lại chính driver bằng Python trong môi trường riêng ở ~/.cache.
    Mọi việc diễn ra BÊN TRONG driver và im lặng: pip không in gì, đường dẫn môi trường không bao giờ xuất hiện trong kết quả.
    (Thật: pip in đường dẫn môi trường ra, model chép đường dẫn đó vào lệnh của nó, iWork hỏi quyền vì ngoài thư mục làm việc.)"""
    try:
        import bs4, fitz
        return
    except ImportError:
        pass
    if os.environ.get('IWORK_BOOTSTRAPPED') == '1':
        raise SystemExit('LỖI: thiếu thư viện beautifulsoup4 hoặc PyMuPDF và không cài được. Báo người dùng; không tự cài và không gõ đường dẫn Python nào.')
    env = Path.home() / '.cache' / 'proposal-review' / 'python'
    py = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    quiet = dict(capture_output=True, text=True)
    def has_deps():
        return py.exists() and subprocess.run([str(py), '-c', 'import bs4, fitz'], **quiet).returncode == 0
    if not has_deps():
        if not py.exists():
            made = subprocess.run([sys.executable, '-m', 'venv', str(env)], **quiet)
            if made.returncode: raise SystemExit('LỖI: không tạo được môi trường Python cho skill. Báo người dùng.')
        done = subprocess.run([str(py), '-m', 'pip', 'install', '-q', '--disable-pip-version-check', '-r', str(S / 'scripts/requirements.txt')], **quiet)
        if done.returncode or not has_deps():
            tail = ' | '.join((done.stderr or done.stdout or '').strip().splitlines()[-2:]).replace(str(Path.home()), '~')
            raise SystemExit('LỖI: không cài được thư viện beautifulsoup4, PyMuPDF (' + tail[:200] + '). Báo người dùng; không tự cài.')
    # chạy lại bằng Python của môi trường, kế thừa đầu ra; không dùng os.execv vì trên Windows nó trả quyền điều khiển cho shell trước khi tiến trình con xong
    result = subprocess.run([str(py), str(Path(__file__).resolve()), *sys.argv[1:]], env={**os.environ, 'IWORK_BOOTSTRAPPED': '1'})
    raise SystemExit(result.returncode)

def tidy_workspace(w, wd, keep_names):
    """Move pipeline scaffolding into the existing _review/<name> scratch folder, leaving only the final HTML (and session.json, needed to resume/report status) visible at the top level."""
    for item in list(w.iterdir()):
        if item.name in keep_names or wd.resolve().is_relative_to(item.resolve()): continue
        dest=wd/item.name
        if dest.exists(): shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(item),str(dest))

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def helper():
    spec=importlib.util.spec_from_file_location('review_pipeline',S/'scripts/pipeline.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

CRITIQUE_HOWTO=('Phản biện độc lập với người viết: tự đọc toàn bộ {task} và đóng vai người chưa từng thấy candidates, rồi ghi {out}. '
 'Nếu phiên có sub-agent (task/general) và việc giao tốn ít bước thì có thể giao NGUYÊN VĂN {task} cho một sub-agent mới và lưu JSON nó trả về, thêm "_meta": {{"mode": "subagent"}}. '
 'Không có thì thôi: không cần ghi _meta, driver tự ghi same_context và phiếu sẽ nêu hạn chế này.')

RESUME_RULE=('QUY TẮC CỨNG: chưa thấy dòng HOÀN TẤT nghĩa là CHƯA XONG. Không tự viết báo cáo/tóm tắt/tệp kết quả (chỉ driver tạo HTML và PDF), không nói "đã hoàn tất". '
  'Nếu mất ngữ cảnh, không chắc đang ở bước nào, hoặc thấy câu "Continue if you have next steps": chạy lại đúng {nxt} để làm tiếp. Nếu lệnh bị từ chối hoặc báo không tìm thấy tệp: chạy lại ĐÚNG lệnh trên (chép nguyên văn), KHÔNG kết luận driver không tồn tại hoặc skill chạy trong sandbox (driver luôn có trên đĩa), KHÔNG tự xuất báo cáo bằng cách khác. Lệnh LUÔN bắt đầu bằng python/python3 rồi mới tới đường dẫn tệp; không bao giờ chạy một đường dẫn .py đứng một mình (trên Windows sẽ bật hộp "chọn ứng dụng để mở tệp .py").')

def task(w,st,title,body):
    p=w/'TASK.md';p.write_text('# '+title+'\n\n'+body,encoding='utf8');save(w/'session.json',st)
    try:rel=w.resolve().relative_to(Path.cwd().resolve())   # tương đối với workspace: iWork không hỏi quyền
    except ValueError:rel=w
    launcher=w/'next.py'   # driver tự tạo: agent chỉ gõ đường dẫn tương đối trong workspace, không phải nhớ đường dẫn skill
    text=f"import runpy, sys\n# Tệp do driver tạo: chạy lại đúng driver của skill.\nDRIVER = {str(Path(__file__).resolve())!r}\nsys.argv = [DRIVER, 'next', '--work', {str(w.resolve())!r}]\nrunpy.run_path(DRIVER, run_name='__main__')\n"
    if not launcher.is_file() or launcher.read_text(encoding='utf8')!=text:launcher.write_text(text,encoding='utf8')
    exe='python' if os.name=='nt' else 'python3'   # Windows thường không có python3
    # Lệnh TƯƠNG ĐỐI và giống hệt ở mọi phiên (cũng là chuỗi có sẵn trong SKILL.md): model không phải nhớ/chép đường dẫn dài có mã phiên.
    # Đường dẫn tuyệt đối dài từng bị model chép sai (ghép nhầm sang thư mục skill) rồi bị iWork hỏi quyền.
    try: rel_launcher=(w.resolve()/'next.py').relative_to(Path.cwd().resolve()).as_posix()
    except ValueError: rel_launcher=(w.resolve()/'next.py').as_posix()
    nxt=f'{exe} "{rel_launcher}"'
    print(json.dumps({'state':'WAITING_FOR_MODEL','phase':st['phase'],'todo':title,'task':str(p),'next_command':nxt},ensure_ascii=False))
    stray=stray_files(w)
    if stray:print('CẢNH BÁO FILE LẠ ở thư mục kết quả: '+', '.join(stray)+'. Chỉ ghi đúng file TASK.md yêu cầu trong _review/; xoá file thừa.')
    print(f'=== CHƯA XONG (phase={st["phase"]}). Đọc {p}, viết đúng file JSON được yêu cầu rồi chạy ngay: {nxt} . Không trả lời hay hỏi người dùng cho tới khi thấy HOÀN TẤT. ===')
    print('(Chỉ chạy đúng lệnh trên. KHÔNG ls/find/cd/rm/2>/dev/null: iWork sẽ hỏi quyền và dừng chờ. Đọc tệp bằng công cụ read, ghi bằng write/edit.)')
    print(RESUME_RULE.format(nxt=nxt))
    with p.open('a',encoding='utf8') as f: f.write('\n\n'+RESUME_RULE.format(nxt=nxt)+'\n')

ALLOWED={'session.json','status.json','TASK.md','next.py','_review','render-manifest.json','output-audit.json','prepare.log','verify.log','critique.log','build.log'}
def stray_files(w):
    st=json.loads((w/'session.json').read_text()) if (w/'session.json').exists() else {}
    keep=ALLOWED|{Path(st.get('source','')).name,'Danh_gia_'+Path(st.get('source','x')).stem+'.html'}
    return sorted(x.name for x in w.iterdir() if x.name not in keep and not x.name.startswith('session-before-recovery-'))

def load_model_json(path):
    """Đọc JSON do model viết; lỗi cú pháp trả về thông báo để giao sửa, không văng traceback."""
    try:return json.loads(Path(path).read_text(encoding='utf8')),None
    except FileNotFoundError:return None,f'chưa có {path}'
    except json.JSONDecodeError as error:return None,f'{path} không phải JSON hợp lệ: {error}'

def main():
    ap=argparse.ArgumentParser(description=__doc__);sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('init');p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--today',default=datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date().isoformat());p.add_argument('--model',default='model mặc định của iWork',help='Chỉ để ghi vào phiếu; driver không gọi model')
    p=sp.add_parser('next');p.add_argument('--work',required=True)
    p=sp.add_parser('doctor');p.add_argument('--work',required=True)
    p=sp.add_parser('resume');p.add_argument('--work',required=True)
    a=ap.parse_args();bootstrap();m=helper()
    if a.cmd=='init':
        source=Path(a.source).resolve()
        if not source.is_file() or source.suffix.lower() not in ['.pptx','.docx','.pdf']:raise ValueError('--source must be a PPTX/DOCX/PDF file, never an _review folder')
        w=Path(a.output).resolve()
        if not w.is_relative_to(Path.cwd().resolve()):raise ValueError(f'Output must be inside the current iWork workspace {Path.cwd()}. Use a new relative output folder, not the input folder.')
        real_today=datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date().isoformat()
        if a.today!=real_today:
            print(f'LƯU Ý: bỏ --today {a.today}; dùng ngày hệ thống {real_today} (model hay tự ghi sai năm, làm sai mọi kết luận quá hạn/chưa tới hạn).')
            a.today=real_today
        w.mkdir(parents=True,exist_ok=False);src=w/source.name;shutil.copy2(source,src)
        st={'source':str(src),'source_sha256':sha(src),'skill_hashes':m.skill_hashes(),'today':a.today,'model':a.model,'phase':'prepare','repairs':{},'mode':'iwork-native-model'};save(w/'session.json',st);m.TODAY=a.today
        try:
            m.tool(w,src,'prepare')
            wd=src.parent/'_review'/src.stem
            manifest=m.render(w,src,wd);save(w/'render-manifest.json',manifest)
        except Exception as error:
            st.update(state='FAILED',error=str(error));save(w/'session.json',st);raise
        st.update(phase='candidates',state='WAITING_FOR_MODEL',prepared_hashes={str(p):sha(p) for p in (wd/'content.md',wd/'facts.json',wd/'source-map.json')})
        wd=src.parent/'_review'/src.stem
        return candidates_task(w,wd,st)
    w=Path(a.work).resolve();st=json.loads((w/'session.json').read_text());src=w/Path(st['source']).name;wd=src.parent/'_review'/src.stem;m.TODAY=st['today']
    if a.cmd=='doctor':
        if not src.is_file() or sha(src)!=st['source_sha256']:raise ValueError('Cannot recover: copied source missing or changed')
        repairs=st.setdefault('maintenance',[]);save(w/f'session-before-recovery-{len(repairs)+1}.json',st)
        repairs.append({'reason':'Explicit recovery after driver update or agent path edit','previous_source':st['source'],'previous_skill_hashes':st['skill_hashes'],'new_skill_hashes':m.skill_hashes()})
        expected=[wd/'content.md',wd/'facts.json',wd/'source-map.json']
        missing=[str(p) for p in expected if not p.is_file()]
        if missing:raise ValueError('Cannot recover: missing prepared files '+', '.join(missing)+'; start a new run')
        new_prepared={str(p):sha(p) for p in expected}
        st.update(source=str(src),skill_hashes=m.skill_hashes(),prepared_hashes=new_prepared);save(w/'session.json',st)
        return resume_task(w,wd,st)
    for path,digest in st.get('prepared_hashes',{}).items():
        if not Path(path).is_file() or sha(path)!=digest:raise ValueError('Prepared evidence changed; start a new run')
    if sha(src)!=st['source_sha256']:raise ValueError('Source changed; start a new run')
    if m.skill_hashes()!=st['skill_hashes']:raise ValueError('Skill changed during run; start a new run')
    if a.cmd=='resume':return resume_task(w,wd,st)
    phase=st['phase']
    if phase=='prepare':raise ValueError('Prepare did not complete; inspect prepare.log and start a new output after fixing the environment')
    if phase=='complete':print(json.dumps(st,ensure_ascii=False));print('HOÀN TẤT: '+st.get('output',''));return
    if phase=='candidates':
        try:
            m.tool(w,src,'verify')
        except RuntimeError as error:
            st['repairs']['candidates_error']=st['repairs'].get('candidates_error',0)+1
            if st['repairs']['candidates_error']>2:raise
            return task(w,st,'Sửa lỗi kỹ thuật trong candidates.json',f'{wd}/candidates.json chưa qua được verify vì lỗi định dạng/schema (không phải REJECT nội dung từng mục). Lỗi thật từ công cụ: {error}\nSửa đúng lỗi này theo mẫu ở {S}/references/candidates.md rồi chạy next_command.')
        v=json.loads((wd/'verified.json').read_text());bad=[x for x in v['issues'] if x['status']=='REJECT']
        if bad and not st['repairs'].get('auto_quotes'):
            st['repairs']['auto_quotes']=1
            if shrink_quotes(m,wd,v,bad):
                try:m.tool(w,src,'verify')
                except RuntimeError:pass
                v=json.loads((wd/'verified.json').read_text());bad=[x for x in v['issues'] if x['status']=='REJECT']
            if bad and len(v['issues'])-len(bad)>=3:st['repairs']['candidates']=1;save(w/'session.json',st)   # còn đủ mục đạt: bỏ mục hỏng ngay, không nhờ model sửa
        if bad and not st['repairs'].get('candidates'):
            st['repairs']['candidates']=1;save(wd/'rejected-before-repair.json',bad)
            return task(w,st,'Sửa trích dẫn một lần',f'Đọc {w}/verify.log và {wd}/content.md. Dùng công cụ edit sửa ĐÚNG trường `quote` của các mục bị REJECT trong {wd}/candidates.json bằng đoạn nguyên văn có thật trong {wd}/content.md; không viết lại cả tệp, không sửa source hay skill. Rồi chạy next_command.')
        if bad:
            save(wd/'rejected-after-repair.json',bad);c=json.loads((wd/'candidates.json').read_text());ids={x['id'] for x in bad};c['issues']=[x for x,vx in zip(c['issues'],v['issues']) if vx['id'] not in ids];c.setdefault('notes',[]).extend('Không qua kiểm trích dẫn: '+x['title']+'. '+x['reason'] for x in bad);save(wd/'candidates.json',c)
            try:
                m.tool(w,src,'verify')
            except RuntimeError as error:
                st['repairs']['candidates_error']=st['repairs'].get('candidates_error',0)+1
                if st['repairs']['candidates_error']>2:raise
                return task(w,st,'Sửa lỗi kỹ thuật trong candidates.json',f'{wd}/candidates.json chưa qua được verify sau khi loại các mục REJECT. Lỗi thật từ công cụ: {error}\nSửa đúng lỗi này rồi chạy next_command.')
        try:
            m.tool(w,src,'critique')
        except RuntimeError as error:
            st['repairs']['critique_error']=st['repairs'].get('critique_error',0)+1
            if st['repairs']['critique_error']>2:raise
            return task(w,st,'Sửa lỗi kỹ thuật trước khi phản biện',f'Bước critique chưa chạy được. Lỗi thật từ công cụ: {error}\nKiểm tra {wd}/candidates.json/verified.json rồi chạy next_command.')
        st['phase']='critique'
        return task(w,st,'Phản biện trước khi giữ nhận xét',f'{CRITIQUE_HOWTO.format(task=wd/"critique_task.md",out=wd/"critique.json")} Phản biện từng trường bằng nguồn và phản chứng, đủ tất cả ID; trích đúng chưa có nghĩa là suy luận đúng. CHỈ ghi critique.json: không sửa candidates.json hay verified.json (nhận định sai thì ghi ket_luan SAI, driver tự loại). Viết JSON rồi chạy next_command; không gọi prepare/verify/build thủ công.')
    if phase=='critique':
        c,err=load_model_json(wd/'critique.json');v=json.loads((wd/'verified.json').read_text());required=[x['id'] for x in v['issues'] if x['status']=='OK']
        if isinstance(c,dict):
            for k in required:                       # điền phần tất định theo ket_luan để model chỉ viết nhận định (ngắn hơn, ít sai cú pháp)
                r=c.get(k)
                if not isinstance(r,dict):continue
                ce=r.get('counterevidence') if isinstance(r.get('counterevidence'),dict) else None
                if str(r.get('ket_luan','')).upper() in ('DUNG','ĐÚNG') and r.get('ly_do'):
                    r.setdefault('checks',{f:True for f in ('title','problem','why','fix','priority','location')})
                    r.setdefault('a',str(r['ly_do']));r.setdefault('b',str((ce or {}).get('finding') or 'không có căn cứ bổ sung'))
                    if ce is not None:ce.setdefault('effect','supports')
                elif r.get('ly_do'):
                    r.setdefault('checks',{f:False for f in ('title','problem','why','fix','priority','location')})
                    r.setdefault('a',str(r['ly_do']));r.setdefault('b',str((ce or {}).get('finding') or 'không có căn cứ bổ sung'))
                    if ce is not None:ce.setdefault('effect','weakens')
            save(wd/'critique.json',c)
        if isinstance(c,dict) and not isinstance(c.get('_meta'),dict):
            c['_meta']={'mode':'same_context'};save(wd/'critique.json',c)   # không ghi mode = tự phản biện trong cùng phiên; phiếu sẽ nêu hạn chế này
        mode=(c or {}).get('_meta',{}).get('mode') if isinstance((c or {}).get('_meta'),dict) else None
        if err or not isinstance(c,dict) or (required and mode not in ('subagent','same_context')) or any(k not in c or not isinstance(c.get(k),dict) or not c[k].get('counterevidence',{}).get('finding') or not c[k].get('counterevidence',{}).get('locations') for k in required):
            st['repairs']['critique']=st['repairs'].get('critique',0)+1
            if st['repairs']['critique']>2:raise ValueError('Phản biện vẫn thiếu sau hai lần sửa')
            why=err or ('thiếu "_meta": {"mode": "subagent" hoặc "same_context"}' if required and mode not in ('subagent','same_context') else f'thiếu ID hoặc counterevidence; cần đủ {required}')
            return task(w,st,'Bổ sung phản biện còn thiếu',f'Lỗi: {why}. Đọc {wd}/critique_task.md. Viết {wd}/critique.json đủ key {required} theo schema, mỗi ID có counterevidence.locations và counterevidence.finding, cộng key "_meta": {{"mode": "subagent"|"same_context"}}. Không đổi candidates. Chạy next_command.')
        try:
            m.tool(w,src,'build')
        except RuntimeError as error:
            st['repairs']['build_error']=st['repairs'].get('build_error',0)+1
            if st['repairs']['build_error']>2:raise
            return task(w,st,'Sửa lỗi kỹ thuật trước khi build',f'Bước build chưa chạy được. Lỗi thật từ công cụ: {error}\nKiểm tra {wd}/critique.json rồi chạy next_command.')
        st['phase']='details'
        return details_task(w,wd,st)
    if phase=='details':
        d,err=load_model_json(wd/'report-details.json')
        if not err and isinstance(d,dict):
            d,err=merge_details(w,wd,d)
        if err or not isinstance(d,dict):
            st['repairs']['details']=st['repairs'].get('details',0)+1
            if st['repairs']['details']>3:raise ValueError('report-details.json vẫn lỗi sau ba lần sửa: '+str(err))
            return details_task(w,wd,st,err or 'report-details.json phải là object JSON')
        d.update(source_sha256=sha(src),verified_sha256=sha(wd/'verified.json'),render_manifest=json.loads((w/'render-manifest.json').read_text()),model=st['model']);save(wd/'report-details.json',d)
        try:
            m.tool(w,src,'build');audit=m.audit_output(w,src,wd,d['render_manifest'])
        except (RuntimeError,ValueError) as error:
            st['repairs']['details']=st['repairs'].get('details',0)+1
            if st['repairs']['details']>3:raise
            return details_task(w,wd,st,str(error))
        st.update(phase='complete',state='BUILT',output=str(w/('Danh_gia_'+src.stem+'.html')),output_sha256=audit['output_sha256'],all_pass=audit['all_pass']);save(w/'session.json',st);save(w/'status.json',st)
        tidy_workspace(w,wd,{Path(st['output']).name,'session.json',src.name})
        print(json.dumps(st,ensure_ascii=False))
        try:shown=str(Path(st['output']).resolve().relative_to(Path.cwd().resolve()))
        except ValueError:shown=st['output']
        print('HOÀN TẤT: '+shown+('' if st['all_pass'] else ' (audit chưa đạt: báo người dùng)')+'  (trích dẫn cho người dùng bằng đường dẫn tương đối này)')
        warn=wd/'details-warnings.json'
        if warn.is_file():
            items=json.loads(warn.read_text(encoding='utf8'))
            if items:print('LƯU Ý khi báo kết quả (kiểm tự động nghi ngờ, người duyệt nên xem lại):\n  - '+'\n  - '.join(items[:6]))
        return
    raise ValueError('Unknown checkpoint phase')

def candidates_task(w,wd,st):
    return task(w,st,'Viết/sửa candidates.json',f'Đọc MỘT lần: {wd}/content.md (đã tách chữ hiển thị, ghi chú người nói, metadata), {wd}/facts.md và schema {S}/references/candidates.md. KHÔNG đọc source-map.json (trùng content.md, chỉ để driver kiểm). Viết {wd}/candidates.json: tối đa 12 vấn đề đúng và quan trọng (không ép đủ), mỗi vấn đề có trích dẫn nguyên văn ngắn từ content.md. Luật nhận xét ở SKILL.md: không bịa, notes không phải slide hiển thị, mâu thuẫn trong nguồn thì xin xác nhận chứ không tự chọn bên đúng, chỉ nói quá hạn khi có bằng chứng chưa hoàn thành, không nhận xét bố cục khi chưa xem ảnh (ghi vào notes là chưa kiểm hình). Không đọc ảnh PNG bằng công cụ chỉ đọc text. Viết xong chạy next_command; không tự gọi review.py.')

def resume_task(w,wd,st):
    if st['phase']=='candidates':return candidates_task(w,wd,st)
    if st['phase']=='critique':return task(w,st,'Tiếp tục phản biện',f'{CRITIQUE_HOWTO.format(task=wd/"critique_task.md",out=wd/"critique.json")} Viết đủ ID, checks boolean và counterevidence.locations/finding cụ thể. Không sửa candidates.json. Sau đó chạy next_command.')
    if st['phase']=='details':return details_task(w,wd,st)
    if st['phase']=='complete':print(json.dumps(st,ensure_ascii=False));print('HOÀN TẤT: '+st.get('output',''));return
    raise ValueError('Prepare chưa hoàn tất; xem prepare.log, không tự tiếp tục dữ liệu thiếu')

SCORE_NAMES=[('Đề xuất rõ ràng',15),('Chính xác, nhất quán',15),('Bằng chứng',10),('Đối tượng, thị trường',10),('Hiệu quả, chi phí',10),('Kế hoạch, nguồn lực',15),('Rủi ro',15),('Cấu trúc trình bày',10)]

def _slide_numbers(issue):
    return sorted({int(n) for n in re.findall(r'\d+',str(issue.get('slides','')))})

def auto_details(w,wd):
    """Phần phiếu tất định, dựng từ final.json và source-map.json; model chỉ phải viết điểm 8 tiêu chí (và sửa lời nếu muốn)."""
    final=json.loads((wd/'final.json').read_text());issues=final['issues']
    manifest=json.loads((w/'render-manifest.json').read_text());smap=json.loads((wd/'source-map.json').read_text())
    by_page={p['page']:p for p in smap.get('pages',[])}
    pages=[]
    for n in range(1,manifest['page_count']+1):
        shown=re.sub(r'\s+',' ',str(by_page.get(n,{}).get('display',''))).strip()
        mine=[x for x in issues if n in _slide_numbers(x)]
        note=('Nội dung: '+shown[:150]+('…' if len(shown)>150 else '')) if shown else 'Trang không có chữ trích xuất được (chưa kiểm hình).'
        if mine:note+=' · Phát hiện: '+'; '.join(x['title'].rstrip('.') for x in mine)
        pages.append({'page':n,'title':(shown[:60] or f'Trang {n}'),'observation':note,'issue_ids':[x['id'] for x in mine]})
    titles='; '.join(x['title'].rstrip('.') for x in issues)
    return {'metadata':{'presenter':None,'department':None,'version':None,'review_type':None,'request_summary':None},
        'scorecard':[{'name':n,'weight':wt,'score':None,'rationale':'','slides':[]} for n,wt in SCORE_NAMES],
        'page_reviews':pages,
        'questions':[{'text':'Anh/chị làm rõ giúp: '+x['title'].rstrip('.')+'?','issue_ids':[x['id']]} for x in issues],
        'actions':[{'issue_id':x['id'],'task':x.get('fix') or x['title'],'owner':None,'collaborators':None,'deadline':None} for x in issues],
        'proposed_structure':[],
        'response_draft':(final.get('verdict','')+(' Đề nghị anh/chị xem xét: '+titles+'.' if titles else '')).strip(),
        'report_checks':{'notes':['Nhận xét từng trang, câu hỏi, hành động và dự thảo phản hồi do công cụ tổng hợp từ danh sách vấn đề đã chốt; chỉ điểm 8 tiêu chí do reviewer chấm.']}}

def merge_details(w,wd,model):
    """Gộp phần model viết lên mặc định của driver. Trả (details, lỗi) để giao sửa nếu điểm 8 tiêu chí chưa đạt."""
    base=auto_details(w,wd)
    sc=model.get('scorecard')
    if not isinstance(sc,list) or len(sc)!=8:
        return None,'scorecard cần đúng 8 mục theo thứ tự: '+', '.join(n for n,_ in SCORE_NAMES)
    cards=[]
    for item,(name,weight) in zip(sc,SCORE_NAMES):
        if not isinstance(item,dict):return None,'mỗi mục scorecard phải là object {name, score, rationale, slides}'
        try:score=float(item.get('score'))
        except (TypeError,ValueError):return None,f'scorecard "{item.get("name",name)}": thiếu score (số 0–10)'
        if not 0<=score<=10:return None,f'scorecard "{item.get("name",name)}": score phải trong 0–10'
        if not str(item.get('rationale','')).strip():return None,f'scorecard "{item.get("name",name)}": thiếu rationale'
        cards.append({'name':item.get('name') or name,'weight':item.get('weight') or weight,'score':score,'rationale':str(item['rationale']).strip(),'slides':item.get('slides') or []})
    base['scorecard']=cards
    for key in ('metadata','questions','proposed_structure','response_draft','report_checks'):
        if model.get(key):base[key]=model[key]
    for key,idk in (('page_reviews','page'),('actions','issue_id')):
        got={x.get(idk):x for x in model.get(key) or [] if isinstance(x,dict)}
        base[key]=[{**x,**{k:v for k,v in got.get(x[idk],{}).items() if v not in (None,'')}} for x in base[key]]
    return base,None

def details_task(w,wd,st,error=''):
    f=json.loads((wd/'final.json').read_text());ids=[x['id'] for x in f['issues']];pages=json.loads((w/'render-manifest.json').read_text())['page_count']
    names='\n'.join(f'  {i}. {n}' for i,(n,_) in enumerate(SCORE_NAMES,1))
    return task(w,st,'Chấm điểm 8 tiêu chí',f'Đọc {wd}/final.json ({len(ids)} vấn đề đã chốt: {ids}) và, nếu cần, các trang liên quan trong {wd}/content.md. Viết {wd}/report-details.json CHỈ gồm một khoá `scorecard`: danh sách đúng 8 mục theo thứ tự\n{names}\nmỗi mục {{"name": …, "score": 0–10, "rationale": "1–2 câu bám nguồn, tối đa 250 ký tự", "slides": [số trang]}}. Điểm là nhận định của reviewer; không nêu phát hiện mới nghiêm trọng ngoài danh sách đã chốt. Công cụ tự dựng nhận xét {pages} trang, câu hỏi, hành động và dự thảo phản hồi từ final.json; bạn không cần viết. Viết xong chạy next_command.'+(('\nLỖI CẦN SỬA (sửa hết trong một lần): '+error) if error else ''))

if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,OSError,KeyError) as error:
        print('LỖI: '+str(error),file=sys.stderr)
        print('=== DỪNG: báo người dùng đúng lỗi trên. Nếu lỗi do đường dẫn/driver đổi, thử "iwork.py doctor --work <output>"; không tự sửa session.json, không init lại khi chưa báo. ===')
        raise SystemExit(1)
