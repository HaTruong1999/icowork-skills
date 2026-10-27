"""Source-layer evidence checks shared by the native review workflow."""
import re,unicodedata

def norm(text):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFC',str(text)).lower()).strip()

def match_quote(quote,text):
    parts=[norm(x) for x in re.split(r'…|\.\.\.',str(quote)) if len(norm(x))>=4]
    return bool(parts) and all(p in norm(text) for p in parts)

def source_map(doc):
    return {'metadata':doc['meta'],'pages':[{'page':p['n'],'display':' '.join(' '.join(b) for b in p['blocks'])+' '+' '.join(' '.join(row) for t in p['tables'] for row in t),'notes':p['notes'],'tables':[{'rows':len(t),'columns':max(map(len,t),default=0),'cells':t} for t in p['tables']]} for p in doc['pages']]}

def check_evidence(issue,source):
    errors=[]; evidence=issue.get('evidence')
    if evidence is None:return errors
    if not isinstance(evidence,list) or not evidence:return ['evidence phải có ít nhất một trích dẫn']
    for e in evidence:
        if not isinstance(e,dict):errors.append('evidence không phải object');continue
        layer=e.get('layer');page=e.get('page')
        if layer=='metadata':text=' '.join(f'{k}: {v}' for k,v in source['metadata'].items())
        elif layer in ('display','notes'):
            p=next((p for p in source['pages'] if p['page']==page),None)
            if p is None:errors.append(f'không có trang {page}');continue
            text=p[layer]
        else:errors.append('layer chỉ là display, notes hoặc metadata');continue
        if not match_quote(e.get('quote',''),text):errors.append(f'trích dẫn không có trong lớp {layer}, trang {page}')
    return errors

DISCLOSURE=re.compile(r'rò rỉ|tiết lộ|lộ (?:bí mật|thông tin)|ghi chú.{0,50}nội bộ|chia sẻ.{0,40}(?:ra ngoài|bên ngoài)',re.I)

def priority_errors(issue,source):
    if issue.get('group')!='gui':return []
    text=' '.join(str(issue.get(k,'')) for k in ('title','problem','why','fix'))
    if not DISCLOSURE.search(text):return []
    proof=issue.get('audience_evidence',[])
    if not isinstance(proof,list):return ['audience_evidence phải là danh sách']
    for e in proof:
        if check_evidence({'evidence':[e]},source):continue
        q=norm(e.get('quote',''))
        if re.search(r'(?:gửi|phát hành|trình bày|chia sẻ).{0,100}(?:khách hàng|đối tác|công khai|bên ngoài)',q) and not re.search(r'\b(?:nếu|không|chưa|dự kiến)\b',q):return []
    return ['nhận định tiết lộ/bảo mật chưa có bằng chứng người nhận thực tế ngoài phạm vi cho phép; dùng nen có điều kiện/câu hỏi hoặc bỏ, không gui']

def claim_errors(issue,source):
    errors=[];text=' '.join(str(issue.get(k,'')) for k in ('title','problem','why'))
    fix=str(issue.get('fix',''));slide_nums={int(n) for n in re.findall(r'\d+',str(issue.get('slides','')))}
    pages=[p for p in source['pages'] if p['page'] in slide_nums]
    if re.search(r'mâu thuẫn|không nhất quán',text,re.I) and re.search(r'(sửa|đổi|thay|thống nhất).{0,90}(thành|theo|là)',fix,re.I) and not re.search(r'xác nhận|xác minh|đối chiếu|làm rõ',fix,re.I):
        errors.append('Mâu thuẫn cần xác nhận giá trị đúng; không tự chọn một phía để viết thay.')
    if issue.get('group')=='gui' and (issue.get('where')=='metadata' or re.search(r'metadata.{0,35}(tiêu đề|title)',text,re.I)):
        proof=issue.get('impact_evidence',[])
        valid=[e for e in proof if not check_evidence({'evidence':[e]},source)] if isinstance(proof,list) else []
        if not any(re.search(r'(hệ thống|cổng|tìm kiếm).{0,70}(lấy|hiển thị|sử dụng).{0,70}(metadata|thuộc tính|title)',str(e.get('quote','')),re.I) for e in valid):
            errors.append('Metadata title khác nội dung chưa chứng minh tác động bắt buộc sửa trước gửi; dùng nen hoặc đưa impact_evidence cụ thể từ nguồn.')
    if issue.get('group')=='trinh-bay' and re.search(r'tiếng Anh|bản EN|song ngữ',text,re.I) and pages and all(not notes_only_english(p['display']) for p in pages) and any(notes_only_english(p['notes']) for p in pages):
        errors.append('Tiếng Anh chỉ nằm trong notes chưa chứng minh lỗi trình bày; không coi độ dài/bản dịch notes là lỗi hiển thị.')
    if issue.get('group')=='gui' and re.search(r'(deadline|hạn|mốc).{0,100}đã qua|quá hạn|chậm tiến độ',text,re.I):
        scope=' '.join(p['display']+' '+p['notes'] for p in pages)
        if not re.search(r'chưa (?:hoàn thành|xong|triển khai)|còn đang|đang (?:triển khai|thực hiện|xử lý)|không đạt|trễ hạn|quá hạn',scope,re.I):
            errors.append('Ngày kế hoạch đã qua nhưng chưa có bằng chứng việc còn chưa hoàn thành; chỉ hỏi cập nhật tình trạng, không kết luận quá hạn/bắt buộc sửa.')
    return errors

def notes_only_english(text):
    words=re.findall(r'[a-z]+',text.lower());return sum(w in {'the','and','with','for','this','that','are','you','we','will','from','their','your','into','our','these','which'} for w in words)>=4

def details_errors(details,source):
    errors=[]
    for item in details.get('page_reviews',[]):
        text=item.get('observation','');p=next((p for p in source['pages'] if p['page']==item.get('page')),None)
        if p and re.search(r'tiếng Anh|bản EN|song ngữ',text,re.I) and notes_only_english(p['notes']) and not notes_only_english(p['display']) and not re.search(r'ghi chú|notes',text,re.I):
            errors.append(f"page_reviews trang {p['page']}: phần tiếng Anh chỉ nằm trong notes, không được coi là chữ hiển thị")
    for item in details.get('scorecard',[]):
        text=item.get('rationale','');pages=[p for p in source['pages'] if p['page'] in item.get('slides',[])]
        if pages and re.search(r'tiếng Anh|bản EN|song ngữ',text,re.I) and any(notes_only_english(p['notes']) for p in pages) and not any(notes_only_english(p['display']) for p in pages) and not re.search(r'ghi chú|notes',text,re.I):
            errors.append('scorecard: không trừ điểm hiển thị vì bản tiếng Anh chỉ nằm trong notes')
    return errors
