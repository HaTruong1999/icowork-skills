---
name: vnptai-report-html
description: Tạo một file HTML báo cáo/tóm tắt độc lập (single-file) theo đúng template chuẩn VNPT AI - trang bìa gradient xanh navy, mục lục (sidebar) cố định bên trái có scrollspy, các section/subsection có khối "key-points" tóm tắt, bảng và hình ảnh được gấp lại trong khối chi tiết dạng "bấm để xem", nút "Mở tất cả / Thu gọn tất cả", nút về đầu trang. Dùng skill này bất cứ khi nào người dùng yêu cầu tạo báo cáo, bản tóm tắt, kế hoạch triển khai, hay tài liệu nội bộ dạng HTML có mục lục và có thể mở/gấp hình-bảng - kể cả khi họ không nói rõ "theo template iCowork" hay không đính kèm file mẫu, miễn là họ nhắc đến việc xuất ra file .html có cấu trúc kiểu tài liệu nội bộ VNPT/VNPT AI.
---

# vnptai-report-html

Skill này giữ lại toàn bộ CSS/JS gốc của template "iCowork" (bản tóm tắt kế hoạch triển khai) và cung cấp một bộ khung (`assets/template.html`) cùng quy tắc điền nội dung, để tạo ra các báo cáo HTML khác có cùng phong cách trình bày mà không cần viết lại CSS/JS từ đầu.

## Khi nào dùng skill này

Dùng ngay khi người dùng:
- Yêu cầu tạo file HTML báo cáo/tóm tắt/kế hoạch có mục lục bên trái, trang bìa, và các bảng/hình có thể bấm mở ra.
- Nhắc tới "theo template chuẩn", "giống file iCowork", "kiểu VNPT AI", hoặc gửi kèm một file HTML output cũ để làm mẫu.
- Muốn chuyển một tài liệu Word/nội dung rời rạc (kế hoạch, đề án, báo cáo tổng hợp) thành một trang HTML độc lập để gửi nội bộ.

Không dùng skill này cho slide (.pptx), file Word (.docx) hay landing page marketing — đây là một dạng "tài liệu nội bộ dài, nhiều bảng/hình, cần mục lục" chứ không phải trang thiết kế.

## Quy trình

### Bước 1 — Thu thập nội dung trước khi viết HTML

Hỏi/nắm rõ những thứ sau (nếu người dùng đã cung cấp trong yêu cầu hoặc file đính kèm thì không cần hỏi lại):

1. **Tiêu đề tài liệu** (hiển thị to trên trang bìa, thường viết hoa) và **phụ đề** 1 câu.
2. **Đơn vị/tổ chức** để hiển thị ở dòng eyebrow trên cùng trang bìa (vd. "VNPT AI · Tài liệu nội bộ").
3. **Cấu trúc mục lục**: danh sách các phần cấp I (I., II., III...) và mục con của từng phần — đây chính là khung của cả `<nav class="sidebar">` lẫn các `<section>`.
4. **Nội dung từng mục con**: đoạn tóm tắt (để bỏ vào `.key-points`), có bảng số liệu không, có hình ảnh không.
5. **Ảnh** (nếu có): phải là ảnh người dùng cung cấp thật (upload file, hoặc mô tả rõ đường dẫn) — **không tự vẽ/bịa ảnh**. Nếu người dùng chưa có ảnh, bỏ qua phần hình, đừng chèn ảnh giữ chỗ giả.
6. **Nguồn gốc tài liệu** cho dòng footer (vd. "rút gọn từ tài liệu gốc '...'") — nếu không có, có thể bỏ dòng ghi nguồn hoặc thay bằng mô tả ngắn gọn tài liệu này được tạo khi nào/từ đâu.

Nếu thiếu quá nhiều nội dung để tạo ra một tài liệu có nghĩa (vd. người dùng chỉ nói "tạo báo cáo" mà không có nội dung gì), hỏi lại một câu duy nhất để lấy nội dung cốt lõi (tiêu đề + các phần chính), rồi tiến hành — đừng bịa số liệu hay nội dung nghiệp vụ.

### Bước 2 — Copy khung và điền nội dung

1. Đọc và copy `assets/template.html` làm điểm xuất phát — **giữ nguyên 100%** phần `<style>` và `<script>`, không viết lại CSS/JS từ đầu, không đổi tên class.
2. Điền trang bìa: `eyebrow`, `<h1>`, `.subtitle`, `.badge`.
3. Với **mỗi phần cấp I** trong nội dung thật, nhân bản khối `<section class="doc-section">` mẫu trong template; với **mỗi mục con**, nhân bản khối `<div class="doc-subsection">` mẫu. Xoá mọi phần mẫu/chú thích hướng dẫn (`<!-- HƯỚNG DẪN: ... -->`) không dùng tới.
4. Xây `<nav class="sidebar">` khớp **chính xác 1:1** với các section/subsection thật đã tạo (xem quy tắc id bên dưới) — mục lục sai id sẽ làm scrollspy và các liên kết nhảy trang không hoạt động.
5. Điền footer.
6. Kiểm tra lại theo checklist ở Bước 4 rồi xuất file.

### Bước 3 — Quy tắc trình bày nội dung

**Khối `.key-points`** (nền xanh nhạt viền trái) mở đầu mỗi section/subsection, chứa 1-3 đoạn `<p>` tóm tắt thông điệp cốt lõi, dùng `<b>` để làm nổi số liệu/từ khoá quan trọng — đây là phần người đọc thấy ngay mà không cần bấm mở gì. Không nhồi cả bảng chi tiết vào đây.

