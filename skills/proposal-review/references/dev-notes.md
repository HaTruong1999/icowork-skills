# Ghi chú cho người phát triển proposal-review

Tệp này không dành cho agent đang chạy review. Agent chỉ cần SKILL.md và các TASK.md do `iwork.py` in ra.

## Pipeline nội bộ

`iwork.py` gọi `scripts/pipeline.py` → `review.py` theo thứ tự `prepare → verify → critique → build`, rồi render ảnh trang và kiểm đầu ra (`audit_output`). Gọi tay để chẩn đoán (ngoài workspace iWork):

```bash
python3 scripts/review.py prepare "file" --today YYYY-MM-DD   # _review/<tên>/content.md, facts.md, source-map.json
python3 scripts/review.py verify "file"                       # kiểm candidates.json -> verified.json
python3 scripts/review.py critique "file"                     # tạo critique_task.md
python3 scripts/review.py build "file"                        # Danh_gia_<tên>.html + answer.md
```

Trong workspace có `session.json` (mode `iwork-native-model`), `review.py` từ chối gọi trực tiếp để tránh phá state. Đây là chặn gọi nhầm, không phải cơ chế bảo mật (driver đặt `IWORK_DRIVER=1`).


## Đổi giao diện, giữ nguyên nội dung

`python3 scripts/review.py restyle "answer.md" "output.html"` dựng lại HTML từ `answer.md` của một lần review đã xong, kiểm từng dòng nội dung không đổi và ghi audit SHA-256. Không chọn lại issues, không chạy lại model. `build` dùng chung renderer.

Thiết kế phiếu: font Be Vietnam Pro nhúng, nền xám sáng, hồ sơ và kết luận dạng card, nhãn số lượng, bộ lọc phát hiện. CSS ở `assets/review.css`, khung ở `assets/reference.html`. Không chép số điểm, số phát hiện hay tên người từ file mẫu vào phiếu thật.

Tính năng nhập trên phiếu HTML: tag màu mức độ ở bảng từng trang; hồ sơ, ô trống, phản hồi, ý kiến/xác nhận sửa trực tiếp được; tự lưu localStorage; nút lưu bản HTML kèm chỉnh sửa. Kết luận là nhóm radio tự tích theo verdict, người review chọn lại được, không sửa đoạn kết luận gốc. Footer: "Đánh giá bằng Coding Assistant."

## Khôi phục state

`iwork.py doctor --work <output>` phục hồi khi workspace bị dời đường dẫn hoặc driver được cập nhật giữa chừng, chỉ khi bản nguồn trong workspace còn đúng hash. Lưu state cũ và hash skill cũ/mới; lượt có doctor là lượt có can thiệp bảo trì.

## Test

```bash
python3 scripts/test_evidence_checks.py
python3 scripts/test_reference_form.py
python3 scripts/test_iwork.py      # cần PyMuPDF, bs4; chạy đủ vòng init → complete bằng JSON mẫu
```
