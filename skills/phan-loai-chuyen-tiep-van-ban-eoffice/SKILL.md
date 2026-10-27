---
name: phan-loai-chuyen-tiep-van-ban-eoffice
description: "Phân loại văn bản eOffice đến và đề xuất chuyển tiếp cho đúng đơn vị, đúng người của Công ty VNPT AI theo chức năng nhiệm vụ trong các Quyết định thành lập đơn vị, chia vai trò Xử lý chính / Phối hợp / Xem để biết. Dùng khi người dùng hỏi văn bản này giao ai, chuyển cho ai, đơn vị nào xử lý chính, phân công/bút phê văn bản, hoặc muốn chuyển tiếp văn bản eOffice đang mở."
---

# Phân loại và chuyển tiếp văn bản eOffice (VNPT AI)

Đọc một văn bản eOffice, xác định đơn vị nào **Xử lý chính**, đơn vị nào **Phối hợp**, đơn vị nào **Xem để biết**, chọn người nhận trong từng đơn vị, rồi trả về đề xuất kèm căn cứ. Trả lời bằng tiếng Việt.

**iWork chỉ đề xuất.** Không tự chuyển văn bản trên eOffice, không ghi ý kiến hay bút phê thay người dùng. Người dùng xác nhận rồi tự thao tác.

## Tài liệu trong skill

- `references/vnpt-ai-chuc-nang-nhiem-vu-don-vi.md` là nguồn dữ liệu duy nhất, gồm chức năng, nhiệm vụ có mã của 7 đơn vị, ma trận phân loại, quy tắc phân xử chồng lấn, bảng lãnh đạo và mẫu kết quả. **Đọc toàn bộ file trước khi phân loại.** Các mục cần dùng:
  - Mục 2: định nghĩa vai trò và nhóm eOffice tương ứng.
  - Mục 3: danh sách đơn vị, mã, tên gọi khác, Ban Lãnh đạo Công ty.
  - Mục 4: ma trận lĩnh vực → Xử lý chính / Phối hợp, có từ khóa nhận diện.
  - Mục 5: chi tiết nhiệm vụ từng đơn vị (để trích mã căn cứ) và bảng lãnh đạo từng đơn vị.
  - Mục 6: quy tắc phân xử khi nhiều đơn vị cùng khớp.
  - Mục 7: ví dụ đã phân loại.
  - Mục 8: mẫu kết quả.

## Quy trình

### Bước 1 — Lấy dữ liệu văn bản

Lấy theo thứ tự ưu tiên:
1. Thẻ "THÔNG TIN VĂN BẢN" mà iWork đã điền sẵn trong phiên khi người dùng mở văn bản trên eOffice. Dùng các trường: Số eOffice, Số ký hiệu, Trích yếu, Đơn vị ban hành, Ngày đến, Độ khẩn, Hạn xử lý, file đính kèm, và **lịch sử xử lý** (người gửi, ý kiến, nhóm Xử lý chính / Phối hợp / Xem để biết).
2. File văn bản đính kèm (PDF/DOCX). Đọc phần nội dung yêu cầu và mục "Nơi nhận".
3. Nội dung người dùng dán vào khung chat.

Nếu chỉ có trích yếu mà nội dung chưa đủ rõ để phân loại, đọc file đính kèm. Không có file thì hỏi người dùng **một câu**.

### Bước 2 — Xác định cấp chuyển tiếp

- **Cấp Công ty → đơn vị**: phân cho các đơn vị, người nhận là Thủ trưởng đơn vị. Đây là **mặc định** khi văn bản gửi đến Công ty VNPT AI và lịch sử xử lý chưa giao đơn vị nào (kể cả văn bản người dùng dán vào). Khi áp mặc định, ghi giả định này ở phần Lưu ý, không hỏi lại.
- **Trong đơn vị**: lịch sử xử lý cho thấy văn bản đã được giao cho đơn vị X, và người dùng là Thủ trưởng X (hoặc nói mình thuộc X). Khi đó phân cho cấp phó/người phụ trách lĩnh vực trong X. Đơn vị khác mà lãnh đạo đã giao Phối hợp/Xem để biết thì giữ nguyên, không đề xuất chuyển lại.
- **Người dùng là văn thư Công ty**: văn thư không tự giao việc. Trình bày kết quả dưới dạng "Đề xuất trình Lãnh đạo Công ty bút phê" và vẫn kèm bảng phân loại để lãnh đạo tham khảo.

