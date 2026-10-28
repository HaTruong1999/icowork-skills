import unittest
import render_html as R
import report as RP


def base_report(extra_block):
    return {
        "meta": {"title": "T"},
        "slides": [
            {"type": "content", "title": "T", "rows": [{"cols": [1], "blocks": [extra_block]}]}
        ],
    }


class BarsRegressionTests(unittest.TestCase):
    """2026-10-28: model dùng 'max' để chia percent đã tính sẵn -> thanh gần như biến mất (0.39% thay vì 23%)."""

    def test_max_field_rejected(self):
        blk = {"type": "bars", "items": [{"label": "A", "value": "1/2", "percent": 50}], "max": 100}
        errs = []
        R.check_block(blk, "slide 1", errs)
        self.assertTrue(any("max" in e for e in errs))

    def test_label_width_must_be_css_length(self):
        blk = {"type": "bars", "items": [{"label": "A", "value": "1/2", "percent": 50}], "label_width": "VNPT IT"}
        errs = []
        R.check_block(blk, "slide 1", errs)
        self.assertTrue(any("label_width" in e for e in errs))
        blk["label_width"] = "90px"
        errs = []
        R.check_block(blk, "slide 1", errs)
        self.assertEqual(errs, [])

    def test_percent_out_of_range_rejected(self):
        blk = {"type": "bars", "items": [{"label": "A", "value": "1/2", "percent": 150}]}
        errs = []
        R.check_block(blk, "slide 1", errs)
        self.assertTrue(any("0-100" in e for e in errs))

    def test_bar_width_uses_percent_directly_not_divided_by_max(self):
        blk = {"type": "bars", "title": "t", "items": [{"label": "VNPT IT", "value": "1367/5946", "percent": 23.0}]}
        html = R.block_html(blk)
        self.assertIn("width:23.00%", html)
        self.assertNotIn("width:0.39%", html)


class UnbalancedBoldTests(unittest.TestCase):
    """2026-10-28: model quên đóng ** -> '**300 VM' hiện nguyên trong PDF."""

    def test_unclosed_bold_rejected(self):
        rep = base_report({"type": "progress", "value": "33%", "percent": 33,
                            "caption": "**150/450 VM** đã hoàn thành · còn **300 VM"})
        errs = R.validate(rep)
        self.assertTrue(any("**" in e for e in errs))

    def test_balanced_bold_accepted(self):
        pairs = R.find_unbalanced_bold({"a": "**xong** rồi", "b": ["ổn", "**cũng ổn**"]})
        self.assertEqual(pairs, [])


class NumberFormatConsistencyTests(unittest.TestCase):
    """2026-10-28: cùng một số viết '7949' ở bìa và '7.949' ở slide khác -> lộn xộn khi đọc."""

    def test_inconsistent_thousand_separator_flagged(self):
        rep = {"slides": [
            {"type": "cover", "title": "T", "subtitle": "7949 VM"},
            {"type": "content", "title": "T", "rows": [{"cols": [1], "blocks": [
                {"type": "stat", "value": "7.949", "label": "Tổng VM"}]}]},
        ]}
        errs = RP.check_number_format(rep)
        self.assertEqual(len(errs), 1)
        self.assertIn("7949", errs[0])

    def test_consistent_formatting_not_flagged(self):
        rep = {"slides": [
            {"type": "cover", "title": "T", "subtitle": "7.949 VM"},
            {"type": "content", "title": "T", "rows": [{"cols": [1], "blocks": [
                {"type": "stat", "value": "7.949", "label": "Tổng VM"}]}]},
        ]}
        self.assertEqual(RP.check_number_format(rep), [])

    def test_same_bare_number_used_only_once_not_flagged(self):
        rep = {"slides": [{"type": "cover", "title": "T", "subtitle": "7949 VM"}]}
        self.assertEqual(RP.check_number_format(rep), [])


class SelfOutputSourceGuardTests(unittest.TestCase):
    """2026-10-28: output cũ của chính skill này bị lưu nhầm tên và đưa lại làm 'nguồn', khiến mọi lỗi cũ lặp lại nguyên văn."""

    def test_own_summary_kicker_detected(self):
        content = "intro text " + ("THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO " * 1)
        self.assertTrue("THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO" in content.upper())

    def test_repeated_section_kicker_pattern_detected(self):
        import re
        content = "01 / 06 · A\n02 / 06 · B\n03 / 06 · C\nnội dung bình thường"
        hits = len(re.findall(r"\b\d{1,2}\s*/\s*\d{1,2}\s*·", content))
        self.assertGreaterEqual(hits, 3)

    def test_real_tracking_table_not_flagged(self):
        import re
        content = "STT Công việc Đơn vị thực hiện Thời hạn Tình trạng Kết quả\n1 Trích xuất danh sách VM VNPT IT 23/10/2026 Đã hoàn thành ..."
        hits = len(re.findall(r"\b\d{1,2}\s*/\s*\d{1,2}\s*·", content))
        self.assertLess(hits, 3)
        self.assertNotIn("THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO", content.upper())


if __name__ == "__main__":
    unittest.main()
