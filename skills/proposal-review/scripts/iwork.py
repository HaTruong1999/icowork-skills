#!/usr/bin/env python3
"""Checkpointed native-agent workflow. No API key or model calls in this driver."""
import argparse, datetime, hashlib, importlib.util, json, os, shutil, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo
S=Path(__file__).resolve().parent.parent
for directory in ('/opt/homebrew/bin', '/usr/local/bin'):
    if Path(directory).is_dir() and directory not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + directory

def bootstrap():
    try:
        import bs4, fitz
    except ImportError:
        env=Path.home()/'.cache'/'proposal-review'/'python'
        py=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        if not py.exists():subprocess.run([sys.executable,'-m','venv',str(env)],check=True)
        subprocess.run([str(py),'-m','pip','install','-r',str(S/'scripts/requirements.txt')],check=True)
        if Path(sys.executable).absolute()==py.absolute():raise RuntimeError('Dependency installation failed')
        os.execv(str(py),[str(py),str(Path(__file__).resolve()),*sys.argv[1:]])

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
    spec=importlib.util.spec_from_file_location('full_workflow',S/'scripts/run_coding_full.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def task(w,st,title,body):
    p=w/'TASK.md';p.write_text('# '+title+'\n\n'+body,encoding='utf8');save(w/'session.json',st)
    print(json.dumps({'state':'WAITING_FOR_MODEL','phase':st['phase'],'task':str(p),'next_command':f'python3 "{Path(__file__).resolve()}" next --work "{w}"'},ensure_ascii=False))

def main():
    ap=argparse.ArgumentParser(description=__doc__);sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('init');p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--today',default=datetime.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date().isoformat());p.add_argument('--model',default='vnptai/coding-assistant')
    p=sp.add_parser('next');p.add_argument('--work',required=True)
    p=sp.add_parser('doctor');p.add_argument('--work',required=True)
    p=sp.add_parser('resume');p.add_argument('--work',required=True)
    a=ap.parse_args();bootstrap();m=helper()
    if a.cmd=='init':
        source=Path(a.source).resolve()
        if not source.is_file() or source.suffix.lower() not in ['.pptx','.docx','.pdf']:raise ValueError('--source must be a PPTX/DOCX/PDF file, never an _review folder')
        w=Path(a.output).resolve()
        if not w.is_relative_to(Path.cwd().resolve()):raise ValueError(f'Output must be inside the current iWork workspace {Path.cwd()}. Use a new relative output folder, not the input folder.')
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
    if phase=='complete':print(json.dumps(st,ensure_ascii=False));return
    if phase=='candidates':
        try:
            m.tool(w,src,'verify')
        except RuntimeError as error:
            st['repairs']['candidates_error']=st['repairs'].get('candidates_error',0)+1
            if st['repairs']['candidates_error']>2:raise
            return task(w,st,'Sửa lỗi kỹ thuật trong candidates.json',f'{wd}/candidates.json chưa qua được verify vì lỗi định dạng/schema (không phải REJECT nội dung từng mục). Lỗi thật từ công cụ: {error}\nSửa đúng lỗi này theo mẫu ở {S}/references/candidates.md rồi chạy next_command.')
        v=json.loads((wd/'verified.json').read_text());bad=[x for x in v['issues'] if x['status']=='REJECT']
        if bad and not st['repairs'].get('candidates'):
            st['repairs']['candidates']=1;save(wd/'rejected-before-repair.json',bad)
            return task(w,st,'Sửa trích dẫn một lần',f'Đọc {w}/verify.log và {wd}/content.md. Sửa {wd}/candidates.json chỉ với căn cứ nguyên văn, không sửa source hay skill. Không sửa bằng chuỗi thay thế chưa đối chiếu file. Ghi JSON đầy đủ nếu cần, rồi chạy next_command.')
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
        return task(w,st,'Phản biện trước khi giữ nhận xét',f'Đọc TOÀN BỘ {wd}/critique_task.md; phản biện từng trường bằng nguồn và phản chứng. Viết {wd}/critique.json đúng schema, đủ tất cả ID. Nếu có ngữ cảnh mới thì dùng; nếu không, ghi hạn chế phản biện cùng ngữ cảnh. Không lấy nguyên văn đúng làm bằng chứng cho suy luận đúng. Chú ý tác động/mức độ/fix: nội dung đã có thì không yêu cầu thêm lại, các nhóm không đồng nghĩa từng sản phẩm, không coi số viết tắt metadata là tên sai, không xác quyết pháp lý hay đối thủ từ kiến thức chưa kiểm. Không gọi prepare/verify/build thủ công; viết JSON rồi chạy next_command.')
    if phase=='critique':
        c=json.loads((wd/'critique.json').read_text());v=json.loads((wd/'verified.json').read_text());required=[x['id'] for x in v['issues'] if x['status']=='OK']
        if any(k not in c or not isinstance(c.get(k),dict) or not c[k].get('counterevidence',{}).get('finding') or not c[k].get('counterevidence',{}).get('locations') for k in required):
            st['repairs']['critique']=st['repairs'].get('critique',0)+1
            if st['repairs']['critique']>2:raise ValueError('Critique still incomplete after two repairs')
            return task(w,st,'Bổ sung phản biện còn thiếu',f'Đọc {wd}/critique_task.md. Viết đủ key {required} vào {wd}/critique.json theo schema, có counterevidence.locations và counterevidence.finding cho mỗi ID. Không đổi candidates. Chạy next_command.')
        try:
            m.tool(w,src,'build')
        except RuntimeError as error:
            st['repairs']['build_error']=st['repairs'].get('build_error',0)+1
            if st['repairs']['build_error']>2:raise
            return task(w,st,'Sửa lỗi kỹ thuật trước khi build',f'Bước build chưa chạy được. Lỗi thật từ công cụ: {error}\nKiểm tra {wd}/critique.json rồi chạy next_command.')
        st['phase']='details'
        return details_task(w,wd,st)
    if phase=='details':
        d=json.loads((wd/'report-details.json').read_text());d.update(source_sha256=sha(src),verified_sha256=sha(wd/'verified.json'),render_manifest=json.loads((w/'render-manifest.json').read_text()),model=st['model']);save(wd/'report-details.json',d)
        try:
            m.tool(w,src,'build');audit=m.audit_output(w,src,wd,d['render_manifest'])
        except (RuntimeError,ValueError) as error:
            st['repairs']['details']=st['repairs'].get('details',0)+1
            if st['repairs']['details']>2:raise
            return details_task(w,wd,st,str(error))
        st.update(phase='complete',state='BUILT',output=str(w/('Danh_gia_'+src.stem+'.html')),output_sha256=audit['output_sha256'],all_pass=audit['all_pass']);save(w/'session.json',st);save(w/'status.json',st)
        tidy_workspace(w,wd,{Path(st['output']).name,'session.json',src.name})
        print(json.dumps(st,ensure_ascii=False));return
    raise ValueError('Unknown checkpoint phase')

def candidates_task(w,wd,st):
    return task(w,st,'Viết/sửa candidates.json',f'Đọc {wd}/source-map.json (tách display/notes/metadata và kích thước bảng), {w}/render-manifest.json để biết ảnh đã render cho người dùng. Căn cứ chính là source-map có display/notes và cấu trúc bảng; chỉ xem ảnh nếu tool tuyên bố hỗ trợ ảnh. Không dùng tool Read chỉ hỗ trợ text để đọc PNG, không thử lặp lại các ảnh khi đã thấy không hỗ trợ; ghi hạn chế vào notes, không khẳng định đã kiểm hình. Đọc toàn bộ {wd}/content.md và facts.md; đọc {S}/references/candidates.md. Dùng model của phiên này viết {wd}/candidates.json đúng schema. Không dùng API key, không đọc báo cáo cũ. Tối đa 12, không ép đủ. Tìm phản chứng trên toàn nguồn trước khi kết luận. Notes không phải slide hiển thị; không kết luận quá hạn chỉ vì ngày đã qua. Soát tên thương hiệu ở bìa và metadata riêng. Không ép các metadata viết tắt thành lỗi. Không tự gán rò rỉ, mức độ pháp lý hoặc thiếu hạ tầng khi chưa có căn cứ. Mâu thuẫn tên/số phải xin xác nhận, không tự chọn bên đúng. Ghi chú có chữ nội bộ không tự là lỗi; group gui về tiết lộ phải có audience_evidence về người nhận thực tế. Kiểm bảng/ma trận, khả năng áp dụng benchmark và giả định business case, không chỉ metadata/keyword. Không bịa ví dụ nguồn hoặc số trang trong fix. Trích đoạn ngắn chính xác từ content.md, không thay dấu nối/xuống dòng bằng ký hiệu tự tạo. Viết xong chạy next_command dưới đây; không tự gọi review.py.')

def resume_task(w,wd,st):
    if st['phase']=='candidates':return candidates_task(w,wd,st)
    if st['phase']=='critique':return task(w,st,'Tiếp tục phản biện',f'Đọc toàn bộ {wd}/critique_task.md và viết critique.json đủ ID, checks boolean và counterevidence.locations/finding cụ thể. Không sửa candidates. Sau đó chạy next_command.')
    if st['phase']=='details':return details_task(w,wd,st)
    if st['phase']=='complete':print(json.dumps(st,ensure_ascii=False));return
    raise ValueError('Prepare chưa hoàn tất; xem prepare.log, không tự tiếp tục dữ liệu thiếu')

def details_task(w,wd,st,error=''):
    f=json.loads((wd/'final.json').read_text());ids=[x['id'] for x in f['issues']];pages=json.loads((w/'render-manifest.json').read_text())['page_count']
    return task(w,st,'Hoàn thiện đủ 12 phần của phiếu',f'Đọc {S}/references/full-report.md, toàn bộ {wd}/content.md và {wd}/final.json. Viết {wd}/report-details.json. Đúng 8 tiêu chí có lý do, đủ {pages} page_reviews (1..{pages}); actions đúng một cho mỗi ID ĐƯỢC GIỮ {ids}, tuyệt đối không dùng dropped/unverified. Nếu rỗng thì actions=[]. Không tự đặt người/hạn; phản hồi là reviewer gửi người trình, không phải xin sếp phê duyệt, không tự thêm ngày/% hoặc lời hứa đã sửa. Cấu trúc trình lại là đề xuất. Đọc source-map.json. Ảnh trong render-manifest để xem nếu có công cụ hỗ trợ ảnh; không thử PNG bằng reader chỉ đọc text. Không hỗ trợ thì ghi rõ chưa kiểm hình; không để bước ảnh chặn việc hoàn thiện phiếu. Không đánh giá bố cục nếu chưa xem ảnh. Không trừ điểm vì tiếng Anh chỉ có trong notes. Không khen bảng theo số tiêu đề khi số hàng/cột thực tế khác. Lý do điểm và observation không được tạo phát hiện nghiêm trọng mới ngoài final; nếu có thì báo rõ cần vòng review mới. Không lấy người/tác giả ở trang khác làm chữ đang hiển thị trên trang này. Ảnh và hash do công cụ điền; không cắt ảnh. Giữ nguyên toàn bộ final. Tự soát lý do điểm, observation, câu hỏi và actions tránh kéo lại nhận xét đã bị loại. Viết JSON xong chạy next_command; chưa báo xong khi chưa thấy phase=complete/all_pass=true. '+('Lỗi cần sửa: '+error if error else ''))

if __name__=='__main__':main()
