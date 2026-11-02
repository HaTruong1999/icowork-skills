"""End-to-end tests for the iwork.py driver: start → advance → build → audit → finish.

Chạy: python3 scripts/test_iwork.py  (cần thư viện trong requirements.txt; các test render cần Chrome/Chromium).
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / 'scripts'))
from export_pdf import find_browser  # noqa: E402

HAS_BROWSER = bool(find_browser())
CSV = 'Ma,Cong viec,Don vi,Han,Trang thai\n1,Ra soat VM,VNPT Net,30/11/2026,Dang trien khai\n2,Quet log,KV1,15/12/2026,Chua bat dau\n'
PLAN = {'meta': {'ten': {'vi': 'Tiến độ VM', 'en': 'VM progress'}, 'ban': 'Bản 1 · 30/11/2026', 'computed': []},
        'outline': ['Bìa', 'Hai việc chính']}
COVER = {'mau': 'bia', 'the': 'Báo cáo', 'tieuDe': 'Tiến độ rà soát VM', 'phu': 'Theo bảng tiến độ', 'dong': 'VNPT Net'}
GOOD = {'mau': 'so-lieu', 'nhan': 'Kết quả', 'dauMuc': 'Kết quả', 'soMuc': '1', 'tieuDe': 'Hai việc *đang theo dõi*',
        'so': [{'so': '2', 'nhan': 'việc theo dõi', 'icon': 'lich'}, {'so': '1', 'nhan': 'việc đang triển khai', 'icon': 'ten-lua'},
               {'so': '1', 'nhan': 'việc chưa bắt đầu', 'icon': 'canh-bao'}], 'nguon': 'Nguồn: tiendo.csv'}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data, encoding='utf-8')


class Driver(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='rsh-test-'))
        write(self.tmp / 'tiendo.csv', CSV)
        self.work = self.tmp / 'out'

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, *args):
        r = subprocess.run([sys.executable, str(SKILL / 'iwork.py'), *args], cwd=self.tmp, capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout + r.stderr

    def state(self):
        return json.loads((self.work / 'iwork-state.json').read_text(encoding='utf-8'))

    def report(self):
        """report.json: ở gốc WORK khi đang làm, trong _work/ sau khi finish dọn."""
        for base in (self.work, self.work / '_work'):
            if (base / 'report.json').is_file():
                return json.loads((base / 'report.json').read_text(encoding='utf-8'))
        raise AssertionError('không thấy report.json')

    def step(self):
        return json.loads((self.work / 'job-step.json').read_text(encoding='utf-8'))

    def start(self, slide2=GOOD):
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out')
        self.assertEqual(code, 0, out)
        write(self.work / 'plan.json', PLAN)
        write(self.work / 'parts' / '01.json', COVER)
        if slide2 is not None:
            write(self.work / 'parts' / '02.json', slide2)
        return out

    def test_start_asks_for_notes_plan_and_never_says_done(self):
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('notes.md', out)
        self.assertIn('plan.json', out)
        self.assertIn('=== CHƯA XONG', out)
        # Commands use the relative WORK path so iWork doesn't prompt for permission.
        self.assertIn('python3 "out/advance.py"', out)      # launcher tương đối: agent không phải nhớ đường dẫn skill
        self.assertNotIn(str(SKILL), out.split('NEXT:')[-1] if 'NEXT:' in out else '')
        r = subprocess.run([sys.executable, 'out/advance.py'], cwd=self.tmp, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('=== CHƯA XONG', r.stdout)
        self.assertIn('BẢNG MẪU K7', out)               # thay cho việc đọc cả huong-dan-k7.md
        self.assertIn('so-lieu: so[]{so,nhan,icon}', out)
        self.assertNotIn('huong-dan-k7.md (mục 4-9)', out)

    @unittest.skipUnless(HAS_BROWSER, 'cần Chrome/Chromium để build')
    def test_theme_and_logo_are_applied_by_driver(self):
        import base64
        png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
        (self.tmp / 'logo.png').write_bytes(png)
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out', '--logo', 'logo.png', '--chan-trang', 'VNPT')
        self.assertEqual(code, 0, out)
        from k7_build import DEFAULT_THEME
        self.assertIn('GIAO DIỆN: ' + DEFAULT_THEME, out)
        write(self.work / 'plan.json', PLAN); write(self.work / 'parts' / '01.json', COVER); write(self.work / 'parts' / '02.json', GOOD)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        rep = self.report()
        self.assertEqual(rep['theme'], DEFAULT_THEME)
        self.assertTrue(rep['meta']['nhanDien']['anh'].startswith('data:image/png;base64,'))
        self.assertEqual(rep['meta']['nhanDien']['chanTrang'], 'VNPT')
        html = (self.work / 'out.html').read_text(encoding='utf-8')
        self.assertNotIn('"theme"', html.split('id="deck">', 1)[1][:2000])
        self.assertIn('data:image/png;base64,', html)

    @unittest.skipUnless(HAS_BROWSER, 'cần Chrome/Chromium để build')
    def test_builds_with_this_skills_theme(self):
        from k7_build import THEMES, DEFAULT_THEME
        self.assertEqual(len(THEMES), 1, 'mỗi skill chỉ mang một giao diện')
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('GIAO DIỆN: ' + DEFAULT_THEME, out)
        write(self.work / 'plan.json', PLAN); write(self.work / 'parts' / '01.json', COVER); write(self.work / 'parts' / '02.json', GOOD)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        self.assertEqual(self.report()['theme'], DEFAULT_THEME)
        marker = {'chung': '"chanTrang":"iView"', 'vnpt-ai': '"chanTrang": "VNPT AI"'}[DEFAULT_THEME]
        html = (self.work / 'out.html').read_text(encoding='utf-8')
        self.assertIn(marker.replace(' ', ''), html.replace(' ', ''))

    def test_bad_logo_rejected(self):
        write(self.tmp / 'logo.txt', 'x')
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out', '--logo', 'logo.txt')
        self.assertNotEqual(code, 0)
        self.assertIn('Logo phải là tệp ảnh', out)

    def test_missing_parts_lists_next_batch(self):
        self.start(slide2=None)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('out/parts/02.json', out)
        self.assertIn('=== CHƯA XONG', out)

    def test_structural_error_is_nonzero_and_names_field(self):
        bad = dict(GOOD, so=GOOD['so'][:2])          # mẫu so-lieu cần 3–6 ô
        self.start(slide2=bad)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 2, out)
        self.assertEqual(self.step()['status'], 'repairable_error')
        self.assertIn('· so', json.dumps(self.step(), ensure_ascii=False))
        self.assertIn('M4', json.dumps(self.step(), ensure_ascii=False))

    def test_hand_edited_state_is_detected(self):
        # Lượt chạy thật: agent hết lượt build rồi tự đặt failed_builds=0 trong iwork-state.json.
        self.start()
        st = self.state(); st['failed_builds'] = 0; st['note'] = 'reset'
        (self.work / 'iwork-state.json').write_text(json.dumps(st), encoding='utf-8')
        code, out = self.run_cli('advance', 'out')
        self.assertNotEqual(code, 0)
        self.assertIn('bị sửa ngoài driver', out)
        self.assertIn('=== DỪNG', out)

    def test_too_long_field_shows_text_and_chars_to_cut(self):
        long = 'việc theo dõi trong bảng tiến độ của hai đơn vị VNPT Net và KV1 tháng này'
        self.start(slide2=dict(GOOD, so=[dict(GOOD['so'][0], nhan=long)] + GOOD['so'][1:]))
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 2, out)
        err = [e for e in self.step()['errors'] if e.get('ma') == 'M2'][0]
        self.assertEqual(err['hien_tai'], long)
        self.assertIn(f'bớt ít nhất {len(long) - 56} ký tự', err['can_bot'])

    @unittest.skipUnless(HAS_BROWSER, 'cần Chrome/Chromium để build')
    def test_flat_deck_with_wrong_numbering_is_autofixed(self):
        self.start(slide2=dict(GOOD, soMuc='1.1', dauMuc='7 · Kết quả'))
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('TỰ SỬA', out)
        self.assertIn('HOÀN TẤT', out)
        fixed = [p for p in (self.work / '_work' / 'parts').glob('02.json')][0]
        slide = json.loads(fixed.read_text(encoding='utf-8'))
        self.assertEqual((slide['soMuc'], slide['dauMuc']), ('1', 'Kết quả'))

    def test_pre_render_errors_also_count_toward_cap(self):
        """Lỗi trước render (ở đây: đơn vị bịa ở bìa) cũng tính lượt build; không có bản nào để giao thì dừng hẳn."""
        bad_cover = dict(COVER, dong='Trung tâm Điều hành giả lập')
        self.start()
        for i in range(4):
            write(self.work / 'parts' / '01.json', dict(bad_cover, phu=f'Theo bảng tiến độ {i}'))
            code, out = self.run_cli('advance', 'out')
            self.assertNotEqual(code, 0)
        self.assertEqual(self.state()['failed_builds'], 4)
        self.assertEqual(self.step()['status'], 'blocked')
        self.assertIn('=== DỪNG', out)

    @unittest.skipUnless(HAS_BROWSER, 'cần Chrome/Chromium để build')
    def test_invented_number_then_no_progress_then_cap(self):
        invented = dict(GOOD, tieuDe='Đã rà soát *987* máy ảo', so=[dict(GOOD['so'][0], so='987')] + GOOD['so'][1:])
        self.start(slide2=invented)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 1, out)
        self.assertEqual(self.step()['status'], 'repairable_error')
        self.assertTrue(any('987' in e for e in self.step()['errors']), self.step())
        # Same content again: refused without rebuilding (this guard used to be dead code).
        history = len(list((self.work / 'build-history').glob('*.log'))) if (self.work / 'build-history').exists() else 0
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 1)
        self.assertIn('REPAIR_REQUIRED', out)
        self.assertEqual(history, len(list((self.work / 'build-history').glob('*.log'))) if (self.work / 'build-history').exists() else 0)
        # Trivial edits that keep the error: blocked after 4 consecutive failed builds.
        for i in range(2, 5):
            write(self.work / 'parts' / '02.json', dict(invented, nguon=f'Nguồn: tiendo.csv {i}'))
            code, out = self.run_cli('advance', 'out')
            self.assertEqual(code, 1, out)
            self.assertNotIn('Traceback', out)
        # Hết lượt: driver giao bản nháp đặt tên *_BAN_NHAP kèm cảnh báo, không bắt người dùng nhắn thêm.
        self.assertIn('BẢN NHÁP CÓ CẢNH BÁO', out)
        self.assertNotIn('=== DỪNG', out)
        delivery = json.loads((self.work / 'delivery.json').read_text(encoding='utf-8'))
        self.assertEqual(delivery['state'], 'draft-with-warnings')
        self.assertTrue(all('_BAN_NHAP' in o for o in delivery['outputs']), delivery)
        self.assertTrue(any('987' in w for w in delivery['warnings']), delivery)
        self.assertEqual(self.state()['phase'], 'complete_with_warnings')

    @unittest.skipUnless(HAS_BROWSER, 'cần Chrome/Chromium để build')
    def test_full_success_auto_audit_and_finish(self):
        """Build đạt → driver tự lập audit và finish trong cùng lệnh advance; model không phải viết audit."""
        self.start()
        write(self.work / 'stray-notes.txt', 'agent scratch')
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('HOÀN TẤT', out)
        self.assertNotIn('CHƯA XONG', out)
        self.assertEqual(self.state()['phase'], 'complete')
        top = sorted(p.name for p in self.work.iterdir())
        self.assertEqual(top, sorted(['_work', 'delivery.json', 'iwork-state.json', 'out.html', 'out.pdf']))
        delivery = json.loads((self.work / 'delivery.json').read_text(encoding='utf-8'))
        self.assertEqual(delivery['state'], 'complete')
        self.assertTrue(any('Chưa xem ảnh' in u for u in delivery['uncertainties']), delivery)
        self.assertEqual({r['so'] for r in delivery['doi_chieu_so']}, {'2', '1'})
        self.assertTrue(all(r['cau_nguon'] for r in delivery['doi_chieu_so']), delivery)
        # Logo đến sau khi đã giao: gắn vào bản cũ, build lại, tự hoàn tất lần nữa.
        import base64
        (self.tmp / 'logo.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='))
        code, out = self.run_cli('start', 'tiendo.csv', '--work', 'out', '--logo', 'logo.png')
        self.assertEqual(code, 0, out)
        self.assertIn('ĐÃ CẬP NHẬT LOGO', out)
        code, out = self.run_cli('advance', 'out')
        self.assertEqual(code, 0, out)
        self.assertIn('HOÀN TẤT', out)
        self.assertIn('data:image/png;base64,', (self.work / 'out.html').read_text(encoding='utf-8'))

    def test_work_prefix_with_session_folder_name_is_normalized(self):
        """Agent hay viết --work <tên thư mục phiên>/report-output: không được sinh thư mục lồng nhau."""
        session = self.tmp / 'sess-1'; session.mkdir()
        write(session / 'tiendo.csv', CSV)
        r = subprocess.run([sys.executable, str(SKILL / 'iwork.py'), 'start', 'tiendo.csv', '--work', 'sess-1/report-output'],
                           cwd=session, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((session / 'report-output' / 'iwork-state.json').is_file())
        self.assertFalse((session / 'sess-1').exists())


class AutoFix(unittest.TestCase):
    """Lỗi cơ học thấy ở lượt chạy thật (NOC): driver tự sửa thay vì tốn lượt build."""
    def drv(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('drv2', SKILL / 'iwork.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    def make(self, slides):
        tmp = Path(tempfile.mkdtemp(prefix='rsh-fix-')); self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / 'parts').mkdir()
        for i, s in enumerate(slides, 1):
            write(tmp / 'parts' / f'{i:02d}.json', s)
        return tmp

    def test_extra_label_field_is_merged_not_silently_dropped(self):
        m = self.drv()
        card = {'mau': 'the', 'dauMuc': 'A', 'soMuc': '1', 'tieuDe': 'x', 'the': [
            {'icon': 'giam', 't': '75,3%', 'nhan': 'Cảnh báo trùng giảm', 'd': 'Từ 85.000 xuống 21.000'},
            {'icon': 'cai-dat', 't': '1.150', 'nhan': 'Luật cảnh báo chuẩn hóa', 'd': ''}]}
        work = self.make([{'mau': 'bia', 'the': 'x', 'tieuDe': 'x'}, card])
        fixes = m.autofix_parts(work, ['a', 'b'], {'giam', 'cai-dat'})
        got = json.loads((work / 'parts' / '02.json').read_text(encoding='utf-8'))['the']
        self.assertEqual(got[0]['d'], 'Cảnh báo trùng giảm: Từ 85.000 xuống 21.000')
        self.assertEqual(got[1]['d'], 'Luật cảnh báo chuẩn hóa')
        self.assertTrue(all('nhan' not in x for x in got) and len(fixes) == 2)
        self.assertEqual(m.unknown_key_errors({'mau': 'the', 'tieuDe': 'x', 'the': [{'t': 'a', 'zzz': 'b'}], 'banLa': 1}).__len__(), 2)

    def test_table_rows_given_as_objects_become_cell_arrays(self):
        """Thật: model viết hang:[{"hang":[..]}] → JS khung dừng ở slide 8, 15 slide sau trắng trong PDF."""
        m = self.drv()
        table = {'mau': 'bang', 'dauMuc': 'A', 'soMuc': '1', 'tieuDe': 'x', 'cot': ['a', 'b', 'c'],
                 'hang': [{'hang': ['1', '2', '3']}, {'hang': ['4', '5']}, ['6', '7', '8']]}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, table])
        m.autofix_parts(work, ['a', 'b'], set())
        got = json.loads((work / 'parts' / '02.json').read_text(encoding='utf-8'))['hang']
        self.assertEqual(got, [['1', '2', '3'], ['4', '5', ''], ['6', '7', '8']])

    def test_unmet_tracker_rows_become_appendix_tables_built_by_driver(self):
        """Thật (War room): 13 dòng theo dõi chưa nêu → model lặp suy nghĩ khi tự dồn vào slide. Driver tự dựng phụ lục 2–5 hàng/slide."""
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, {'mau': 'so-lieu', 'tieuDe': 'y', 'so': []}, {'mau': 'cam-on', 'tieuDe': 'z'}])
        write(work / 'plan.json', {'meta': {'ten': {'vi': 'x'}}, 'outline': ['a', 'b', 'c']})
        rows = [{'kind': 'row', 'row': f'1.{k}', 'unit': 'VNPT IT', 'due': '26/10/2026', 'result': 'Đã có danh mục VM ' + 'x' * 120} for k in range(11)]
        note = m.add_coverage_slides(work, rows)
        self.assertIn('3 slide phụ lục', note)
        plan = json.loads((work / 'plan.json').read_text(encoding='utf-8'))
        self.assertEqual(len(plan['outline']), 6)
        parts = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 7)]
        self.assertEqual(parts[-1]['mau'], 'cam-on')
        sizes = [len(p['hang']) for p in parts if p['mau'] == 'bang']
        self.assertEqual(sorted(sizes), [3, 4, 4]); self.assertTrue(all(2 <= n <= 5 for n in sizes))
        self.assertTrue(all(len(c) <= 80 for p in parts if p['mau'] == 'bang' for r in p['hang'] for c in r))
        self.assertIsNone(m.add_coverage_slides(work, rows[:1]))

    def test_workpath_after_completion_points_to_state_folder(self):
        m = self.drv()
        top = Path(tempfile.mkdtemp(prefix='rsh-wp-')); self.addCleanup(shutil.rmtree, top, True)
        (top / '_work').mkdir(); write(top / 'iwork-state.json', {'phase': 'complete'})
        self.assertEqual(m.workpath(str(top / '_work')), top.resolve())

    def test_split_table_keeps_clean_titles_and_drops_invisible_solution_number(self):
        m = self.drv()
        rows = [[f'r{k}', 'a', 'b'] for k in range(7)]
        table = {'mau': 'bang', 'tieuDe': 'Tiến độ rà soát VM theo checklist ATTT (mục 9.a-9.f)', 'cot': ['x', 'y', 'z'], 'hang': rows}
        vd = {'mau': 'van-de', 'tieuDe': 'x', 'vanDe': {'t': 'a', 'y': ['1', '2'], 'so': '7', 'soNhan': 'n'}, 'giaiPhap': {'t': 'b', 'y': ['1', '2'], 'so': '4', 'soNhan': 'm'}}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, table, vd])
        write(work / 'plan.json', {'meta': {'ten': {'vi': 'x'}}, 'outline': ['a', 'b', 'c']})
        self.assertIn('chia bảng', m.split_long_tables(work))
        titles = json.loads((work / 'plan.json').read_text(encoding='utf-8'))['outline']
        self.assertEqual(len(titles), 4); self.assertNotIn('( (', titles[1]); self.assertTrue(titles[1].endswith('(1/2)'))
        self.assertEqual(sum(t.count('(') - t.count(')') for t in titles[1:3]), 0)
        m.autofix_parts(work, titles, set())
        got = json.loads((work / 'parts' / '04.json').read_text(encoding='utf-8'))
        self.assertNotIn('so', got['giaiPhap']); self.assertEqual(got['vanDe']['so'], '7')

    def test_long_source_gets_short_brief_with_line_pointers(self):
        m = self.drv()
        work = self.make([])
        body = '\n'.join(f'## Slide {k}\n' + ' '.join(f'từ{k}_{j}' for j in range(90)) for k in range(1, 41))
        (work / 'content.md').write_text('# NGUỒN 1\n\n- title: X\n\n' + body, encoding='utf-8')
        brief = m.make_brief(work)
        text = brief.read_text(encoding='utf-8')
        self.assertLess(len(text), 20000); self.assertIn('## Slide 40 (content.md dòng', text); self.assertIn('## Slide 1 (content.md dòng', text)
        short = self.make([]); (short / 'content.md').write_text('## Slide 1\nx\n## Slide 2\ny', encoding='utf-8')
        self.assertIsNone(m.make_brief(short))

    def test_plan_with_metadata_key_and_object_outline_is_repaired(self):
        """Thật (Hải Phòng): model viết plan.json với "metadata" và outline là object, không có meta.ten → build chặn, tốn lượt."""
        m = self.drv()
        work = self.make([])
        write(work / 'plan.json', {'metadata': {'title': 'Đề xuất CĐS Hải Phòng', 'totalSlides': 3},
                                   'outline': [{'slide': 1, 'type': 'cover', 'title': 'Bìa'}, {'slide': 2, 'title': 'Hiện trạng'}]})
        note = m.fix_plan(work)
        plan = json.loads((work / 'plan.json').read_text(encoding='utf-8'))
        self.assertEqual(plan['outline'], ['Bìa', 'Hiện trạng']); self.assertEqual(plan['meta']['ten']['vi'], 'Đề xuất CĐS Hải Phòng'); self.assertNotIn('metadata', plan)
        self.assertIn('metadata', note)

    def test_speaker_notes_are_composed_only_from_slide_text(self):
        """Người dùng báo HTML mất lời thoại, rồi cần đầy đủ chi tiết hơn: đủ từng ý, con số, nguồn, kết luận; chỉ dùng chữ trên slide."""
        m = self.drv()
        slides = [{'mau': 'bia', 'tieuDe': 'Báo cáo *War room*', 'phu': 'Rà soát an ninh', 'dong': 'VNPT IT, 24/10/2026'},
                  {'mau': 'so-lieu', 'tieuDe': 'Tổng quan', 'phu': 'Toàn Tập đoàn', 'so': [{'so': '7.949', 'nhan': 'VM toàn Tập đoàn'}, {'so': '450', 'nhan': 'VM VNPT Net'}], 'ketLuan': 'Đã rà soát xong', 'nguon': 'Nguồn: báo cáo 24/10'},
                  {'mau': 'bang', 'tieuDe': 'Tiến độ', 'cot': ['Đơn vị', 'Tổng VM', 'Hạn'], 'hang': [['VNPT Net', '496', '24/10'], ['VNPT AI', '464', '30/10']]},
                  {'mau': 'van-de', 'tieuDe': 'Sự cố', 'vanDe': {'t': 'Bị chiếm quyền', 'y': ['03 VCenter', '02 ESXi'], 'so': '5', 'soNhan': 'máy chủ'}, 'giaiPhap': {'t': 'Khắc phục', 'y': ['Gỡ mã độc']}},
                  {'mau': 'the', 'tieuDe': 'Ba ý', 'the': [{'t': 'An toàn', 'd': 'Kiểm soát truy cập'}, {'t': 'Sao lưu', 'd': 'Hằng ngày'}]},
                  {'mau': 'lo-trinh', 'tieuDe': 'Lộ trình', 'buoc': [{'tg': '2026', 't': 'Khởi động', 'd': 'Chọn đối tác'}]},
                  {'mau': 'cam-on', 'tieuDe': 'Cảm ơn', 'lienHe': [{'gt': 'www.vnpt.vn'}]}]
        n = [m.compose_loi_thoai(x) for x in slides]
        self.assertIn('Kính chào', n[0]); self.assertNotIn('*', n[0]); self.assertIn('VNPT IT, 24/10/2026', n[0])
        self.assertIn('Thứ nhất, VM toàn Tập đoàn: 7.949.', n[1]); self.assertIn('Thứ 2, VM VNPT Net: 450.', n[1])
        self.assertIn('Điều cần nhớ: Đã rà soát xong.', n[1]); self.assertIn('Nguồn số liệu: báo cáo 24/10.', n[1])
        self.assertIn('VNPT Net — Tổng VM: 496; Hạn: 24/10.', n[2]); self.assertIn('VNPT AI — Tổng VM: 464; Hạn: 30/10.', n[2])
        self.assertIn('- 03 VCenter.', n[3]); self.assertIn('Con số đáng chú ý: 5 máy chủ.', n[3]); self.assertIn('Về giải pháp: Khắc phục.', n[3])
        self.assertIn('Thứ nhất, An toàn: Kiểm soát truy cập.', n[4]); self.assertIn('Bước 1 (2026): Khởi động — Chọn đối tác.', n[5])
        self.assertIn('cảm ơn', n[6].lower()); self.assertIn('www.vnpt.vn', n[6])
        self.assertTrue(all(len(t) <= 1500 for t in n)); self.assertIn('\n', n[1])
        long = {'mau': 'the', 'tieuDe': 'Dài', 'ketLuan': 'Kết luận quan trọng', 'nguon': 'Nguồn: x', 'the': [{'t': f'Ý {k}', 'd': 'mô tả khá dài ' * 8} for k in range(1, 7)]}
        t = m.compose_loi_thoai(long); self.assertLessEqual(len(t), 1500); self.assertIn('Điều cần nhớ: Kết luận quan trọng.', t)   # quá dài thì bỏ nguồn trước, giữ kết luận

    def test_comma_separated_headers_are_not_one_invented_name(self):
        """Thật (War room, e2e): lời thoại "các cột: Data Center, Tổng Host, Đã Patch, Hạn" bị coi là một tên riêng không có trong nguồn."""
        import report
        rep = {'slides': [{'mau': 'bang', 'loiThoai': 'Bảng gồm các cột: Data Center, Tổng Host, Đã Patch, Hạn, Tình trạng.'}]}
        self.assertEqual(report.check_invented_names(rep, 'tong host da patch han tinh trang'), [])
        rep2 = {'slides': [{'mau': 'the', 'tieuDe': 'Nam Cần Thơ phụ trách'}]}
        self.assertTrue(report.check_invented_names(rep2, 'south'))

    def _source_deck(self, parts):
        """Nguồn 11 slide: ba slide ngăn phần (01, 02, 03) và nội dung dài; trả (work, slides báo cáo)."""
        m = self.drv()
        def body(n): return ' '.join(f'tukhoa{n}x{j}' for j in range(30)) + ' noi dung chi tiet cua slide nguon so ' + str(n)
        src = ['# NGUỒN 1: x.pptx\n', '## Slide 1\nBáo cáo', '## Slide 2\nNỘI DUNG 01 Định hướng 02 Đồng hành 03 Hợp tác triển khai',
               '## Slide 3\n01 ĐỊNH HƯỚNG CHIẾN LƯỢC', '## Slide 4\n' + body(4), '## Slide 5\n' + body(5), '## Slide 6\n02 ĐỒNG HÀNH THỰC HIỆN',
               '## Slide 7\n' + body(7), '## Slide 8\n' + body(8), '## Slide 9\n03 HỢP TÁC TRIỂN KHAI', '## Slide 10\n' + body(10), '## Slide 11\nCảm ơn']
        mk = lambda n, title: {'mau': 'so-lieu', 'tieuDe': title, 'so': [{'so': '1', 'nhan': ' '.join(f'tukhoa{n}x{j}' for j in range(12))}]}
        slides = parts(mk)
        work = self.make(slides)
        if src: (work / 'content.md').write_text('\n'.join(src), encoding='utf-8')
        write(work / 'plan.json', {'meta': {'ten': {'vi': 'x'}}, 'outline': [x['tieuDe'] for x in slides]})
        return m, work

    def test_chapter_position_follows_source_structure_even_when_titles_differ(self):
        """Cấu trúc phần quyết định trước: slide ngăn phần của file nguồn ("03 HỢP TÁC…") chỉ ra chương bị bỏ sót nằm ở đâu, không cần tiêu đề trùng từ."""
        toc = {'mau': 'muc-luc', 'tieuDe': 'Mục lục', 'muc': [{'t': 'Định hướng chiến lược', 'd': 'a'}, {'t': 'Đồng hành thực hiện', 'd': 'b'}, {'t': 'Hợp tác triển khai', 'd': 'c'}]}
        m, work = self._source_deck(lambda mk: [{'mau': 'bia', 'tieuDe': 'x'}, toc, {'mau': 'chuong', 'so': '01', 'tieuDe': 'Định hướng chiến lược'}, mk(4, 'Hiện trạng'), mk(5, 'Mục tiêu'),
                  {'mau': 'chuong', 'so': '02', 'tieuDe': 'Đồng hành thực hiện'}, mk(7, 'Kiến trúc'), mk(8, 'Ứng dụng'), mk(10, 'Lộ trình chi tiết'), {'mau': 'cam-on', 'tieuDe': 'Cảm ơn'}])
        note = m.add_missing_chapters(work)
        self.assertIn('Hợp tác triển khai', note)
        got = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 12)]
        k = [x['mau'] for x in got].index('chuong', 6)
        self.assertEqual(got[k]['so'], '03'); self.assertEqual(got[k + 1]['tieuDe'], 'Lộ trình chi tiết')
        plan = json.loads((work / 'plan.json').read_text(encoding='utf-8'))
        self.assertTrue(any('tự thêm' in x and 'theo cấu trúc file nguồn' in x for x in plan['meta']['canXacNhan']))

    def test_no_source_structure_means_chapters_are_whatever_the_deck_has(self):
        """Nguồn không có slide ngăn phần: driver không bịa thêm chương; mục lục không còn hứa phần không có (suy ra từ chương)."""
        toc = {'mau': 'muc-luc', 'tieuDe': 'Mục lục', 'muc': [{'t': 'Định hướng', 'd': 'a'}, {'t': 'Đồng hành', 'd': 'b'}, {'t': 'Kế hoạch tài chính', 'd': 'c'}]}
        m, work = self._source_deck(lambda mk: [{'mau': 'bia', 'tieuDe': 'x'}, toc, {'mau': 'chuong', 'so': '01', 'tieuDe': 'Định hướng'}, mk(4, 'Hiện trạng'),
                  {'mau': 'chuong', 'so': '02', 'tieuDe': 'Đồng hành'}, mk(7, 'Kiến trúc'), mk(10, 'Lộ trình')])
        (work / 'content.md').write_text('# NGUỒN 1: x.pptx\n## Slide 1\nBáo cáo không có slide ngăn phần', encoding='utf-8')
        self.assertIsNone(m.add_missing_chapters(work))                                  # không có cấu trúc nguồn: không chèn gì
        self.assertIn('bỏ slide mục lục', m.sync_toc_with_chapters(work))                # chỉ 2 chương: khung K7 không cho mục lục
        plan = json.loads((work / 'plan.json').read_text(encoding='utf-8'))
        self.assertEqual(len(plan['outline']), 6); self.assertNotIn('Mục lục', plan['outline'])
        self.assertTrue(any('bỏ slide mục lục' in x.lower() or 'Đã bỏ slide mục lục' in x for x in plan['meta']['canXacNhan']))
        self.assertIsNone(m.sync_toc_with_chapters(work))

    def test_table_of_contents_is_derived_from_chapters(self):
        m = self.drv()
        toc = {'mau': 'muc-luc', 'tieuDe': 'Mục lục', 'muc': [{'t': 'Phần tự nghĩ ra A', 'd': 'a'}, {'t': 'Phần tự nghĩ ra B', 'd': 'b'}, {'t': 'Phần tự nghĩ ra C', 'd': 'c'}, {'t': 'Phần D', 'd': 'd'}]}
        chap = lambda k, t: {'mau': 'chuong', 'so': str(k), 'tieuDe': t, 'phu': 'mô tả ' + t}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x', 'the': 'a'}, toc, chap(1, 'Hiện trạng'), {'mau': 'so-lieu', 'tieuDe': 'a', 'so': []}, chap(2, 'Giải pháp'), {'mau': 'so-lieu', 'tieuDe': 'b', 'so': []}, chap(3, 'Cam kết')])
        m.autofix_parts(work, ['a'] * 7, set(), '', '')
        got = json.loads((work / 'parts' / '02.json').read_text(encoding='utf-8'))
        self.assertEqual([x['t'] for x in got['muc']], ['Hiện trạng', 'Giải pháp', 'Cam kết'])
        short = {'mau': 'muc-luc', 'tieuDe': 'Mục lục', 'muc': [{'t': 'Hiện trạng gọn', 'd': 'a'}, {'t': 'Giải pháp', 'd': 'b'}, {'t': 'Cam kết VNPT', 'd': 'c'}]}   # viết gọn nhưng đúng phần: giữ chữ của model
        work2 = self.make([{'mau': 'bia', 'tieuDe': 'x', 'the': 'a'}, short, chap(1, 'Hiện trạng chi tiết'), {'mau': 'so-lieu', 'tieuDe': 'a', 'so': []}, chap(2, 'Giải pháp trọng tâm'), {'mau': 'so-lieu', 'tieuDe': 'b', 'so': []}, chap(3, 'Cam kết của VNPT')])
        m.autofix_parts(work2, ['a'] * 7, set(), '', '')
        self.assertEqual(json.loads((work2 / 'parts' / '02.json').read_text(encoding='utf-8'))['muc'][0]['t'], 'Hiện trạng gọn')

    def test_source_structure_finds_part_dividers_only(self):
        m = self.drv()
        work = self.make([])
        (work / 'content.md').write_text('# NGUỒN 1: x\n## Slide 1\n01 PHẦN MỘT\n## Slide 2\n2.1 NHÓM CÁC NHIỆM VỤ\n## Slide 3\n03 PHẦN BA\n', encoding='utf-8')
        _, div = m.source_structure(work)
        self.assertEqual(div, {1: 1, 3: 3})                                  # "2.1 …" là mục con, không phải slide ngăn phần
        (work / 'content.md').write_text('# NGUỒN 1: a\n## Slide 1\n01 A\n# NGUỒN 2: b\n## Slide 1\n01 B\n', encoding='utf-8')
        self.assertEqual(m.source_structure(work), ({}, {}))                 # nhiều nguồn: không dùng

    def test_cover_gets_label_instead_of_empty_oval(self):
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'Đề xuất đồng hành CĐS', 'phu': 'VNPT', 'dong': 'Hải Phòng, Tháng 10/2026'}])
        m.autofix_parts(work, ['a'], set(), '', '')
        self.assertEqual(json.loads((work / 'parts' / '01.json').read_text(encoding='utf-8'))['the'], 'Đề xuất · 2026')
        self.assertEqual(m.cover_label({'tieuDe': 'Số liệu quý'}, ''), 'Báo cáo điều hành')

    def test_empty_slide_detector_names_first_blank_slide(self):
        import re
        dom = ('<section class="muc-slide" id="slide-7"><div class="khung"><p>x</p></div></section>'
               '<section class="muc-slide" id="slide-8"><div class="muc-slide__dau"></div><div class="khung"></div><details></details></section>'
               '<section class="muc-slide" id="slide-9"><div class="khung"></div></section>')
        found = [int(n) for n in re.findall(r'<section[^>]*id="slide-(\d+)"(?:(?!</section>).)*?<div class="khung"></div>', dom, re.S)]
        self.assertEqual(found, [8, 9])

    def test_object_outline_is_normalized_to_titles(self):
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}])
        write(work / 'plan.json', {'meta': {'ten': 'x'}, 'outline': [{'tieuDe': 'Bìa'}, {'title': 'Hai', 'mau': 'the'}, {'noiDung': {'vi': 'Ba'}}, 'Bốn']})
        self.assertIn('danh sách tiêu đề', m.fix_plan(work))
        self.assertEqual(json.loads((work / 'plan.json').read_text(encoding='utf-8'))['outline'], ['Bìa', 'Hai', 'Ba', 'Bốn'])
        self.assertIsNone(m.fix_plan(work))

    def test_outline_grows_to_match_extra_parts(self):
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'Bìa'}, {'mau': 'the', 'tieuDe': 'Hai'}, {'mau': 'cam-on', 'tieuDe': {'vi': 'Cảm ơn'}}])
        write(work / 'plan.json', {'meta': {'ten': 'x'}, 'outline': ['Bìa', 'Hai']})
        self.assertIn('3 slide', m.extend_outline(work))
        self.assertEqual(json.loads((work / 'plan.json').read_text(encoding='utf-8'))['outline'], ['Bìa', 'Hai', 'Cảm ơn'])
        self.assertIsNone(m.extend_outline(work))

    def test_unknown_icon_is_replaced_by_closest_meaning(self):
        m = self.drv(); icons = {'tiet-kiem', 'bieu-do', 'nguoi', 'canh-bao'}
        work = self.make([{'mau': 'bia', 'the': 'x', 'tieuDe': 'x'}, {'mau': 'so-lieu', 'soMuc': '1', 'dauMuc': 'A', 'so': [{'so': '1', 'nhan': 'a', 'icon': 'tien-te'}, {'so': '2', 'nhan': 'b', 'icon': 'xyz-la'}]}])
        fixes = m.autofix_parts(work, ['a', 'b'], icons)
        got = json.loads((work / 'parts' / '02.json').read_text(encoding='utf-8'))['so']
        self.assertEqual(got[0]['icon'], 'tiet-kiem')
        self.assertIn(got[1]['icon'], icons)
        self.assertEqual(len(fixes), 2)

    def test_flat_numbering_is_normalized_not_rejected(self):
        m = self.drv()
        body = lambda d: {'mau': 'the', 'dauMuc': d, 'tieuDe': 'x'}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, body('1 · Tổng quan'), body('2 · Kết quả'), {'mau': 'cam-on', 'tieuDe': 'x'}])
        m.autofix_parts(work, list('abcd'), set())
        slides = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 5)]
        self.assertEqual([s.get('soMuc') for s in slides], [None, '1', '2', None])
        self.assertEqual(slides[1]['dauMuc'], 'Tổng quan')
        self.assertEqual(m.story_errors(slides, {'meta': {}}, ''), [])

    def test_chapter_deck_numbers_follow_chapter(self):
        m = self.drv()
        ch = lambda n: {'mau': 'chuong', 'so': n, 'tieuDe': 'x'}
        body = lambda d: {'mau': 'the', 'dauMuc': d, 'tieuDe': 'x'}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, body('0 · Tóm tắt'), ch('1'), body('Sự cố'), ch('2'), body('3 · Kết quả')])
        m.autofix_parts(work, list('abcdef'), set())
        slides = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 7)]
        self.assertEqual([s.get('dauMuc') for s in slides if s['mau'] == 'the'], ['Tóm tắt', '1 · Sự cố', '2 · Kết quả'])
        self.assertEqual(m.story_errors(slides, {'meta': {}}, ''), [])

    def test_bilingual_org_name_on_cover_is_not_flagged(self):
        from source_audit import identity_errors
        rep = {'meta': {}, 'slides': [{'mau': 'bia', 'the': {'vi': 'Báo cáo', 'en': 'Report'},
                                       'dong': {'vi': 'Trung tâm Điều hành mạng – VNPT Net', 'en': 'Network Operation Center – VNPT Net'}}]}
        self.assertEqual(identity_errors(rep, 'Trung tâm Điều hành mạng - VNPT Net báo cáo tháng 10'), [])
        self.assertTrue(identity_errors(rep, 'Báo cáo của đơn vị khác'))

    def test_near_miss_char_limit_is_only_a_reminder(self):
        from k7_build import soften
        near = {'muc': 'loi', 'ma': 'M2', 'vi_tri': 'slide 1 · muc.0.d · vi', 'y': 'Dài 42/40 ký tự'}
        far = {'muc': 'loi', 'ma': 'M2', 'vi_tri': 'slide 1 · tieuDe · vi', 'y': 'Dài 90/64 ký tự'}
        got = soften([near, far])
        self.assertEqual((got[0]['muc'], got[1]['muc']), ('nhac', 'loi'))

    def test_missing_nguon_is_filled_from_source_file(self):
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, {'mau': 'so-lieu', 'dauMuc': 'A', 'soMuc': '1', 'tieuDe': 'x', 'so': []}])
        m.autofix_parts(work, ['a', 'b'], set(), 'bao-cao.pdf (24/10/2026)')
        self.assertEqual(json.loads((work / 'parts' / '02.json').read_text(encoding='utf-8'))['nguon'], 'Nguồn: bao-cao.pdf (24/10/2026)')

    def test_missing_dauMuc_is_filled_from_label(self):
        m = self.drv()
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, {'mau': 'so-lieu', 'nhan': 'Kết quả chính', 'tieuDe': 'Hai *việc*'}, {'mau': 'the', 'tieuDe': 'Một *cụm* tiêu đề khá dài để kiểm cắt nhãn mục'}])
        m.autofix_parts(work, list('abc'), set())
        got = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')).get('dauMuc') for i in (2, 3)]
        self.assertEqual(got[0], 'Kết quả chính')
        self.assertTrue(got[1] and len(got[1]) <= 32 and '*' not in got[1])

    def test_table_of_contents_is_rebuilt_never_an_error(self):
        m = self.drv()
        toc = {'mau': 'muc-luc', 'tieuDe': 'Nội dung', 'muc': [{'t': f'P{i}'} for i in range(6)]}
        ch = lambda n, t: {'mau': 'chuong', 'so': n, 'tieuDe': t, 'phu': 'Một câu mô tả phần'}
        body = lambda d: {'mau': 'the', 'dauMuc': d, 'tieuDe': 'x'}
        work = self.make([{'mau': 'bia', 'tieuDe': 'x'}, toc, ch('1', 'Nền tảng'), body('A'), ch('2', 'Kết quả'), body('B'), ch('3', 'Kế hoạch'), body('C')])
        fixes = m.autofix_parts(work, list('abcdefgh'), set())
        slides = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 9)]
        self.assertEqual([x['t'] for x in slides[1]['muc']], ['Nền tảng', 'Kết quả', 'Kế hoạch'])
        self.assertTrue(any('mục lục dựng lại' in f for f in fixes))
        self.assertEqual(m.story_errors(slides, {'meta': {}}, ''), [])
        # một chương duy nhất + mục lục 6 mục: không lỗi, đánh số phẳng
        one = [{'mau': 'bia', 'tieuDe': 'x'}, dict(toc), ch('1', 'Nền tảng'), body('1 · A'), body('2 · B')]
        work = self.make(one); m.autofix_parts(work, list('abcde'), set())
        slides = [json.loads((work / 'parts' / f'{i:02d}.json').read_text(encoding='utf-8')) for i in range(1, 6)]
        self.assertEqual(m.story_errors(slides, {'meta': {}}, ''), [])
        self.assertEqual([s.get('soMuc') for s in slides[3:]], ['1', '2'])

    def test_phrase_copied_verbatim_from_source_is_never_blocked(self):
        m = self.drv()
        slides = [{'mau': 'bia', 'tieuDe': 'x'}, {'mau': 'the', 'soMuc': '1', 'dauMuc': 'A', 'tieuDe': 'Đã tích hợp thiết bị cho 2 vùng còn lại'}]
        source = 'Mục tiêu: tích hợp thiết bị cho 2 vùng còn lại; kết nối phiếu sự cố đang chờ.'
        self.assertEqual(m.story_errors(slides, {'meta': {}}, source), [])

    def test_atbm_specific_rules_do_not_fire_on_other_sources(self):
        m = self.drv()
        slides = [{'mau': 'bia', 'tieuDe': 'x'}, {'mau': 'the', 'soMuc': '1', 'dauMuc': 'A', 'tieuDe': 'Hoàn thành tích hợp vùng 1 và vùng 2 trong tháng'}]
        self.assertEqual(m.story_errors(slides, {'meta': {}}, 'Báo cáo NOC tháng 10: tổng 120 sự cố.'), [])


class Rules(unittest.TestCase):
    """Luật bắt các lỗi thấy ở lượt chạy thật bằng vnptai/coding-assistant."""
    def story(self, slides):
        import importlib.util
        spec = importlib.util.spec_from_file_location('drv', SKILL / 'iwork.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m.story_errors(slides, {'meta': {}}, '')

    def test_chapter_numbers_must_match_existing_chapters(self):
        ch = lambda n: {'mau': 'chuong', 'so': n, 'tieuDe': 'x'}
        body = lambda d: {'mau': 'the', 'dauMuc': d, 'tieuDe': 'x'}
        ok = [{'mau': 'bia'}, body('Tóm tắt điều hành'), ch('01'), body('1 · A'), ch('02'), body('2 · B'), {'mau': 'cam-on'}]
        self.assertEqual(self.story(ok), [])
        self.assertTrue(any('trước chương đầu' in e for e in self.story([{'mau': 'bia'}, body('0 · Tóm tắt'), ch('01'), body('1 · A'), ch('02'), body('2 · B')])))
        self.assertEqual(self.story([{'mau': 'bia'}, ch('1'), {'mau': 'the', 'soMuc': '1', 'dauMuc': 'A', 'tieuDe': 'x'}, {'mau': 'the', 'soMuc': '2', 'dauMuc': 'B', 'tieuDe': 'x'}]), [])   # một chương duy nhất = deck phẳng
        self.assertTrue(any('bắt đầu bằng 5' in e for e in self.story([ch('01'), body('1 · A'), ch('02'), body('2 · B'), body('5 · Kiến nghị')])))

    def test_flat_deck_with_toc_names_wrong_slides(self):
        body = lambda n, d='Kết quả': {'mau': 'the', 'dauMuc': d, 'soMuc': n, 'tieuDe': 'x'}
        toc = {'mau': 'muc-luc', 'muc': []}
        self.assertEqual(self.story([{'mau': 'bia'}, toc, body('1'), body('2'), {'mau': 'cam-on'}]), [])
        errs = self.story([{'mau': 'bia'}, toc, body('2'), body('3', '2 · B')])
        self.assertTrue(errs and 'slide 3 (parts/03.json): soMuc "2" → cần "1"' in errs[0] and 'slide 4' in errs[0], errs)

    def test_invented_org_in_closing_slide(self):
        from source_audit import identity_errors
        rep = {'meta': {}, 'slides': [{'mau': 'cam-on', 'tieuDe': 'Cảm ơn', 'lienHe': [{'nhan': 'Liên hệ', 'gt': 'Ban ATBM – VNPT Net'}]}]}
        self.assertTrue(identity_errors(rep, 'Báo cáo của VNPT Net'))
        self.assertEqual(identity_errors(rep, 'Ban ATBM – VNPT Net phụ trách'), [])

    def test_leak_check_ignores_copied_wording_with_source_numbers(self):
        import report
        other = {'slides': [{'mau': 'the', 'tieuDe': 'Mentor RAN 30, NMS 28', 'the': []}]}
        self.assertEqual(report.check_example_leak(other, 'Mentor RAN 30 máy; NMS 28 máy; báo cáo mới'), [])

    def test_audit_hash_error_states_expected_value(self):
        from source_audit import check_audit, sha
        with tempfile.TemporaryDirectory() as d:
            w = Path(d); write(w / 'report.json', {'meta': {}, 'slides': []}); write(w / 'content.md', 'x')
            errs = check_audit(w, {'report_sha256': 'sai'})
            self.assertTrue(any(sha(w / 'report.json') in e for e in errs))


class Example(unittest.TestCase):
    def test_example_passes_k7_structure_check(self):
        sys.path.insert(0, str(SKILL / 'scripts'))
        from k7_build import kiem_k7
        rep = json.loads((SKILL / 'examples/atbm-vm/report.json').read_text(encoding='utf-8'))
        errors = [x for x in kiem_k7(rep) if x['muc'] == 'loi']
        self.assertEqual(errors, [])

    def test_example_leak_check_flags_copy_but_not_self(self):
        import report
        rep = json.loads((SKILL / 'examples/atbm-vm/report.json').read_text(encoding='utf-8'))
        own = (SKILL / 'examples/atbm-vm/content.md').read_text(encoding='utf-8')
        self.assertEqual(report.check_example_leak(rep, own), [])
        other = {'slides': [{'mau': 'so-lieu', 'tieuDe': 'Công nghệ thông tin chiếm 62% trong 450 VM', 'so': []}]}
        self.assertTrue(report.check_example_leak(other, 'Báo cáo khác về mạng lõi, 12 trạm.'))

    def test_docx_export_reads_k7(self):
        from to_docx import build_docx
        import docx
        rep = json.loads((SKILL / 'examples/atbm-vm/report.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'x.docx'
            build_docx(rep, out)
            doc = docx.Document(out)
        headings = [p.text for p in doc.paragraphs if p.style.name == 'Heading 1']
        self.assertEqual(len(headings), len(rep['slides']) - 1 + 1)  # 8 slide nội dung + mục "Điểm cần xác nhận"
        self.assertEqual(len(doc.tables), 2)
        self.assertTrue(any('33,33%' in p.text for p in doc.paragraphs))


class Docs(unittest.TestCase):
    def test_report_skills_in_sync(self):
        tool = SKILL.parent.parent / 'tools' / 'sync_report_skills.py'
        if not tool.exists():
            self.skipTest('chỉ kiểm trong repo')
        r = subprocess.run([sys.executable, str(tool), '--check'], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + 'Chạy python3 tools/sync_report_skills.py')

    def test_references_exist_and_rules_agree(self):
        skill = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        guide = (SKILL / 'references/huong-dan-k7.md').read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)', skill):
            self.assertTrue((SKILL / link).exists(), link)
        self.assertNotIn('vi-du/', guide)
        self.assertNotIn('1,272`, `11.88%`.', guide.replace('(không đổi thành `1,272`, `11.88%`)', ''))
        self.assertIn('Giữ cách viết số của nguồn', skill)
        self.assertNotIn('API', skill.replace('không gọi API riêng', ''))


if __name__ == '__main__':
    unittest.main()
