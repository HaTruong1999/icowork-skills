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
if __name__=='__main__':unittest.main()
