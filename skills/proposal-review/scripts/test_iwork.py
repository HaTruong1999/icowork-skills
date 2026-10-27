import unittest, tempfile, json, subprocess, sys, zipfile
from pathlib import Path
SCRIPT=Path(__file__).with_name('iwork.py')
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
if __name__=='__main__':unittest.main()
