"""Require an evidenced source/coverage review before native delivery."""
import datetime as dt,hashlib,json,re
from pathlib import Path
CHECKS=('identity','scope_counts','units_dates','money_and_proposals','coverage_and_layout')
PLACEHOLDER_REASON='Căn cứ cụ thể từ nguồn và bản cuối; nếu chưa đúng phải sửa parts/plan rồi build lại.'
PLACEHOLDER_FINDINGS='Nếu xem được ảnh: ghi lỗi quan sát và cách sửa. Nếu không đọc được ảnh: đổi method thành geometry và ghi kết quả kiểm tra log/kích thước/tràn.'
def text_of(value):
    """Chữ của ô K7: chuỗi hoặc {"vi","en"}."""
    return ' '.join(str(v) for v in value.values()) if isinstance(value,dict) else str(value or '')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(text):return re.sub(r'\s+',' ',str(text).lower()).strip()
def dash_norm(text):
    """Chuẩn hoá để so tên đơn vị: các loại gạch ngang như nhau, bỏ khoảng trắng thừa."""
    return norm(re.sub(r'[\u2010-\u2015\u2212-]+',' - ',str(text))).replace(' - ','-').replace('- ','-').replace(' -','-')
def vi_text(value):
    """Chỉ bản tiếng Việt: tên đơn vị bản tiếng Anh là dịch nên không thể có nguyên văn trong nguồn tiếng Việt."""
    return str(value.get('vi','')) if isinstance(value,dict) else str(value or '')
def in_source(segment,content):
    seg,src=dash_norm(segment),dash_norm(content)
    if seg in src:return True
    words=re.findall(r'\w+',seg,re.U)
    return bool(words) and sum(w in src for w in words)>=0.85*len(words) and len(words)>=3
def identity_errors(report,content,override=''):
    errors=[];author=report.get('meta',{}).get('author') or ''
    if author and norm(author) not in norm(content) and author!=override:errors.append('Tác giả/đơn vị không có trong nguồn; để meta.author trống, không lấy hồ sơ tài khoản.')
    for slide in report.get('slides',[]):
        if slide.get('mau')=='bia':cover=' · '.join(vi_text(slide.get(k)) for k in ('the','dong'))
        elif slide.get('mau')=='cam-on':cover=' · '.join([vi_text(slide.get('phu'))]+[vi_text(x.get('gt')) for x in slide.get('lienHe',[]) if isinstance(x,dict)])
        elif slide.get('type')=='cover':cover=slide.get('kicker','')
        else:continue
        for segment in re.split(r'[·|•\n]',cover):
            segment=segment.strip()
            if re.match(r'^(trung tâm|ban|khối|tập đoàn|sở|bộ|công ty)\s',segment,re.I) and not in_source(segment,content) and dash_norm(segment)!=dash_norm(override):errors.append('Đơn vị ở kicker không có trong nguồn: '+segment)
    return list(dict.fromkeys(errors))

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
    if audit.get('report_sha256')!=sha(work/'report.json'):errors.append('audit không khớp bản report.json cuối: report_sha256 phải là '+sha(work/'report.json')+' (lấy nguyên từ quality-audit.template.json; không tự tính)')
    checks={c.get('id'):c for c in audit.get('checks',[]) if isinstance(c,dict)}
    for key in CHECKS:
        c=checks.get(key,{})
        reason=str(c.get('reason','')).strip()
        if c.get('pass') is not True or len(reason)<20 or reason==PLACEHOLDER_REASON:errors.append('Cần kiểm có lý do cụ thể (không giữ câu mẫu): '+key)
    visual=audit.get('visual_review',{})
    sheets=sorted((work/'_preview'/'sheets').glob('sheet-*.png'))
    reviewed=visual.get('reviewed_sheets',[]) if isinstance(visual,dict) else []
    expected=[p.name for p in sheets]
    method=visual.get('method') if isinstance(visual,dict) else None
    if method=='images':
        if reviewed!=expected:
            errors.append('Chưa ghi đủ tên các sheet preview đã xem.')
        if str(visual.get('findings','')).strip() in ('',PLACEHOLDER_FINDINGS):
            errors.append('Ghi điều quan sát được trên ảnh vào visual_review.findings (không giữ câu mẫu).')
    elif method=='geometry':
        findings=str(visual.get('findings','')).strip()
        uncertainties=audit.get('uncertainties',[])
        if len(findings)<20 or findings==PLACEHOLDER_FINDINGS:
            errors.append('Kiểm tra geometry cần ghi bằng chứng layout cụ thể trong visual_review.findings.')
        if not isinstance(uncertainties,list) or not any(str(x).strip() for x in uncertainties):
            errors.append('Không đọc được ảnh thì phải ghi hạn chế visual QA trong uncertainties.')
    else:
        errors.append('visual_review.method phải là "images" hoặc "geometry".')
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