Chỉ hỏi người dùng một câu ("Anh/chị chuyển ở cấp Công ty hay trong đơn vị nào?") khi các dấu hiệu mâu thuẫn nhau, vd lịch sử đã giao đơn vị X nhưng người dùng không thuộc X.

### Bước 3 — Phân loại

Làm theo mục 1.1 (bước 1–5) và mục 6 của file tham chiếu. Những điểm hay sai:
1. Chỉ định có sẵn trong văn bản, bút phê hoặc lịch sử xử lý thì giữ nguyên. Phần nào iWork tự bổ sung phải nói rõ là bổ sung.
2. Mỗi lượt chuyển chỉ có **một** đơn vị Xử lý chính, kể cả khi văn bản gồm nhiều việc (mục 1.1 bước 4). Phần việc riêng của từng đơn vị Phối hợp ghi ở cột "Nội dung cần làm".
3. Nhiều đơn vị cùng khớp → áp quy tắc mục 6 và ghi tên quy tắc đã dùng vào phần Lưu ý.
4. Căn cứ phải là **mã nhiệm vụ có thật** trong mục 5 (vd `QTNS.9.8`, `KDTV.2.1`). Mã chỉ khớp gần đúng thì ghi "(gần nhất)". Không tự đặt mã, không gán nhiệm vụ mà file không có.
5. "Trình lãnh đạo" có hai cách dùng. Hãy theo đúng mục 1.2 của file tham chiếu.

### Bước 4 — Chọn người nhận

Theo mục 1.1 bước 6 của file tham chiếu. Ô `[cần bổ sung]` và ô `[vd: …]` đều là chưa có dữ liệu. **Không bịa họ tên, email hay tài khoản.** Thiếu dữ liệu thì cuối kết quả nhắc một dòng: bổ sung bảng lãnh đạo của đơn vị đó vào file tham chiếu.

### Bước 5 — Trả kết quả

Dùng mẫu markdown ở mục 8 của file tham chiếu, với tên vai trò theo eOffice: **Xử lý chính / Phối hợp / Xem để biết**. Yêu cầu:
- Dòng đầu là kết luận ngắn, vd "Đề xuất: Ban QTNS xử lý chính, Ban KDTV phối hợp."
- Cột "Nội dung cần làm" nêu việc cụ thể lấy từ văn bản, không chép lại chức năng chung.
- Ghi hạn xử lý nếu có. Văn bản Khẩn/Hỏa tốc thì nêu ngay ở dòng đầu. Dùng ngày hiện tại của hệ thống/phiên làm việc để tính hạn còn bao lâu; nếu còn dưới 2 ngày thì cũng nêu ở dòng đầu. Không biết ngày hiện tại thì chỉ ghi hạn, không tính.
- Độ tin cậy nói về độ chắc của **phân loại**: **Cao** khi khớp rõ một lĩnh vực hoặc đã có chỉ định; **Trung bình** khi phải phân xử chồng lấn hoặc dùng mã "(gần nhất)"; **Thấp** chỉ khi không xác định được Xử lý chính (vai trò "Trình lãnh đạo"). Ghi chú "Cần trình Lãnh đạo Công ty" hoặc dạng trình bút phê cho văn thư không làm giảm độ tin cậy.
- Chỉ xuất khối JSON ở mục 8 khi người dùng yêu cầu hoặc khi cần tích hợp.
- Cuối kết quả gợi ý bước tiếp, vd "Anh/chị có muốn em soạn ý kiến chuyển xử lý không?". iWork được soạn nội dung ý kiến; thao tác chuyển trên eOffice do người dùng tự làm.

## Lưu ý

- Văn bản đi do chính VNPT AI ban hành (ký hiệu `…/VNPT AI-<đơn vị>`): phần ký hiệu cho biết đơn vị soạn thảo. Đơn vị soạn thảo thường là đầu mối theo dõi, không mặc nhiên là Xử lý chính cho việc phát sinh sau đó.
- Văn bản chỉ đạo chung, báo cáo tổng hợp gửi "các đơn vị" → áp quy tắc chung 1–2 ở mục 6 của file tham chiếu. "Các đơn vị" trong văn bản của Tập đoàn là các đơn vị VNPT, không phải đơn vị trực thuộc VNPT AI.
- Không tiết lộ, suy đoán hay tổng hợp thông tin cá nhân ngoài những gì có trong văn bản và file tham chiếu.
- File tham chiếu được xây từ bản dự thảo các Quyết định thành lập (tháng 01/2026). Người dùng phản ánh cơ cấu đã thay đổi thì làm theo thông tin mới nhất họ cung cấp và đề nghị cập nhật file.
