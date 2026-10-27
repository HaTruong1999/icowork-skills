# Báo cáo đầy đủ theo mẫu người dùng

Sau prepare → candidates → verify → critique → build, tạo report-details.json bằng model từ toàn bộ nguồn và final.json mới nhất, rồi build lại. Không lấy câu chữ của báo cáo mẫu làm kết luận mới. Không thay đổi hoặc rút gọn danh sách final để vừa bố cục.

Cấu trúc:
- source_sha256, verified_sha256: công cụ điền; không để model đoán.
- metadata: presenter, department, version, review_type, request_summary; mỗi giá trị cần căn cứ trong nguồn; nếu thiếu dùng null. Không suy ra tác giả từ lastModifiedBy.
- scorecard: 8 tiêu chí đề xuất rõ ràng; chính xác/nhất quán; bằng chứng; thị trường/đối tượng; hiệu quả/chi phí; kế hoạch/nguồn lực; rủi ro; cấu trúc. Mỗi mục {name, weight, score, rationale, slides}. Trọng số dương, tổng 100; score 0–10 là đánh giá của người review, không phải số liệu tác giả. Giải thích cụ thể theo nguồn; tiêu chí không phù hợp đổi tên trước khi chấm, không áp tiêu chí thương mại máy móc vào tài liệu chuyên đề. Điểm tổng do code tính trung bình có trọng số.
- page_reviews: một mục cho từng trang/slide {page, title, observation, issue_ids}. Observation phân biệt mô tả nội dung với kết luận kiểm chứng; issue_ids chỉ lấy ID trong final.json. Không kết luận bố cục/hình nếu chỉ đọc text. Ảnh gốc được công cụ render thêm; không yêu cầu model chọn tọa độ.
- questions: [{text, issue_ids}] câu hỏi cho người trình, căn cứ các điểm chưa đủ thông tin hoặc vấn đề đã xác minh.
- actions: [{issue_id, task, owner, collaborators, deadline}]. Bao phủ mọi ID final; task diễn đạt đúng fix. Owner/deadline chỉ điền khi nguồn giao đúng việc sửa đó, còn lại null. Không lấy người nộp file làm người phụ trách mọi việc.
- proposed_structure: [{title, content, is_new, rationale}] đề xuất thứ tự trình lại phù hợp chính tài liệu; ghi rõ là đề xuất của reviewer.
- response_draft: dự thảo phản hồi bằng lời, giữ đúng kết luận final; không tự đặt hạn hoặc khẳng định đã gửi.
- report_checks: kiểm từng scorecard rationale, page observation, question, action, cấu trúc và phản hồi có căn cứ; ghi các điểm còn hạn chế vào notes. Các thành phần này là nhận định/tư vấn của reviewer, không gán thành sự thật của nguồn.

Lịch sử chỉ ghi lượt chạy hiện tại (model, ngày), không dựng các vòng trước. Khối xác nhận để trống cho người dùng điền. Trường thiếu có lý do; không sao chép tác giả/điểm/deadline của template.

Nếu model trả tổng trọng số khác 100 nhưng từng trọng số dương, công cụ tính theo trọng số tương đối rồi chuẩn hóa % hiển thị; ghi rõ việc chuẩn hóa, giữ nguyên điểm và tỷ lệ trọng số. Không sửa số liệu nguồn.
