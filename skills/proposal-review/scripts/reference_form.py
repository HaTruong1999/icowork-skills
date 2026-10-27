"""Populate the user's exact reference form without inventing review content."""
from pathlib import Path
import re,base64,json
from bs4 import BeautifulSoup

def render(content_html,mdt,title,script_path,report_data=None):
    root=Path(script_path).resolve().parent.parent
    doc=BeautifulSoup((root/'assets/reference.html').read_text(),'html.parser')
    content=BeautifulSoup(content_html,'html.parser')
    sections={re.sub(r'^\d+\.\s*','',s.h2.get_text()):s for s in content.select('main > section') if s.h2}
    issues=content.select('article.issue');total=len(issues)
    summary=sections.get('Kết luận');strengths=sections.get('Điểm tốt')
    # Keep reference styling and all twelve sections. Never retain sample review facts.
    doc.title.string=title
    header=doc.select_one('header.form-head');header.h1.string=title
    header.select_one('.form-id').string='Proposal-review-v5'
    filename=re.search(r'trên file (.+)\.$',mdt,re.M)
    day=re.search(r'Đánh giá ngày ([\d/]+)',mdt)
    for row in header.select('.meta > div'):
        key=row.dt.get_text();row.dd.clear()
        row.dd.string=filename.group(1) if key=='Tệp tài liệu' and filename else day.group(1) if key=='Ngày review' and day else '—'
    conclusion=doc.select_one('#ket-luan')
    scale=conclusion.select_one('.decision-scale');scale.replace_with(content.select_one('.decision-scale'))
    verdict=conclusion.select_one('.verdict');verdict.clear()
    verdict.append(BeautifulSoup('<div class="score"><div class="num">—</div><div class="of">/ 10 · chưa chấm điểm</div></div><div class="conclusion-copy"></div>','html.parser'))
    target=verdict.select_one('.conclusion-copy')
    if summary:
        for el in list(summary.select('[data-source-line]')):target.append(el)
    chips=content.select_one('.review-counts')
    if chips:target.append(chips)
    # Fields in the reference use the original groups, not an invented severity scale.
    counts={k:sum(k in x.get('class',[]) for x in issues) for k in ('crit','major','minor')}
    level={'crit':'Cần sửa trước khi gửi','major':'Cần sửa trước khi trình bày','minor':'Nên bổ sung'}
    orig_ids={}
    for issue in issues:
        orig=issue.get('id');orig_ids[orig]=issue
    findings=doc.select_one('#van-de');heading=findings.h2.extract();findings.clear();findings.append(heading)
    filters=content.select_one('.filters')
    if filters:findings.append(filters)
    for issue in issues:findings.append(issue)
    # Every source line stays visible, including strengths, priority and unverified notes.
    good=doc.select_one('#diem-manh');head=good.h2.extract();good.clear();good.append(head)
    if strengths:
        ul=strengths.find('ul')
        if ul:good.append(ul)
    else:good.append(BeautifulSoup('<p class="lede">Chưa có nội dung đánh giá điểm mạnh.</p>','html.parser'))
    # Build a page map from explicit locations; no finding is inferred from a thumbnail.
    bypage={}
    for issue in issues:
        first=issue.select_one('.review-text').get_text(' ',strip=True)
        titletext=issue.select_one('strong').get_text(' ',strip=True) if issue.select_one('strong') else first
        location=titletext.rsplit('(',1)[-1].rstrip(').') if '(' in titletext else ''
        if any(k in location.lower() for k in ('toàn','metadata','thuộc tính')):continue
        for n in set(map(int,re.findall(r'\d+',location))):
            if 0<n<1000:bypage.setdefault(n,[]).append(issue)
    # Images are added only from a source-hashed manifest in report_data.
    page_count=max(bypage,default=0)
    mapping=doc.select_one('#ban-do .strip');mapping.clear()
    slidebody=doc.select_one('#tung-slide tbody');slidebody.clear()
    for n in range(1,page_count+1):
        related=bypage.get(n,[]);rank=next((k for k in ('crit','major','minor') if any(k in i.get('class',[]) for i in related)),'minor')
        mapping.append(BeautifulSoup(f'<a class="tile {rank}" href="#s{n}">{n}</a>','html.parser'))
        tr=doc.new_tag('tr',id=f's{n}');td=doc.new_tag('td',attrs={'class':'n'});td.string=str(n);tr.append(td)
        imagecell=doc.new_tag('td');imagecell.string=f'Trang/slide {n}'
        tr.append(imagecell);severity=doc.new_tag('td');severity.string=level[rank] if related else 'Chưa có phát hiện riêng';tr.append(severity)
        details=doc.new_tag('td')
        for i in related:
            a=doc.new_tag('a',href='#'+i['id']);a.string=i.select_one('strong').get_text(' ',strip=True) if i.select_one('strong') else 'Xem nhận xét';details.append(a);details.append(doc.new_tag('br'))
        if not related:details.string='Không suy ra đã kiểm chứng đầy đủ trang này.'
        tr.append(details);slidebody.append(tr)
    for k,txt in [('l-crit',level['crit']),('l-major',level['major']),('l-minor',level['minor'])]:doc.select_one('.legend .'+k).string=txt
    doc.select_one('#ban-do .lede').string='Bấm vào số trang/slide để xem tham chiếu. Bản đồ chỉ tổng hợp vị trí được nêu trong kết quả review.'
    # Scores, questions, proposed restructuring are blank rather than copied from example.
    for row in doc.select('#tieu-chi .crit-row'):
        row.select_one('.crit-score').string='—'
        row.select_one('.crit-note').string='Chưa có điểm và căn cứ chấm trong kết quả review.'
        row.select_one('.bar i')['style']='width:0'
        small=row.select_one('small')
        if small:small.string='Chưa xác định trọng số'
    doc.select_one('#tieu-chi .lede').string='Giữ khung chấm điểm của mẫu; chưa gán điểm khi kết quả review không có dữ liệu chấm.'
    for ident in ('cau-hoi','cau-truc'):
        sec=doc.find(id=ident);h=sec.h2.extract();sec.clear();sec.append(h);p=doc.new_tag('p',attrs={'class':'lede'});p.string='Chưa có nội dung riêng trong kết quả review hiện tại.';sec.append(p)
    # Tracker contains every issue and original fix verbatim; no invented owner/deadline.
    tbody=doc.select_one('#hanh-dong tbody');tbody.clear()
    for i,issue in enumerate(issues,1):
        text=issue.get_text(' ',strip=True);fix=text.split('Sửa:',1)[-1].strip() if 'Sửa:' in text else 'Xem yêu cầu trong nhận xét.'
        tr=doc.new_tag('tr')
        values=[str(i),fix,'—','—','—']
        for value in values:
            td=doc.new_tag('td');td.string=value;tr.append(td)
        td=doc.new_tag('td');select=doc.new_tag('select',attrs={'aria-label':f'Trạng thái mục {i}'})
        for name in ['Mở','Đang xử lý','Đã sửa','Không đồng ý']:
            op=doc.new_tag('option');op.string=name;select.append(op)
        td.append(select);tr.append(td);td=doc.new_tag('td',attrs={'contenteditable':'true','aria-label':f'Phản hồi mục {i}'});tr.append(td);tbody.append(tr)
    note=doc.select_one('#hanh-dong .lede');note.string='Theo dõi tất cả nhận xét. Phụ trách và hạn để trống khi chưa được giao. Nội dung nhập chỉ giữ trong lần mở trang hiện tại.'
    message=doc.select_one('#msg');message.clear()
    for name in ('Ưu tiên','Chưa kiểm chứng'):
        sec=sections.get(name)
        if sec:
            h=doc.new_tag('h3');h.string=name;message.append(h)
            for el in list(sec.select('[data-source-line]')):message.append(el)
    doc.select_one('#phan-hoi h2').string='10. Ưu tiên và nội dung chưa kiểm chứng'
    doc.select_one('#phan-hoi .lede').string='Giữ nguyên các nội dung bổ sung từ kết quả review.'
    history=doc.select_one('#lich-su tbody');history.clear();tr=doc.new_tag('tr')
    for value in ['—',day.group(1) if day else '—','—','Xem kết luận review','—',f'{total} phát hiện, giữ đủ nội dung']:
        td=doc.new_tag('td');td.string=value;tr.append(td)
    history.append(tr)
    for p in doc.select('#xac-nhan .sig-meta'):p.string='........................................'
    doc.select_one('footer.foot').clear();doc.select_one('footer.foot').string='Bố cục theo mẫu người dùng cung cấp. Nội dung từ kết quả proposal-review; không sao chép nhận xét, điểm, người phụ trách hoặc deadline của bản mẫu.'
    # Bring content-preserving adapters and the working group-filter behavior.
    extra=doc.new_tag('style');extra.string='''.review-text{line-height:1.8}.review-text>strong:first-child{display:block;margin-bottom:10px;font-size:1.04rem}.field{display:block;margin-top:12px}.field.fix{background:var(--good-bg);padding:10px 12px;border-radius:6px}.legacy-line{margin:10px 0}.note-card{padding:16px 20px;margin-top:16px}.note-card summary{cursor:pointer}.source-number{font-weight:800;color:var(--muted);margin-bottom:6px}.issue[hidden]{display:none}.msg{white-space:normal}.msg h3{margin:18px 0 10px}@media print{.issue[hidden]{display:block!important}}''';doc.head.append(extra)
    for scr in doc.find_all('script'):scr.decompose()
    js=content.find('script')
    if js:
        # Reference tracker and copy behavior, plus working issue filters.
        js.string=(js.string or '')+''';(function(){var sels=document.querySelectorAll('.tracker select');function update(){var n=Array.from(sels).filter(function(s){return s.value==='Đã sửa'||s.value==='Không đồng ý'}).length;document.getElementById('progText').textContent='Đã xử lý '+n+'/'+sels.length;document.getElementById('progBar').style.width=(sels.length?n/sels.length*100:0)+'%'}sels.forEach(function(s){s.addEventListener('change',update)});update();document.getElementById('copyBtn').addEventListener('click',function(){if(navigator.clipboard)navigator.clipboard.writeText(document.getElementById('msg').innerText)})})();''';doc.body.append(js)
    if report_data: populate_details(doc,report_data)
    apply_interactive_ui(doc)
    return str(doc)

