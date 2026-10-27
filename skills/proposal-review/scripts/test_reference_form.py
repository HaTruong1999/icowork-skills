import copy,importlib.util,unittest
from pathlib import Path
from bs4 import BeautifulSoup
p=Path(__file__).with_name('review.py');spec=importlib.util.spec_from_file_location('review_form',p);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
MD='''# Đánh giá: Tài liệu thử\n\n## Kết luận\n\nGửi được sau khi sửa 1 mục.\n\n## Điểm tốt\n\n- Điểm tốt thử nghiệm.\n\n## Cần sửa trước khi gửi\n\n1. **Số liệu chưa thống nhất (slide 1).** Có hai giá trị. Nguyên văn: "42". Vì sao: Khó đối chiếu. Sửa: Xác nhận lại nguồn.\n\n## Ưu tiên\n\n- Sửa mục 1.\n\n## Chưa kiểm chứng\n\n- Đánh giá ngày 26/10/2026 trên file Test.pdf.\n'''
class FormTests(unittest.TestCase):
 def data(self):
  return {'source_sha256':'abc','final_issues':[{'id':'I1','group':'gui'}],'scorecard':[{'name':str(i),'weight':w,'score':i,'rationale':'Lý do thử','slides':[1]} for i,w in enumerate([10,20,15,10,15,15,10,5])],'page_reviews':[{'page':1,'title':'Trang đầu','observation':'Mô tả thử','issue_ids':['I1']}],'render_manifest':{'source_sha256':'abc','page_count':1,'pages':[]},'questions':[{'text':'Nguồn số liệu là gì?'}],'actions':[{'issue_id':'I1','task':'Xác nhận nguồn','owner':None,'collaborators':None,'deadline':None}],'proposed_structure':[{'title':'Mục tiêu','content':'Đề xuất thử','is_new':False}],'response_draft':'Dự thảo thử','model':'vnptai/coding-assistant'}
 def test_twelve_sections_and_no_example_facts(self):
  s=BeautifulSoup(r.md_to_html(MD,'Tài liệu thử',self.data()),'html.parser');self.assertEqual(len(s.select('main>section')),12);self.assertNotIn('A Dũng Anh',s.get_text());self.assertNotIn('28/10/2026',s.get_text());self.assertEqual(len(s.select('.tracker tbody tr')),1)
 def test_weighted_score(self):
  d=self.data();expected=sum(x['weight']*x['score'] for x in d['scorecard'])/100;s=BeautifulSoup(r.md_to_html(MD,'Test',d),'html.parser');self.assertEqual(s.select_one('.score .num').text,f'{expected:.1f}'.replace('.',','))
 def test_relative_weights_are_normalized(self):
  d=self.data()
  for x in d['scorecard']:x['weight']*=.9
  s=BeautifulSoup(r.md_to_html(MD,'Test',d),'html.parser');self.assertIn('chuẩn hóa',s.select_one('#tieu-chi .lede').text)
  expected=sum(x['score']*x['weight'] for x in d['scorecard'])/sum(x['weight'] for x in d['scorecard']);self.assertEqual(s.select_one('.score .num').text,f'{expected:.1f}'.replace('.',','))
 def test_missing_page_rejected(self):
  d=self.data();d['render_manifest']['page_count']=2
  with self.assertRaisesRegex(ValueError,'Missing'):r.md_to_html(MD,'Test',d)
 def test_missing_action_rejected(self):
  d=self.data();d['actions']=[]
  with self.assertRaisesRegex(ValueError,'Actions'):r.md_to_html(MD,'Test',d)
 def test_unknown_reference_rejected(self):
  d=self.data();d['page_reviews'][0]['issue_ids']=['I9']
  with self.assertRaisesRegex(ValueError,'Unknown'):r.md_to_html(MD,'Test',d)
 def test_wrong_image_source_rejected(self):
  d=self.data();d['render_manifest']['source_sha256']='wrong'
  with self.assertRaisesRegex(ValueError,'manifest'):r.md_to_html(MD,'Test',d)
if __name__=='__main__':unittest.main()
