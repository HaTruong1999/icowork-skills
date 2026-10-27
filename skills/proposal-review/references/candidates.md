# candidates.json

Viết trong thư mục `_review/<tên>/` cạnh nguồn:

```json
{
  "doc_title": "Tên theo nội dung",
  "verdict": "Chưa nên gửi. Nêu ngắn điểm mạnh và vấn đề lớn nhất đã kiểm.",
  "strengths": [{"text": "Điểm tốt có căn cứ", "slides": "1"}],
  "issues": [{
    "title": "Vấn đề cụ thể",
    "group": "gui",
    "slides": [1],
    "quote": "Nguyên văn từ content.md",
    "problem": "Nhận định cần kiểm chứng",
    "why": "Tác động tới người đọc/quyết định",
    "fix": "Cách sửa có căn cứ"
  }],
  "notes": []
}
```

`group`: gui (trước gửi), trinh-bay (trước trình), nen (bổ sung). Có mã `fact` như `F2` hoặc `F2, F3` thì có thể dùng thay quote; phải đọc chính các facts đó và nguồn. Mã fact không chứng minh mọi câu viết thêm đều đúng.

Nhận định thiếu nội dung dùng `type: thieu-noi-dung`, `absent_terms: [từ đã tìm]`; không buộc trích một câu không tồn tại. Việc tìm từ chỉ giúp định vị, phải đọc cả nội dung trước khi kết luận thiếu. Điểm cần ảnh mà không có ảnh để kiểm đưa vào notes.

Mã như F1 phải ghi trong trường fact, không ghi trong quote. Với metadata ghi where: metadata, không gán số trang bìa.

## Bằng chứng tách theo lớp (nên dùng thay quote khi có nhiều vị trí)
`evidence`: danh sách `{"page": 4, "layer": "display", "quote": "nguyên văn ngắn"}`. Layer là display, notes hoặc metadata (metadata không cần page). Công cụ kiểm từng trích dẫn trong đúng lớp; không ghép thêm nhãn Slide N vào quote. Mâu thuẫn cần bằng chứng cả hai phía và fix xin tác giả xác nhận.
Vấn đề tiết lộ/bảo mật ở group gui cần `audience_evidence` cùng cấu trúc, trích bằng chứng người nhận thực tế ngoài phạm vi cho phép; nếu không có, diễn đạt có điều kiện ở nen hoặc bỏ. Chữ “nội bộ” hay Presenter View có thể xảy ra không chứng minh đã lộ.

Metadata title khác nội dung thường là nen; gui cần impact_evidence cùng cấu trúc evidence, chứng minh hệ thống/kênh gửi thực tế sử dụng metadata gây tác động. Bản tiếng Anh chỉ trong notes không là lỗi trình bày. Không dùng ngày kế hoạch quá khứ làm lỗi quá hạn khi thiếu bằng chứng việc còn chưa xong.
