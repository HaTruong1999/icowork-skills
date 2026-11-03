import unittest, tempfile, json, subprocess, sys, shutil, zipfile
from pathlib import Path
SCRIPT=Path(__file__).with_name('iwork.py')
REVIEW=Path(__file__).with_name('review.py')
class Checkpoints(unittest.TestCase):
 def run_cli(self,*args):
  value=args[args.index('--output')+1] if '--output' in args else args[args.index('--work')+1] if '--work' in args else None
  cwd=Path(value).parent if value is not None else None
  return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],capture_output=True,text=True,cwd=cwd)
 def test_rejects_directory_as_source(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.run_cli('init','--source',d,'--output',Path(d)/'out');self.assertNotEqual(r.returncode,0);self.assertIn('never an _review folder',r.stderr)
 def test_resume_survives_cwd_and_rejects_changed_source(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'source with spaces.pdf'
   import fitz
   doc=fitz.open();page=doc.new_page();page.insert_text((72,72),'VNPT source');doc.save(src);doc.close()
   out=d/'output with spaces';r=self.run_cli('init','--source',src,'--output',out);self.assertEqual(r.returncode,0,r.stderr);state=json.loads((out/'session.json').read_text());self.assertEqual(state['phase'],'candidates');self.assertTrue((out/'TASK.md').exists())
   # A changed copy must never reuse candidates or continue with stale evidence.
   Path(state['source']).write_bytes(b'changed');r=self.run_cli('next','--work',out);self.assertNotEqual(r.returncode,0);self.assertIn('Source changed',r.stderr);self.assertEqual(json.loads((out/'session.json').read_text())['phase'],'candidates')
 def test_doctor_recovers_prepared_hashes_after_workspace_moved(self):
  with tempfile.TemporaryDirectory() as root:
   root=Path(root);loc1=root/'loc1';loc1.mkdir();src=loc1/'source.pdf'
   import fitz
   doc=fitz.open();page=doc.new_page();page.insert_text((72,72),'VNPT source');doc.save(src);doc.close()
   out=loc1/'out';r=self.run_cli('init','--source',src,'--output',out);self.assertEqual(r.returncode,0,r.stderr)
   self.assertEqual(json.loads((out/'session.json').read_text())['phase'],'candidates')
   # Simulate the sandbox remounting the whole workspace under a new absolute path.
   loc2=root/'loc2';loc2.mkdir();moved=loc2/'out';shutil.move(str(out),str(moved))
   r=self.run_cli('next','--work',moved);self.assertNotEqual(r.returncode,0);self.assertIn('Prepared evidence changed',r.stderr)
   r=self.run_cli('doctor','--work',moved);self.assertEqual(r.returncode,0,r.stderr)
   state=json.loads((moved/'session.json').read_text())
   for p in state['prepared_hashes']:self.assertTrue(Path(p).is_relative_to(moved.resolve()),p)
   # next must no longer trip on the stale-path check; it should instead ask the model
   # to fix the still-missing candidates.json, gracefully (not an uncaught crash).
   r=self.run_cli('next','--work',moved);self.assertEqual(r.returncode,0,r.stderr);self.assertNotIn('Prepared evidence changed',r.stderr+r.stdout)
   state=json.loads((moved/'session.json').read_text())
   self.assertEqual(state['phase'],'candidates');self.assertEqual(state['repairs'].get('candidates_error'),1)
 def test_guard_blocks_direct_review_call_in_iwork_workspace(self):
  import os
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'doc.pdf'
   import fitz
   doc=fitz.open();page=doc.new_page();page.insert_text((72,72),'VNPT doc');doc.save(src);doc.close()
   (d/'session.json').write_text(json.dumps({'mode':'iwork-native-model'}))
   r=subprocess.run([sys.executable,str(REVIEW),'prepare',str(src)],capture_output=True,text=True,cwd=d)
   self.assertNotEqual(r.returncode,0);self.assertIn('iwork.py',r.stderr)
   env={**os.environ,'IWORK_DRIVER':'1'}
   r=subprocess.run([sys.executable,str(REVIEW),'prepare',str(src)],capture_output=True,text=True,cwd=d,env=env)
   self.assertEqual(r.returncode,0,r.stderr)

class FullLoop(unittest.TestCase):
 """init → candidates → verify → critique → details → complete, bằng JSON viết tay như model sẽ viết."""
 def run_cli(self,cwd,*args):
  r=subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],capture_output=True,text=True,cwd=cwd,timeout=300)
  return r.returncode,r.stdout+r.stderr
 def test_full_loop_with_repairs(self):
  import fitz
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'de_xuat.pdf'
   doc=fitz.open()
   for text in ('De xuat trien khai nen tang X cho 3 don vi. Ngan sach 5 ty dong.','Ke hoach: hoan thanh trong quy 4/2026. Chua co phan tich rui ro.'):
    page=doc.new_page();page.insert_text((72,72),text)
   doc.save(src);doc.close()
   code,out=self.run_cli(d,'init','--source',src,'--output','out','--today','2026-10-30')
   self.assertEqual(code,0,out);self.assertIn('=== CHƯA XONG (phase=candidates)',out)
   self.assertRegex(out,r'python3? \\"out/next\.py')   # lệnh tương đối, giống hệt ở mọi phiên; không có đường dẫn skill
   r=subprocess.run([sys.executable,'out/next.py'],cwd=d,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);self.assertIn('=== CHƯA XONG',r.stdout)
   w=d/'out';wd=w/'_review'/'de_xuat';nxt=('next','--work','out')
   (wd/'candidates.json').write_text(json.dumps({'doc_title':'Đề xuất nền tảng X','verdict':'Cần bổ sung.','strengths':[{'text':'Nêu rõ ngân sách','slides':'1'}],
    'issues':[{'id':'I1','title':'Thiếu phân tích rủi ro','group':'nen','slides':[2],'quote':'Chua co phan tich rui ro',
     'problem':'Trang 2 tự nêu chưa có phân tích rủi ro.','why':'Lãnh đạo khó cân nhắc khi chưa thấy rủi ro.','fix':'Bổ sung phân tích rủi ro chính và biện pháp giảm thiểu.'}],'notes':[]},ensure_ascii=False))
   code,out=self.run_cli(d,*nxt);self.assertEqual(code,0,out);self.assertIn('phase=critique',out);self.assertIn('sub-agent',(w/'TASK.md').read_text(encoding='utf8'))
   crit={'I1':{'ket_luan':'DUNG','ly_do':'Nguồn tự nêu thiếu.','counterevidence':{'locations':['trang 1','trang 2'],'finding':'Không thấy phân tích rủi ro ở trang 1.'}}}   # tối giản: driver tự điền a, b, checks, effect
   (wd/'critique.json').write_text(json.dumps(crit,ensure_ascii=False))
   code,out=self.run_cli(d,*nxt);self.assertEqual(code,0,out);self.assertIn('phase=details',out)   # thiếu _meta: driver tự ghi same_context, không bắt sửa
   self.assertEqual(json.loads((wd/'critique.json').read_text(encoding='utf8'))['_meta']['mode'],'same_context')
   (wd/'report-details.json').write_text('{"scorecard": [}')                                      # JSON hỏng -> giao sửa
   code,out=self.run_cli(d,*nxt);self.assertEqual(code,0,out);self.assertIn('không phải JSON hợp lệ',(w/'TASK.md').read_text(encoding='utf8'));self.assertNotIn('Traceback',out)
   names=['Đề xuất rõ ràng','Chính xác, nhất quán','Bằng chứng','Đối tượng','Hiệu quả, chi phí','Kế hoạch, nguồn lực','Rủi ro','Cấu trúc']
   details={'metadata':{'presenter':None,'department':None,'version':None,'review_type':None,'request_summary':None},
    'scorecard':[{'name':n,'weight':10 if i<4 else 15,'score':6,'rationale':'Đánh giá theo nội dung hai trang nguồn.','slides':[1,2]} for i,n in enumerate(names)],
    'page_reviews':[{'page':1,'title':'Đề xuất','observation':'Nêu phạm vi và ngân sách.','issue_ids':[]},{'page':2,'title':'Kế hoạch','observation':'Nêu mốc, tự nhận chưa có phân tích rủi ro.','issue_ids':['I1']}],
    'questions':[{'text':'Rủi ro chính và cách giảm thiểu là gì?','issue_ids':['I1']}],
    'actions':[{'issue_id':'I1','task':'Bổ sung phân tích rủi ro.','owner':None,'collaborators':None,'deadline':None}],
    'proposed_structure':[{'title':'Rủi ro','content':'Thêm mục rủi ro sau kế hoạch','is_new':True,'rationale':'Đề xuất của reviewer'}],
    'response_draft':'Đề nghị bổ sung phân tích rủi ro trước khi trình.','report_checks':{'notes':[]}}
   (wd/'report-details.json').write_text(json.dumps(details,ensure_ascii=False))
   code,out=self.run_cli(d,*nxt);self.assertEqual(code,0,out);self.assertIn('HOÀN TẤT',out)
   st=json.loads((w/'session.json').read_text());self.assertEqual(st['phase'],'complete');self.assertTrue(st['all_pass'])
   html=(w/'Danh_gia_de_xuat.html').read_text(encoding='utf8')
   self.assertIn('Thiếu phân tích rủi ro',html);self.assertIn('cùng phiên',html)
   self.assertEqual(sorted(x.name for x in w.iterdir()),sorted(['Danh_gia_de_xuat.html','_review','de_xuat.pdf','session.json']))
 def test_no_issues_skips_critique_repair(self):
  import fitz
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'ok.pdf';doc=fitz.open();doc.new_page().insert_text((72,72),'Bao cao day du, ro rang.');doc.save(src);doc.close()
   code,out=self.run_cli(d,'init','--source',src,'--output','out','--today','2026-10-30');self.assertEqual(code,0,out)
   wd=d/'out'/'_review'/'ok'
   (wd/'candidates.json').write_text(json.dumps({'doc_title':'Báo cáo','verdict':'Gửi được.','strengths':[],'issues':[],'notes':[]},ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertEqual(code,0,out)
   code,out=self.run_cli(d,'next','--work','out');self.assertEqual(code,0,out)
   self.assertIn('phase=details',out);self.assertNotIn('Bổ sung phản biện',out)
 def test_minimal_details_only_scorecard_is_enough(self):
  """Model chỉ viết điểm 8 tiêu chí; nhận xét từng trang, hành động, câu hỏi, phản hồi do driver dựng từ final.json."""
  import fitz
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'dx.pdf';doc=fitz.open()
   for text in ('De xuat nen tang X. Ngan sach 5 ty dong.','Ke hoach quy 4/2026. Chua co phan tich rui ro.'):doc.new_page().insert_text((72,72),text)
   doc.save(src);doc.close()
   code,out=self.run_cli(d,'init','--source',src,'--output','out','--today','2026-10-30');self.assertEqual(code,0,out)
   w=d/'out';wd=w/'_review'/'dx'
   (wd/'candidates.json').write_text(json.dumps({'doc_title':'X','verdict':'.','strengths':[],'issues':[
    {'id':'I1','title':'Thiếu phân tích rủi ro','group':'nen','slides':[2],'quote':'Chua co phan tich rui ro','problem':'Trang 2 tự nêu chưa có phân tích rủi ro.','why':'Khó cân nhắc.','fix':'Bổ sung phân tích rủi ro.'}],'notes':[]},ensure_ascii=False))
   self.run_cli(d,'next','--work','out')
   ok={k:True for k in ('title','problem','why','fix','priority','location')}
   (wd/'critique.json').write_text(json.dumps({'I1':{'a':'x','b':'y','ket_luan':'DUNG','ly_do':'z','checks':ok,'counterevidence':{'locations':['trang 1','trang 2'],'finding':'Đối chiếu hai trang.','effect':'supports'}}},ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertIn('phase=details',out)
   names=['Đề xuất rõ ràng','Chính xác, nhất quán','Bằng chứng','Đối tượng, thị trường','Hiệu quả, chi phí','Kế hoạch, nguồn lực','Rủi ro','Cấu trúc trình bày']
   bad={'scorecard':[{'name':n,'score':6,'rationale':'Bám nội dung hai trang.','slides':[1]} for n in names[:7]]}
   (wd/'report-details.json').write_text(json.dumps(bad,ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertEqual(code,0,out);self.assertIn('đúng 8 mục',(w/'TASK.md').read_text(encoding='utf8'))
   good={'scorecard':[{'name':n,'score':6,'rationale':'Bám nội dung hai trang.','slides':[1]} for n in names]}
   (wd/'report-details.json').write_text(json.dumps(good,ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertEqual(code,0,out);self.assertIn('HOÀN TẤT',out)
   html=(w/'Danh_gia_dx.html').read_text(encoding='utf8')
   self.assertIn('Thiếu phân tích rủi ro',html);self.assertIn('Ke hoach quy 4/2026',html)   # nhận xét trang 2 do driver dựng từ nguồn
   self.assertEqual(json.loads((w/'session.json').read_text())['all_pass'],True)
 def test_heuristic_details_warning_does_not_block(self):
  import fitz
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'dx.pdf';doc=fitz.open()
   for text in ('De xuat nen tang X. Ngan sach 5 ty dong.','Ke hoach quy 4/2026. Chua co phan tich rui ro.'):doc.new_page().insert_text((72,72),text)
   doc.save(src);doc.close()
   code,out=self.run_cli(d,'init','--source',src,'--output','out','--today','2026-10-30');self.assertEqual(code,0,out)
   w=d/'out';wd=w/'_review'/'dx'
   bad='Thiếu hoàn toàn dự toán kinh phí chi tiết cho từng hạng mục triển khai nền tảng, không có bảng phân bổ ngân sách theo quý và không nêu nguồn vốn của dự án'
   (wd/'candidates.json').write_text(json.dumps({'doc_title':'X','verdict':'.','strengths':[],'issues':[
    {'id':'I1','title':'Thiếu phân tích rủi ro','group':'nen','slides':[2],'quote':'Chua co phan tich rui ro','problem':'Trang 2 tự nêu chưa có phân tích rủi ro.','why':'Khó cân nhắc.','fix':'Bổ sung phân tích rủi ro.'},
    {'id':'I2','title':bad,'group':'nen','slides':[1],'quote':'Ngan sach 5 ty dong','problem':bad+'.','why':'Khó duyệt.','fix':'Bổ sung dự toán.'}],'notes':[]},ensure_ascii=False))
   self.run_cli(d,'next','--work','out')
   ok={k:True for k in ('title','problem','why','fix','priority','location')}
   ce={'locations':['trang 1','trang 2'],'finding':'Đối chiếu hai trang.','effect':'supports'}
   (wd/'critique.json').write_text(json.dumps({'_meta':{'mode':'same_context'},'I1':{'a':'x','b':'y','ket_luan':'DUNG','ly_do':'z','checks':ok,'counterevidence':ce},
    'I2':{'a':'x','b':'y','ket_luan':'SAI','ly_do':'Trang 1 đã có ngân sách 5 tỷ đồng.','checks':ok,'counterevidence':ce}},ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertIn('phase=details',out)
   # Lý do chấm điểm nhắc lại nhận định đã bị phản biện loại: trước đây chặn cả lượt, nay chỉ cảnh báo.
   det={'scorecard':[{'name':f'Tiêu chí {i}','score':5,'rationale':bad,'slides':[1]} for i in range(1,9)]}
   (wd/'report-details.json').write_text(json.dumps(det,ensure_ascii=False))
   code,out=self.run_cli(d,'next','--work','out');self.assertEqual(code,0,out)
   self.assertIn('HOÀN TẤT',out);self.assertIn('LƯU Ý',out)
 def test_no_api_path_left(self):
  root=Path(__file__).resolve().parent.parent
  self.assertFalse((root/'scripts'/'run_coding_full.py').exists())
  for f in root.rglob('*.py'):
   if f.name=='test_iwork.py':continue
   self.assertNotIn('api-genai',f.read_text(encoding='utf8'),f)

class BootstrapQuiet(unittest.TestCase):
    """Thật (Windows): pip in đường dẫn môi trường ~/.cache, model chép đường dẫn đó vào lệnh → iWork hỏi quyền."""
    def test_missing_libraries_error_never_exposes_environment_path(self):
        import builtins, importlib.util, io, os
        spec = importlib.util.spec_from_file_location('iw_boot', Path(__file__).with_name('iwork.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        real = builtins.__import__
        def fake(name, *a, **k):
            if name in ('bs4', 'fitz'): raise ImportError(name)
            return real(name, *a, **k)
        old = os.environ.get('IWORK_BOOTSTRAPPED'); os.environ['IWORK_BOOTSTRAPPED'] = '1'
        builtins.__import__ = fake
        try:
            with self.assertRaises(SystemExit) as ctx: m.bootstrap()
        finally:
            builtins.__import__ = real
            if old is None: os.environ.pop('IWORK_BOOTSTRAPPED', None)
            else: os.environ['IWORK_BOOTSTRAPPED'] = old
        msg = str(ctx.exception)
        self.assertIn('thiếu thư viện', msg); self.assertNotIn('.cache', msg); self.assertNotIn(str(Path.home()), msg)


class ShortcutLauncher(unittest.TestCase):
    """Thật (Windows): model gõ python "<skill>/scripts/next.py" (tệp không tồn tại) → iWork hỏi quyền. Tạo sẵn tệp đó cho chạy được."""
    def test_skill_scripts_next_py_runs_the_session_in_current_folder(self):
        import fitz
        here = Path(__file__).resolve().parent
        self.assertTrue((here / 'next.py').is_file())
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); src = d / 'dx.pdf'; doc = fitz.open(); doc.new_page().insert_text((72, 72), 'De xuat nen tang X. Ngan sach 5 ty dong.'); doc.save(src); doc.close()
            r = subprocess.run([sys.executable, str(here / 'iwork.py'), 'init', '--source', 'dx.pdf', '--output', 'review-output'], cwd=d, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            r = subprocess.run([sys.executable, str(here / 'next.py')], cwd=d, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn('WAITING_FOR_MODEL', r.stdout)
            with tempfile.TemporaryDirectory() as empty:
                r = subprocess.run([sys.executable, str(here / 'next.py')], cwd=empty, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0); self.assertIn('Chưa có phiên review', r.stdout + r.stderr)

if __name__=='__main__':unittest.main()