**`ul.mini-list`** dùng khi cần liệt kê nhanh vài con số/hạng mục ngay trong `.key-points` (vd. quy mô nhân sự theo từng nhóm), mỗi `<li>` một dòng ngắn, số liệu in đậm.

**Bảng** — LUÔN bọc trong:
```html
<details class="fold"><summary><span class="fold-icon">&#128202;</span><span class="fold-label">Bảng <số>: <tên bảng></span><span class="fold-hint">(bấm để xem)</span></summary><div class="fold-body"><div class="table-wrap"><table>
...
</table></div>
<p><em>Bảng <số>: <tên bảng></em></p></div></details>
```
- Icon 📊 (`&#128202;`) cho bảng, 📷 (`&#128247;`) cho hình.
- Hàng đầu tiên trong `<tbody>` đóng vai trò header (chữ `<strong>`), **không dùng `<thead>`**.
- Các hàng dữ liệu luân phiên `class="odd"` / `class="even"`, bắt đầu bằng `odd`.
- `<colgroup>` khai báo độ rộng % từng cột, tổng khoảng 99–100%.
- Caption lặp lại đúng tên bảng, đặt trong `<p><em>...</em></p>` ngay sau bảng — không đổi cách diễn đạt giữa fold-label và caption.
- Bảng nhiều cột (>5-6 cột, vd. bảng phân bổ nguồn lực theo nhiều vai trò) thì thêm `class="resource-table"` vào `<table>` để bảng không bị bóp méo, tự cuộn ngang trong khung.

**Hình ảnh** — cũng bọc trong `details.fold` (icon 📷), mỗi ảnh là `<p><img loading="lazy" src="..." alt="..."/></p>` theo sau bởi `<p><em>chú thích</em></p>`. Nếu 2-3 ảnh liên quan chặt chẽ, có thể gộp chung một `details.fold` với `fold-label` liệt kê tên các hình cách nhau bằng `&nbsp;/&nbsp;`. Ảnh nhúng trực tiếp bằng base64 (`data:image/...;base64,...`) giống bản gốc nếu người dùng gửi file ảnh — đọc file ảnh, encode base64, nhúng thẳng vào `src` để file HTML vẫn là **một file độc lập** không phụ thuộc file ngoài.

**Đánh số bảng/hình**: theo mẫu `<số phần>.<số mục con>.<số thứ tự trong mục con>`, ví dụ mục con thứ 2 của Phần I, bảng thứ nhất trong mục đó → "Bảng I.2.1"; hình thứ ba trong mục con thứ 1 của Phần II → "Hình II.1.3". Đánh số liên tục theo thứ tự xuất hiện, không nhảy số.

### Bước 4 — Quy tắc đặt id / neo mục lục

Mỗi `<section class="doc-section">` và mỗi `<div class="doc-subsection">` cần một `id` duy nhất, và `<nav class="sidebar">` phải trỏ tới đúng id đó qua `href="#id-đó"`.

Cách tạo id nhất quán và an toàn (trình duyệt chấp nhận id/href chứa chữ có dấu tiếng Việt bình thường, không cần bỏ dấu):
1. Lấy tiêu đề mục (không gồm số La Mã/số thứ tự phía trước nếu muốn id gọn hơn, nhưng phải **nhất quán** giữa các mục).
2. Chuyển hết về chữ thường.
3. Thay khoảng trắng bằng dấu gạch ngang `-`.
4. Bỏ dấu chấm câu, ngoặc, dấu `&`, dấu `/` — chỉ giữ chữ (có dấu), số và gạch ngang.
5. Gộp nhiều gạch ngang liền nhau thành một.

Ví dụ: tiêu đề "II. CÁC TÍNH NĂNG AI HIỆN CÓ" → id `ii.-cac-tinh-nang-ai-hien-co` **hoặc** giữ nguyên dấu `ii.-các-tính-năng-ai-hiện-có` — cả hai cách đều chạy được, miễn là `id` trên section và `href` trên link mục lục **khớp ký tự tuyệt đối với nhau**. Chọn một cách và áp dụng thống nhất cho toàn bộ tài liệu; đừng trộn lẫn (đây là lỗi thường gặp nếu bỏ dấu không đều tay).

### Bước 5 — Checklist trước khi xuất file

- [ ] Mỗi `href="#..."` trong `<nav class="sidebar">` có đúng một `id="..."` tương ứng tồn tại trong nội dung.
- [ ] Mọi bảng và hình đều nằm trong `<details class="fold">` với `<summary>` gồm đủ icon + fold-label + fold-hint.
- [ ] Không còn placeholder dạng `__...__` hay chú thích `HƯỚNG DẪN:` sót lại trong file cuối.
- [ ] Không tự bịa số liệu, hình ảnh, hay tên bảng — mọi nội dung số liệu phải đến từ người dùng/tài liệu nguồn.
- [ ] File là **một HTML độc lập**: không link CSS/JS/ảnh ngoài, ảnh (nếu có) nhúng base64 ngay trong file.
- [ ] `<title>` khớp với `<h1>` trang bìa.

### Bước 6 — Xuất file

Dùng `create_file` để lưu file vào `/mnt/user-data/outputs/<tên-file>.html` (đặt tên theo nội dung + ngày, kiểu `TenTaiLieu_TomTat_YYYYMMDD_HHhMM.html` nếu phù hợp), sau đó gọi `present_files` để người dùng thấy và tải về. Không dùng artifact — đây là file HTML tải xuống, không phải nội dung hiển thị trong khung chat.