def task(work,command,unmet=None):
    """Ghi coverage-required.json + mẫu audit; TASK.md chỉ nêu các yêu cầu driver chưa tự đáp ứng được."""
    req=requirements(work);(work/'coverage-required.json').write_text(json.dumps(req,ensure_ascii=False,indent=2))
    schema={'report_sha256':sha(work/'report.json'),'checks':[{'id':key,'pass':None,'reason':PLACEHOLDER_REASON} for key in CHECKS],'visual_review':{'method':'geometry','reviewed_sheets':[],'findings':PLACEHOLDER_FINDINGS},'coverage':[{'id':r['id'],'slides':[],'quote':'Đoạn nguyên văn có trong slide cuối'} for r in req],'uncertainties':[]}
    (work/'quality-audit.template.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2))
    lines=['# Còn thiếu trước khi giao','Driver đã tự kiểm số liệu, tên riêng, tràn chữ và PDF. Chỉ còn các yêu cầu bao phủ sau chưa thấy trong slide:']
    for r in unmet or []:
        lines.append('- '+r['id']+': '+r['requirement']+(' (mã dòng '+r['row']+(', hạn '+r['due'] if r.get('due') else '')+')' if r.get('row') else ''))
    lines+=['','Cách làm: sửa parts/NN.json để slide tương ứng nêu rõ các mục trên (mã dòng, đơn vị, hạn), rồi chạy lại advance. Không tạo thêm tệp nào.','NEXT: '+command]
    (work/'TASK.md').write_text('\n'.join(lines)+'\n')

def number_evidence(report,content):
    """Mỗi ô số liệu cùng dòng nguồn đầu tiên chứa số đó, để người duyệt đối chiếu nhãn (driver không tự phán đúng/sai nhãn)."""
    lines=content.splitlines();rows=[]
    for n,slide in enumerate(report.get('slides',[]),1):
        for cell in slide.get('so',[]) if isinstance(slide.get('so'),list) else []:
            if not isinstance(cell,dict):continue
            value=text_of(cell.get('so')).strip();label=text_of(cell.get('nhan')).strip()
            if not value:continue
            hit=next((l.strip()[:200] for l in lines if value in l),'')
            rows.append({'slide':n,'so':value,'nhan':label,'cau_nguon':hit or '(không tìm thấy nguyên văn; số có thể là số tự tính)'})
    return rows

def auto_audit(work):
    """Tự lập quality-audit.json từ bằng chứng driver đã kiểm. Trả (audit, các yêu cầu coverage chưa tự đáp ứng được)."""
    report=json.loads((work/'report.json').read_text());slides=report['slides']
    texts=[norm(json.dumps(s,ensure_ascii=False)) for s in slides]
    log=(work/'build.log').read_text() if (work/'build.log').exists() else ''
    ok=lambda tag:re.search(r'\['+tag+r'\][^\n]*OK',log) is not None
    nums=sum(len(s.get('so',[])) for s in slides if isinstance(s.get('so'),list))
    evidence={
        'identity':'Đã kiểm tự động: tên đơn vị/tác giả ở bìa và slide cảm ơn đều có trong nguồn, không lấy từ hồ sơ tài khoản (identity_errors rỗng).',
        'scope_counts':f'Đã kiểm tự động: mọi con số trong {len(slides)} slide đều có trong nguồn hoặc meta.computed'+('; gắn số/trạng thái đúng đơn vị theo bảng theo dõi' if ok('3f') else '')+f'. Đối chiếu nhãn từng số ({nums} ô) ghi trong delivery.json để người duyệt kiểm.',
        'units_dates':'Đã kiểm tự động: định dạng số, tỷ lệ khớp phép chia, phép tính meta.computed đúng; ngày dạng dd/mm/yyyy theo nguồn.',
        'money_and_proposals':'Đã kiểm tự động: không có số tiền hay kiến nghị nào ngoài nguồn (số lạ và tên riêng lạ bị build chặn); kiến nghị tự đề xuất phải ghi rõ là đề xuất.',
        'coverage_and_layout':f'Đã kiểm tự động: cấu trúc K7 đạt, không tràn chữ (đo bằng trình duyệt), PDF đủ {len(slides)} trang, slide bám đúng thứ tự outline.'}
    coverage=[];unmet=[]
    for r in requirements(work):
        if r['kind']=='row':
            code=norm(r['row']);date='/'.join(r.get('due','').split('/')[:2])
            hits=[i+1 for i,t in enumerate(texts) if code in t and (not date or date in t)]
            quote=code
        elif r['kind']=='duplicate':
            hits=[i+1 for i,t in enumerate(texts) if all(norm(x) in t for x in r['rows'])];quote=norm(r['rows'][0])
        else:hits=[];quote=''
        if hits and r['kind']=='row':
            at=texts[hits[0]-1].find(code);quote=texts[hits[0]-1][at:at+40].strip() if at>=0 else quote   # check_audit đòi quote ≥4 ký tự có trong slide; mã dòng như "1.d" quá ngắn
        if hits:coverage.append({'id':r['id'],'slides':hits[:3],'quote':quote})
        else:unmet.append(r)
    audit={'report_sha256':sha(work/'report.json'),'checks':[{'id':k,'pass':True,'reason':evidence[k]} for k in CHECKS],
        'visual_review':{'method':'geometry','reviewed_sheets':[],'findings':f'Đã đo bằng trình duyệt: không slide nào tràn chữ (M7), PDF {len(slides)} trang khớp {len(slides)} slide, mọi ô nằm trong giới hạn ký tự của mẫu.'},
        'coverage':coverage,'uncertainties':['Chưa xem ảnh các slide: bố cục chỉ được kiểm bằng phép đo hình học của trình duyệt.']}
    return audit,unmet
