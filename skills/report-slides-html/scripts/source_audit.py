"""Require an evidenced source/coverage review before native delivery."""
import datetime as dt,hashlib,json,re
from pathlib import Path
CHECKS=('identity','scope_counts','units_dates','money_and_proposals','coverage_and_layout')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(text):return re.sub(r'\s+',' ',str(text).lower()).strip()
def identity_errors(report,content,override=''):
    errors=[];author=report.get('meta',{}).get('author') or ''
    if author and norm(author) not in norm(content) and author!=override:errors.append('Tác giả/đơn vị không có trong nguồn; để meta.author trống, không lấy hồ sơ tài khoản.')
    for slide in report.get('slides',[]):
        if slide.get('type')!='cover':continue
        for segment in re.split(r'[·|•\n]',slide.get('kicker','')):
            segment=segment.strip()
            if re.match(r'^(trung tâm|ban|khối|tập đoàn|sở|bộ|công ty)\s',segment,re.I) and norm(segment) not in norm(content) and norm(segment)!=norm(override):errors.append('Đơn vị ở kicker không có trong nguồn: '+segment)
    return errors

def requirements(work):
    result=[]
    for p in sorted((work/'tracker').glob('*/tracker.json')):
        data=json.loads(p.read_text());profile=p.with_name('source-checks.json')
        if not profile.exists():continue
        check=json.loads(profile.read_text());source=p.parent.name;today=dt.datetime.strptime(data['date'],'%d/%m/%Y').date()
        must=set(check['union'])|set(check['later_than_total'])
        for row in data['rows']:
            due=dt.datetime.strptime(row['due'],'%d/%m/%Y').date() if row.get('due') else None
            if row.get('st')!='xong' and due and today<=due<=today+dt.timedelta(days=3):must.add(row['stt'])
            if re.search(r'\d\s*(?:tỷ|triệu|TB|GB)',row.get('result',''),re.I):must.add(row['stt'])
        for row in data['rows']:
            if row['stt'] in must:
                result.append({'id':source+':'+row['stt'],'kind':'row','row':row['stt'],'unit':row.get('unit',''),'due':row.get('due',''),'result':row.get('result',''),'requirement':'Giữ mã dòng, đơn vị, trạng thái/kết quả và đúng hạn; khoản tiền chỉ là khoản nguồn ghi, không tự suy ra chưa được cấp hoặc là nguyên nhân chậm.'})
        for ids in check['duplicate_candidates']:result.append({'id':source+':duplicate:'+','.join(ids),'kind':'duplicate','rows':ids,'requirement':'Nêu rõ nghi trùng, chưa xác nhận bản ghi thừa; không khử âm thầm.'})
        if check['later_than_total']:result.append({'id':source+':timeline','kind':'timeline','requirement':'Nêu mốc tổng khác các hạn thành phần; không gộp thành một deadline.'})
    return result

def check_audit(work,audit):
    report=json.loads((work/'report.json').read_text());slides=report['slides'];state=json.loads((work/'iwork-state.json').read_text()) if (work/'iwork-state.json').exists() else {};content=(work/'content.md').read_text() if (work/'content.md').exists() else '';errors=identity_errors(report,content,state.get('author_override',''))
    if audit.get('report_sha256')!=sha(work/'report.json'):errors.append('audit không khớp bản report.json cuối')
    checks={c.get('id'):c for c in audit.get('checks',[]) if isinstance(c,dict)}
    for key in CHECKS:
        c=checks.get(key,{})
        if c.get('pass') is not True or len(str(c.get('reason','')).strip())<20:errors.append('Cần kiểm có lý do cụ thể: '+key)
    covered={c.get('id'):c for c in audit.get('coverage',[]) if isinstance(c,dict)}
    for req in requirements(work):
        c=covered.get(req['id'],{});nums=c.get('slides',[])
        if not nums or any(not isinstance(n,int) or not 1<=n<=len(slides) for n in nums):errors.append('Thiếu slide bằng chứng: '+req['id']);continue
        text=norm(' '.join(json.dumps(slides[n-1],ensure_ascii=False) for n in nums));quote=norm(c.get('quote',''))
        if len(quote)<4 or quote not in text:errors.append('Quote không có trong slide cuối: '+req['id'])
        if req['kind']=='row':
            if req['row'] not in text:errors.append('Slide cần ghi rõ mã dòng '+req['row'])
            date='/'.join(req.get('due','').split('/')[:2])
            if date and date not in text:errors.append('Thiếu hạn của dòng '+req['row']+': '+date)
        elif req['kind']=='duplicate' and not all(row in text for row in req['rows']):errors.append('Thiếu mã các dòng nghi trùng')
    return errors

def task(work,command):
    req=requirements(work);(work/'coverage-required.json').write_text(json.dumps(req,ensure_ascii=False,indent=2))
    schema={'report_sha256':sha(work/'report.json'),'checks':[{'id':key,'pass':None,'reason':'Căn cứ cụ thể từ nguồn và bản cuối; nếu chưa đúng phải sửa parts/plan rồi build lại.'} for key in CHECKS],'coverage':[{'id':r['id'],'slides':[],'quote':'Đoạn nguyên văn có trong slide cuối, không phải nguyên văn nguồn'} for r in req],'uncertainties':[]}
    (work/'quality-audit.template.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2))
    (work/'TASK.md').write_text('# Kiểm chất lượng trước giao\nĐọc report.json cuối, nguồn/facts và coverage-required.json; xem toàn bộ ảnh _preview/sheets nếu công cụ của phiên hỗ trợ. Nếu không đọc được ảnh, ghi rõ trong uncertainties và phương pháp kiểm layout bằng log/geometry; không nhận đã xem ảnh. Viết quality-audit.json theo quality-audit.template.json.\nKiểm đếm dòng cha/tổng/chi tiết/nghi trùng; hợp/giao trạng thái; số tổng có phạm vi ở mọi lần lặp; so sánh theo đơn vị phải rõ đầy đủ hay chọn mục. Giữ hạn riêng, đơn vị đo, phân biệt khoản tiền nguồn ghi với thiếu vốn đã xác nhận và đề xuất của reviewer. Không bịa tác giả, nguyên nhân chậm, ngân sách hoặc mức ưu tiên tuyệt đối. Không lặp một KPI hai lần trên cùng slide.\nNếu thiếu/sai thì sửa parts/plan, build lại rồi audit đúng hash mới. Không tick qua khi thiếu bằng chứng.\nNEXT: '+command+'\n')
    print('BUILD ĐẠT; CHƯA GIAO. Đọc '+str(work/'TASK.md')+'; ghi quality-audit.json rồi chạy: '+command)