def populate_details(doc,data):
    """Model-authored full report; deterministic scores, references and image provenance."""
    def tag(name,text=None,**attrs):
        e=doc.new_tag(name,attrs=attrs)
        if text is not None:e.string=str(text)
        return e
    meta=data.get('metadata',{});mapping={'Người trình':'presenter','Đơn vị trình':'department','Phiên bản':'version','Loại review':'review_type','Nội dung xin duyệt':'request_summary'}
    for row in doc.select('.meta > div'):
        key=row.dt.get_text()
        if key in mapping:row.dd.string=str(meta.get(mapping[key]) or '—')
        elif key=='Vòng review':row.dd.string='Lần chạy hiện tại'
    criteria=data['scorecard'];weight=sum(float(x['weight']) for x in criteria)
    if len(criteria)!=8 or weight<=0 or any(not 0<=float(x['score'])<=10 or float(x['weight'])<=0 for x in criteria):raise ValueError('Invalid scorecard: need eight valid scores and positive relative weights')
    score=sum(float(x['score'])*float(x['weight']) for x in criteria)/weight
    doc.select_one('.score .num').string=f'{score:.1f}'.replace('.',',');doc.select_one('.score .of').string='/ 10 · đánh giá của reviewer'
    card=doc.select_one('#tieu-chi .criteria');card.clear()
    for item in criteria:
        row=tag('div',**{'class':'crit-row'});name=tag('div',item['name'],**{'class':'crit-name'});name.append(tag('small',f'Trọng số {float(item["weight"])/weight*100:.1f}%'));row.append(name)
        bar=tag('div',**{'class':'bar'});bar.append(tag('i',style=f'width:{float(item["score"])*10}%;background:var(--major)'));row.append(bar);row.append(tag('div',item['score'],**{'class':'crit-score'}));row.append(tag('div',item['rationale']+' · Trang/slide '+str(item.get('slides',[])),**{'class':'crit-note'}));card.append(row)
    doc.select_one('#tieu-chi .lede').string='Điểm do reviewer đánh giá, tính trung bình có trọng số; không phải số liệu của tác giả.'+(' Trọng số tương đối của model được chuẩn hóa về 100% khi hiển thị.' if abs(weight-100)>1e-6 else '')
    pages=data['page_reviews'];manifest=data.get('render_manifest',{});images={p['page']:p for p in manifest.get('pages',[])}
    if manifest and manifest.get('source_sha256')!=data['source_sha256']:raise ValueError('Image manifest source mismatch')
    import hashlib
    issue_ids={x['id']:i for i,x in enumerate(data['final_issues'],1)}
    body=doc.select_one('#tung-slide tbody');body.clear();strip=doc.select_one('#ban-do .strip');strip.clear()
    for page in pages:
        n=int(page['page']);ids=page.get('issue_ids',[])
        if any(x not in issue_ids for x in ids):raise ValueError('Unknown issue ID in page review')
        tr=tag('tr',id=f's{n}');tr.append(tag('td',n,**{'class':'n'}));cell=tag('td')
        img=images.get(n)
        if img:
            imagepath=Path(img['image']);raw=imagepath.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=img['sha256']:raise ValueError('Image hash mismatch')
            uri='data:image/png;base64,'+base64.b64encode(raw).decode();cell.append(tag('img',src=uri,alt=f'Trang/slide {n}',loading='lazy'))
        cell.append(tag('div',page['title'],style='margin-top:6px;font-weight:600'));tr.append(cell)
        related=[x for x in data['final_issues'] if x['id'] in ids];level=next((g for g in ['gui','trinh-bay','nen'] if any(x['group']==g for x in related)),None);cls={'gui':'crit','trinh-bay':'major','nen':'minor'}.get(level,'minor')
        tr.append(tag('td',{'gui':'Sửa trước khi gửi','trinh-bay':'Sửa trước trình bày','nen':'Nên bổ sung'}.get(level,'Không gắn phát hiện')))
        detail=tag('td',page['observation']);chips=tag('div',**{'class':'chips'})
        for id_ in ids:chips.append(tag('a',id_,href=f'#issue-{issue_ids[id_]}',**{'class':'chip '+{'gui':'c','trinh-bay':'M','nen':'m'}[next(x['group'] for x in related if x['id']==id_)]}))
        detail.append(chips);tr.append(detail);body.append(tr);strip.append(tag('a',n,href=f'#s{n}',**{'class':'tile '+cls}))
    if len(pages)!=manifest.get('page_count',len(pages)) or sorted(p['page'] for p in pages)!=list(range(1,len(pages)+1)):raise ValueError('Missing or duplicated page reviews')
    doc.select_one('#ban-do .lede').string='Bản đồ tổng hợp nhận xét từng trang/slide và mức ưu tiên của các phát hiện đã qua kiểm chứng.'
    questions=doc.select_one('#cau-hoi');h=questions.h2.extract();questions.clear();questions.append(h);ol=tag('ol',**{'class':'qs'})
    for q in data['questions']:li=tag('li');li.append(tag('div',q['text']));ol.append(li)
    questions.append(ol)
    actions=data['actions'];byid={x['issue_id']:x for x in actions}
    if set(byid)!=set(issue_ids) or len(actions)!=len(issue_ids):raise ValueError('Actions must cover every final issue exactly once')
    rows=doc.select('#hanh-dong tbody tr')
    for issue,row in zip(data['final_issues'],rows):
        action=byid[issue['id']];cells=row.find_all('td');cells[1].string=action['task'];cells[2].string=action.get('owner') or '—';cells[3].string=action.get('collaborators') or '—';cells[4].string=action.get('deadline') or '—'
    structure=doc.select_one('#cau-truc');h=structure.h2.extract();structure.clear();structure.append(h);structure.append(tag('p','Đề xuất của reviewer cho bản trình lại.',**{'class':'lede'}));flow=tag('div',**{'class':'flow'})
    for n,item in enumerate(data['proposed_structure'],1):
        step=tag('div',**{'class':'step'+(' new' if item.get('is_new') else '')});step.append(tag('div',n,**{'class':'n'}));step.append(tag('h3',item['title']));step.append(tag('p',item['content']));flow.append(step)
    structure.append(flow)
    feedback=doc.select_one('#phan-hoi');feedback.h2.string='10. Phản hồi gửi người trình';feedback.select_one('.lede').string='Dự thảo do reviewer đề xuất, chưa gửi.'
    message=doc.select_one('#msg');preserved=list(message.contents);message.clear();message.append(tag('p',data['response_draft'],style='white-space:pre-wrap'))
    for e in preserved:message.append(e)
    last=doc.select_one('#lich-su tbody tr');cells=last.find_all('td');cells[0].string='1';cells[2].string='Lần chạy hiện tại';cells[4].string=f'{score:.1f}';cells[5].string=f'Model: {data.get("model","—")} · {len(issue_ids)} phát hiện'
    dispositions=data.get('review_dispositions',[])
    if dispositions:
        panel=tag('details',**{'class':'card note-card'});panel.append(tag('summary',f'{len(dispositions)} nhận định chưa được giữ sau phản biện — xem đầy đủ'))
        for disposition in dispositions:
            issue=disposition['issue'];decision=disposition['decision'];item=tag('div',style='padding:16px;border-top:1px solid var(--rule)');item.append(tag('h3',issue['id']+' · '+issue['title']))
            for key,label in [('quote','Nguyên văn'),('problem','Hiện trạng'),('why','Ảnh hưởng'),('fix','Yêu cầu đề xuất ban đầu')]:
                if issue.get(key):item.append(tag('p',label+': '+issue[key]))
            item.append(tag('p','Kết quả phản biện: '+str(decision.get('ket_luan','KHONG_CHAC'))+' · '+str(decision.get('ly_do',issue.get('reason','')))))
            panel.append(item)
        doc.select_one('#van-de').append(panel)
    doc.select_one('footer.foot').string='Review bằng '+data.get('model','model được chỉ định')+'. Ảnh toàn trang được render từ đúng file nguồn; không cắt ảnh. Điểm số và cấu trúc trình lại là nhận định của reviewer. Người phụ trách/hạn chưa được giao để trống. '

