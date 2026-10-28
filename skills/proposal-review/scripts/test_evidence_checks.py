import datetime as dt
import unittest
from evidence_checks import claim_errors, details_errors, dropped_claim_errors


class ClaimDateTests(unittest.TestCase):
    """2026-10-28: claim_errors chỉ dò chữ ('đang thực hiện'...), không so ngày thật với ngày
    đánh giá - nên nhận nhầm mốc CHƯA tới hạn thành 'quá hạn'. Vá bằng so ngày trích dẫn với today."""

    def test_future_date_flagged_as_not_yet_overdue(self):
        issue = {"group": "gui", "problem": "6 công việc quá hạn, không có giải trình.",
                  "why": "Các mốc 26/10, 27/10, 30/10 đã quá hạn.", "quote": "Hạn 26/10/2026"}
        errs = claim_errors(issue, {"pages": []}, today=dt.date(2026, 10, 24))
        self.assertTrue(any("chưa qua" in e for e in errs))

    def test_genuinely_overdue_date_not_flagged_by_new_check(self):
        issue = {"group": "gui", "problem": "Việc quá hạn.", "quote": "Hạn 20/10/2026"}
        errs = claim_errors(issue, {"pages": []}, today=dt.date(2026, 10, 24))
        self.assertFalse(any("chưa qua" in e for e in errs))

    def test_claims_no_explanation_but_quote_has_one(self):
        issue = {"group": "gui", "problem": "Mục 1.d chưa có giải trình.",
                  "quote": "Đang thực hiện làm sạch DS, cần thêm thời gian"}
        errs = claim_errors(issue, {"pages": []}, today=dt.date(2026, 10, 24))
        self.assertTrue(any("đã có nội dung giải trình" in e for e in errs))


class DroppedClaimConsistencyTests(unittest.TestCase):
    """2026-10-28: scorecard/page_reviews nhắc lại (như sự thật) một nhận định đã bị phản biện
    SAI hoặc bị REJECT ở verify - mâu thuẫn với final.json. Xem SKILL.md 'Nhất quán giữa
    scorecard/page_reviews và final.json'."""

    def setUp(self):
        self.dropped = [{"id": "I1", "title": "Metadata file ghi sai tên đối tác: NVIDIA thay vì Qualcomm",
                          "problem": "Metadata file ghi NVIDIA trong khi nội dung nói về Qualcomm.",
                          "why": "", "fix": ""}]

    def test_scorecard_rationale_reusing_dropped_issue_flagged(self):
        details = {"scorecard": [{"criterion": "Chính xác / Nhất quán",
                                   "rationale": "Metadata file ghi 'NVIDIA' trong khi toàn bộ nội dung nói về Qualcomm — lỗi nghiêm trọng."}]}
        errs = dropped_claim_errors(details, self.dropped)
        self.assertEqual(len(errs), 1)
        self.assertIn("NVIDIA", errs[0])

    def test_unrelated_scorecard_rationale_not_flagged(self):
        details = {"scorecard": [{"criterion": "Thị trường / Đối tượng",
                                   "rationale": "Proposal nhắm đúng đối tác Qualcomm, nội dung tập trung vào hiệu năng phần cứng."}]}
        self.assertEqual(dropped_claim_errors(details, self.dropped), [])

    def test_page_reviews_reusing_dropped_issue_flagged(self):
        details = {"page_reviews": [{"page": 1, "observation": "Metadata file ghi sai tên đối tác NVIDIA thay vì Qualcomm."}]}
        errs = dropped_claim_errors(details, self.dropped)
        self.assertEqual(len(errs), 1)

    def test_no_dropped_issues_means_no_errors(self):
        details = {"scorecard": [{"criterion": "X", "rationale": "Bất kỳ nội dung gì."}]}
        self.assertEqual(dropped_claim_errors(details, []), [])

    def test_details_errors_wires_dropped_issues_through(self):
        details = {"scorecard": [{"criterion": "Chính xác / Nhất quán",
                                   "rationale": "Metadata file ghi NVIDIA thay vì Qualcomm."}],
                    "page_reviews": []}
        source = {"pages": []}
        errs = details_errors(details, source, self.dropped)
        self.assertTrue(any("NVIDIA" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