def apply_interactive_ui(doc):
    """User-authorized editing, severity tags, compact footer; shared by all outputs."""
    def make_editable(element,key,label,placeholder='Nhập nội dung'):
        element['contenteditable']='true';element['data-edit-key']=key;element['aria-label']=label;element['data-placeholder']=placeholder;element['spellcheck']='false';element['role']='textbox';element['aria-multiline']='true'
        classes=element.get('class',[])
        if 'editable-field' not in classes:classes.append('editable-field')
        element['class']=classes
    for i,row in enumerate(doc.select('.meta > div')):
        make_editable(row.dd,f'meta-{i}',row.dt.get_text(' ',strip=True))
    for i,row in enumerate(doc.select('#hanh-dong tbody tr')):
        cells=row.find_all('td')
        for j in (2,3,4,6):
            if j<len(cells):make_editable(cells[j],f'action-{i}-{j}',f'Mục {i+1}: '+{2:'phụ trách',3:'phối hợp',4:'hạn',6:'phản hồi'}[j])
        if row.select_one('select'):row.select_one('select')['data-edit-key']=f'action-{i}-status'
    feedback=doc.select_one('#msg > p') or doc.select_one('#msg')
    if feedback:make_editable(feedback,'feedback-draft','Phản hồi gửi người trình','Nhập phản hồi')
    for i,card in enumerate(doc.select('#xac-nhan .card')):
        label=card.h3.get_text(' ',strip=True)
        area=card.select_one('.lines')
        if area:
            area.clear();make_editable(area,f'confirmation-{i}-opinion',label,'Nhập ý kiến hoặc xác nhận')
        for j,field in enumerate(card.select('.sig-meta')):make_editable(field,f'confirmation-{i}-meta-{j}',f'{label}: thông tin ký xác nhận')
        sig=card.select_one('.sig-area')
        if sig:make_editable(sig,f'confirmation-{i}-signature',f'{label}: họ tên','Nhập họ tên người xác nhận')
    for i,cell in enumerate(doc.select('#lich-su td')):
        if cell.get_text(strip=True) in ('','—'):make_editable(cell,f'history-{i}','Thông tin lịch sử review')
    for i,el in enumerate(doc.select('td,dd,.fill,.crit-score,.score .num')):
        if el.get_text(strip=True) in ('','—') and not el.find(['img','select','input']) and not el.get('contenteditable'):
            make_editable(el,f'blank-{i}','Thông tin bổ sung')
    for row in doc.select('#tung-slide tbody tr'):
        cells=row.find_all('td',recursive=False)
        if len(cells)<3:continue
        cell=cells[2];label=cell.get_text(' ',strip=True)
        cls='crit' if 'trước khi gửi' in label.lower() else 'major' if 'trước trình' in label.lower() or 'trước khi trình' in label.lower() else 'minor' if 'bổ sung' in label.lower() else 'neutral'
        cell.clear();span=doc.new_tag('span',attrs={'class':'severity-tag '+cls});span.string=label;cell.append(span)
    tracker_note=doc.select_one('#hanh-dong .lede')
    if tracker_note:tracker_note.string='Sửa trực tiếp người phụ trách, hạn xử lý và phản hồi. Dùng Lưu bản HTML để lưu một bản có chỉnh sửa.'
    hint=doc.new_tag('p',attrs={'class':'decision-hint'});hint.string='Tự chọn theo kết quả review. Bạn có thể đọc và chọn lại kết luận.'
    doc.select_one('.decision-scale').insert_after(hint)
    footer=doc.select_one('footer.foot')
    if footer:footer.clear();footer.string='Đánh giá bằng Coding Assistant.'
    toolbar=doc.new_tag('div',attrs={'class':'edit-toolbar'})
    button=doc.new_tag('button',type='button',id='saveEditedHtml');button.string='Lưu bản HTML';toolbar.append(button)
    state=doc.new_tag('span',attrs={'id':'editSaveState','role':'status','aria-live':'polite'});state.string='Bấm vào các ô để chỉnh sửa';toolbar.append(state)
    doc.select_one('header.form-head').append(toolbar)
    style=doc.new_tag('style');style.string='''
.decision-scale .opt{cursor:pointer;position:relative}.decision-scale .opt input{position:absolute;opacity:0;width:1px;height:1px}.decision-scale .opt:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:3px}.decision-hint{font-size:.85rem;color:var(--muted);margin:10px 0 0}.severity-tag{display:inline-flex;align-items:center;gap:6px;padding:5px 9px;border-radius:6px;font-size:.78rem;line-height:1.5;font-weight:650;border:1px solid transparent}.severity-tag::before{content:"";width:6px;height:6px;flex:none;border-radius:50%;background:currentColor}.severity-tag.crit{color:var(--crit);background:var(--crit-bg)}.severity-tag.major{color:var(--major);background:var(--major-bg)}.severity-tag.minor{color:var(--minor);background:var(--minor-bg)}.severity-tag.neutral{color:var(--muted);background:var(--soft)}.editable-field{border-radius:4px;outline:none;min-height:1.5em;transition:background .12s,box-shadow .12s}.editable-field:hover{background:var(--soft);box-shadow:0 0 0 1px var(--rule)}.editable-field:focus{background:var(--surface);box-shadow:0 0 0 2px var(--accent);outline:none}.editable-field:empty::before{content:attr(data-placeholder);color:var(--muted);opacity:.6;pointer-events:none}.editable-field[contenteditable]{cursor:text}.sign .lines.editable-field{min-height:140px;line-height:30px;padding:2px 8px;background-image:repeating-linear-gradient(to bottom,transparent 0,transparent 29px,var(--rule) 29px,var(--rule) 30px);white-space:pre-wrap}.sign .sig-area.editable-field{min-height:64px;height:auto;padding:10px 8px;white-space:pre-wrap}.msg>.editable-field{white-space:pre-wrap;padding:8px;min-height:110px}.edit-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:14px;border-top:1px solid var(--rule);padding-top:16px;margin-top:20px;font-size:.83rem;color:var(--muted)}.edit-toolbar button{font:inherit;font-weight:600;border:1px solid var(--rule);background:var(--soft);color:var(--ink);border-radius:6px;padding:8px 12px;cursor:pointer}.edit-toolbar button:hover{border-color:var(--accent);color:var(--accent)}@media print{.edit-toolbar{display:none}.editable-field:empty::before{content:""}.editable-field{box-shadow:none!important}.severity-tag{print-color-adjust:exact;-webkit-print-color-adjust:exact}}
''';doc.head.append(style)
    script=doc.new_tag('script');script.string=r'''
(function(){
 var fields=Array.from(document.querySelectorAll('[data-edit-key]')), status=document.getElementById('editSaveState');
 var storageKey='proposal-review-edits-v2:'+location.pathname, edits={};
 function notify(text){if(status)status.textContent=text;}
 function syncDecision(el){el.querySelectorAll('.opt').forEach(function(label){var input=label.querySelector('input');label.classList.toggle('on',input.checked);label.querySelector('.box').textContent=input.checked?'✓':'';});}
 function readField(el){if(el.dataset.editType==='decision'){var checked=el.querySelector('input:checked');return checked?checked.value:null;}return el.tagName==='SELECT'?el.value:el.innerHTML;}
 function writeField(el,value){if(el.dataset.editType==='decision'){el.querySelectorAll('input').forEach(function(input){input.checked=input.value===String(value)});syncDecision(el);}else if(el.tagName==='SELECT')el.value=value;else el.innerHTML=value;}
 function snapshot(){var data={};fields.forEach(function(el){data[el.dataset.editKey]=readField(el);});return data;}
 var defaults=snapshot();
 function save(event){var el=event&&event.currentTarget;if(el&&el.dataset.editKey){var key=el.dataset.editKey,value=readField(el);if(el.dataset.editType==='decision')syncDecision(el);if(value===defaults[key])delete edits[key];else edits[key]=value;}try{localStorage.setItem(storageKey,JSON.stringify(edits));notify('Đã lưu chỉnh sửa trong trình duyệt');}catch(e){notify('Dùng “Lưu bản HTML” để giữ chỉnh sửa');}}
 // An exported file carries its edits in the DOM and does not load older browser drafts.
 if(!document.documentElement.hasAttribute('data-exported-edits')){
  try{var stored=JSON.parse(localStorage.getItem(storageKey)||'null');if(stored){edits=stored;fields.forEach(function(el){if(Object.prototype.hasOwnProperty.call(stored,el.dataset.editKey)){writeField(el,stored[el.dataset.editKey]);}});notify('Đã khôi phục chỉnh sửa trước đó');}}catch(e){}
 }
 fields.forEach(function(el){
  el.addEventListener(el.tagName==='SELECT'||el.dataset.editType==='decision'?'change':'input',save);
  if(el.tagName!=='SELECT'&&el.dataset.editType!=='decision')el.addEventListener('focus',function(){var t=el.textContent.trim();if(t==='—'||(t&&/^[.\s]+$/.test(t)))el.textContent='';});
  if(el.tagName!=='SELECT'&&el.dataset.editType!=='decision')el.addEventListener('paste',function(e){e.preventDefault();var text=(e.clipboardData||window.clipboardData).getData('text/plain');document.execCommand('insertText',false,text);});
 });
 document.getElementById('saveEditedHtml').addEventListener('click',function(){
  save();var clone=document.documentElement.cloneNode(true);clone.setAttribute('data-exported-edits','true');
  document.querySelectorAll('select[data-edit-key]').forEach(function(el){var target=Array.from(clone.querySelectorAll('select[data-edit-key]')).find(function(x){return x.dataset.editKey===el.dataset.editKey;});if(target)Array.from(target.options).forEach(function(option){if(option.value===el.value)option.setAttribute('selected','');else option.removeAttribute('selected');});});
  document.querySelectorAll('input[name="review-decision"]').forEach(function(input){var target=clone.querySelector('#'+input.id);if(input.checked)target.setAttribute('checked','');else target.removeAttribute('checked');});
  var blob=new Blob(['<!doctype html>
'+clone.outerHTML],{type:'text/html;charset=utf-8'});var url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=(decodeURIComponent(location.pathname).split('/').pop()||'Phieu_review.html').replace(/[.]html?$/i,'_da_chinh_sua.html');a.click();setTimeout(function(){URL.revokeObjectURL(url);},3000);notify('Đã xuất bản HTML có chỉnh sửa');
 });
 document.querySelectorAll('.tracker select').forEach(function(el){el.dispatchEvent(new Event('change'));});
})();
'''
    # Escape the literal line break inside the JavaScript Blob string.
    script.string=script.string.replace("'<!doctype html>\n'", "'<!doctype html>\\n'")
    doc.body.append(script)
