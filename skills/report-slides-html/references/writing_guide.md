# Cách biến tài liệu gốc thành báo cáo slide trình lãnh đạo

> **Bản -k7:** mục 1, 2, 4 (ghi notes.md, dàn slide, văn phong) vẫn dùng được. Mục 3 và 5/5b nói về
> khối `stat/panel/bars/...` của schema cũ - **không áp dụng**. Chọn mẫu slide và viết đúng cấu trúc
> theo [huong-dan-k7.md](huong-dan-k7.md) mục 3 (mạch mẫu) và mục 5 (12 mẫu), không theo mục 3/5/5b dưới đây.

Mục tiêu: lãnh đạo xem 1 phút mỗi slide là nắm được **đã làm được gì – còn vướng gì – cần ai làm gì**.
Mẫu chuẩn (schema cũ, chỉ để tham khảo mạch ý): `examples/atbm-vm/` (báo cáo tiến độ ATBM hệ thống VM, 7 slide).

## 1. Ghi chú nguồn trước khi viết (notes.md)

Đọc hết `content.md` (đọc từng đoạn nếu dài). Ghi ra `WORK/notes.md` theo khung:

```
# Mảng việc: <tên>                      (lặp cho từng mảng)
- Kết quả: <câu ngắn> [NGUỒN 1 > Trang 4]
- Số liệu: 505 tài khoản; 150/450 VM [NGUỒN 1 > Trang 4]
- Khó khăn/vướng mắc: …
- Việc tiếp theo: …
- Kiến nghị (ai – làm gì): …
# Thông tin chung: đơn vị báo cáo, ngày, phạm vi, người nhận,
#   mục tiêu, thời hạn, kinh phí / giải ngân, tiến độ tổng (nếu nguồn có)
```
Thông tin chung **bắt buộc có mặt** trong báo cáo khi nguồn có: thời hạn và mục tiêu đưa vào `subtitle` bìa
hoặc `lead` slide đầu; kinh phí/giải ngân và tiến độ tổng đưa thành `stat` (slide đầu hoặc slide tổng hợp).
Vị trí: pdf → `Trang n`, pptx → `Slide n`, docx/html/txt → tên mục gần nhất.
Chép số **nguyên văn** từ nguồn kèm vị trí. Không chắc → `report.py find WORK "<từ khóa>"`.
Nguồn mâu thuẫn nhau (2 file ghi 2 số khác) → dùng số của file mới nhất, ghi vào câu trả lời cuối cho người dùng.

## 2. Dàn slide chuẩn (báo cáo tiến độ / kết quả)

| # | Slide | Nội dung | Khối gợi ý |
|---|---|---|---|
| 1 | Bìa | đơn vị · chuyên đề, tên báo cáo, phạm vi, ngày, mục lục = các mảng việc + “Thông điệp, kiến nghị” | `cover` |
| 2…n | Mỗi **mảng việc** 1 slide | kicker `0i / 0N · TÊN MẢNG`; tiêu đề = hành động + kết quả; hàng 1: 2–4 số chính; hàng 2: chi tiết + khó khăn; `next` = việc tiếp theo | `stat`, `progress`, `status_table`, `panel`, `split`, `numlist` |
| (tùy) | Slide chi tiết | khi mảng có bảng phân loại/danh sách dài; kicker thêm `· CHI TIẾT` | `category`, `table`, `bars` |
| cuối | Tổng hợp (`dark: true`) | kicker `THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO`; 3–4 số quan trọng nhất; “Đã đạt được” + “Kiến nghị” | `stat` (tone `accent`/`highlight`), `text` |

Số mảng việc: 3–6. Tài liệu không phải báo cáo tiến độ (đề xuất, kế hoạch, đánh giá) vẫn dùng dàn này,
đổi tên mục: “Bối cảnh – Giải pháp – Lộ trình – Kinh phí – Kiến nghị”.

## 3. Chọn khối theo dạng dữ liệu

| Dữ liệu trong nguồn | Khối |
|---|---|
| 1–4 con số then chốt | hàng `stat` (số quan trọng nhất: `tone: primary`; số cần chú ý: `warn`) |
| Tỷ lệ hoàn thành X/Y | `progress` (value “33,33%”, caption “**150/450 VM** đã hoàn thành · còn **300 VM**”) |
| Tổng chia 2–3 nhóm | `split` |
| Vài dòng “số – ý nghĩa” | `numlist` |
| Danh sách hạng mục + trạng thái | `status_table` (có mô tả) hoặc `status_list` (gom theo trạng thái) |
| Kết quả / khó khăn / vướng mắc / kiến nghị | `panel` tone `light` / `warn` / `danger` / `dark` |
| Bảng phân loại có tổng | `category` (2 bảng cạnh nhau: tone `primary` và `dark`) |
| Bảng nhiều cột | `table` |
| So sánh đơn vị | `bars` |
| Việc sắp làm (đánh số) | `steps` |

Bố cục hay dùng: hàng 1 `[1,1,1]` ba `stat`; hàng 2 `[1.1,0.9]` khối chính + khối phụ; cột trái hẹp dạng `stack`
(`stat` + `progress`) bên cạnh cột phải `stack` (`panel` kết quả + `panel` khó khăn) với `cols: [0.75, 1.25]`.

## 4. Văn phong

- Câu ngắn, kiểu văn bản hành chính; bắt đầu bằng động từ: “Hoàn thành…”, “Đã đổi…”, “Phối hợp…”.
- Tiêu đề slide nói **kết quả hoặc việc**, không chung chung (“Triển khai đổi mật khẩu quản trị”, không phải “Mục 2”).
- Mỗi gạch đầu dòng 1 ý, ≤ 2 dòng. Dùng `**đậm**` cho số và cụm từ khóa, tối đa 2 chỗ/câu.
- Trạng thái dùng thống nhất: Hoàn thành · Đang triển khai · Đang đánh giá · Chưa hoàn thành.
- Kiến nghị ghi rõ **ai – làm gì – (khi nào)**: “VNPT-IT cấp đủ 300 TB dung lượng Backup…”.
- Viết tắt giữ như nguồn (VM, ATBM, SIEM, EDR/EPP…). Nguồn có giải thích thì có thể đưa vào `note`;
  nguồn **không** giải thích (vd NTL, PHG) → để nguyên, **không tự đoán nghĩa**.
- Ngày dạng `dd/mm/yyyy`; số thập phân dấu phẩy; nghìn dấu chấm.

## 5. Không được

- Không bịa số, tên, mốc thời gian. Số tự tính (tỷ lệ %, tổng, còn lại) → khai `meta.computed` kèm phép tính.
- Không thêm nhận định “đánh giá cao”, “rất tốt” nếu nguồn không có.
- Không thêm chi tiết suy đoán: nguồn ghi “3/5 vùng đã kết nối” thì **không** tự ghi “còn Vùng 4, Vùng 5”;
  nguồn không ghi trạng thái thì không tự gán “Đang triển khai”.
- Không lấy chữ của ví dụ mẫu ATBM (“VNPT NET”, “CHUYÊN ĐỀ 05”, tên hệ thống, số liệu…) nếu nguồn không có;
  kicker bìa ghi đơn vị/chủ đề **có trong nguồn**.
- Tỷ lệ % đi kèm phân số phải làm tròn đúng: 26/64 = 40,6% → ghi 41% (hoặc 40,6%), không ghi 40%.
- Không viết lại số đã có thành dạng khác (“giảm 3 lần”, “giảm 75%”) trừ khi khai `meta.computed`.
- Không sửa `assets/template.html`/CSS để chữa tràn – sửa nội dung (rút gọn, đổi `cols`, tách slide).
- Không viết HTML bằng tay; mọi thay đổi qua `parts/NN.json` hoặc `plan.json` rồi `iwork.py build`.

## 5. Dàn BÁO CÁO ĐIỀU HÀNH – MẶC ĐỊNH CHO MỌI ĐẦU VÀO (theo mẫu báo cáo CEO của lãnh đạo)

Người đọc: lãnh đạo cấp cao, xem cả báo cáo trong ~2 phút. Nguyên tắc: **kết luận trước** (BLUF), mỗi slide
trả lời một câu hỏi, **gộp** chứ không chép lại bảng, **tô màu theo trạng thái** (xanh xong · xanh dương đang làm ·
cam chậm/chờ · đỏ chưa bắt đầu/quá hạn/thiếu nguồn lực). Số slide theo lượng nội dung; dàn dưới là gợi ý, có thể thêm slide chi tiết để tránh tràn.

| # | Slide | Trả lời câu hỏi | Khối |
|---|---|---|---|
| 1 | Bìa | Báo cáo gì, cập nhật lúc nào, phạm vi | `cover`: kicker `BÁO CÁO ĐIỀU HÀNH · <ĐƠN VỊ>`, `date` = “Cập nhật: <giờ> · <ngày>” (lấy từ đầu bảng), `agenda` = các phần |
| 2 | `01 / 0N · TỔNG QUAN` | Tình hình chung ra sao? | Hàng 1: **4 `stat`** (xem dưới). Hàng 2: `status_table` các **nhóm việc** (gộp các mục của bảng thành 3–5 nhóm theo chủ đề): `item` = tên nhóm (ghi “Mục 1, 2…”), `status` = trạng thái nhóm, `desc` = chủ trì · thời hạn · 1 kết quả nổi bật |
| 3 | `02 / 0N · <MẢNG RỦI RO NHẤT>` | Việc rủi ro nhất tới đâu? | `bars` hoặc `progress` cho từng phân số X/Y của mảng đó (dùng % trong facts.md); `panel` tone `danger` cho phát hiện nghiêm trọng; `next` = việc kế tiếp có mốc |
| 4 | `03 / 0N · THEO ĐƠN VỊ` | Ai chậm, ai xong? | `bars` tiến độ từng đơn vị (đơn vị 0% hoặc chưa bắt đầu: `tone: "warn"`), hoặc `table`; `panel` tone `warn` liệt kê đơn vị chưa bắt đầu kèm hạn |
| 5 (tùy) | Tổng hợp `dark: true` | Cần lãnh đạo quyết gì? | 2–3 `stat` + `text` “Kiến nghị” (chỉ khi nguồn có kiến nghị/nhu cầu nguồn lực) |

**Chọn 4 số cho slide Tổng quan** (lấy từ `facts.md`, mỗi số một ý khác nhau):
1. **Quy mô**: tổng đối tượng được rà soát/quản lý (tổng lớn nhất nêu trong bảng).
2. **Tiến độ việc rủi ro nhất**: phân số tổng hợp của mảng có rủi ro cao nhất (vd tổng các site/cụm), tone `primary`.
3. **Khối lượng đã làm**: tổng số đã hoàn thành của mảng triển khai rộng nhất (tổng theo mục trong facts.md).
4. **Vướng mắc lớn nhất**: nhu cầu/thiếu hụt nguồn lực (tổng dung lượng, số đơn vị chưa bắt đầu…), tone `warn`.

Mỗi dòng của bảng gốc **không** cần xuất hiện; dòng nào **chậm, chưa bắt đầu, quá hạn, thiếu nguồn lực** thì PHẢI xuất hiện.
Trạng thái nhóm: tất cả dòng xong → “Đã hoàn thành”; có dòng chưa bắt đầu/thiếu nguồn lực → nêu đúng chữ đó;
còn lại → “Đang thực hiện” kèm “xong m/n đầu việc” (số m/n lấy từ facts.md).


### 5b. Áp dàn điều hành cho tài liệu KHÔNG phải bảng theo dõi
Vẫn dùng các nhóm nội dung như bảng trên; chỉ đổi nội dung từng ô:

| Loại nguồn | 4 số Tổng quan | Bảng nhóm việc (slide Tổng quan) | Slide 3 (mảng quan trọng nhất) | Slide 4 |
|---|---|---|---|---|
| Báo cáo tiến độ/kết quả (văn bản) | quy mô · tỷ lệ hoàn thành chính · giải ngân/nguồn lực · vướng mắc lớn nhất | các hạng mục, trạng thái, hạn | `progress`/`bars` các chỉ tiêu X/Y | theo đơn vị/vùng (`bars`, `table`) |
| Đề xuất / kế hoạch | quy mô (số nhiệm vụ, đơn vị) · mục tiêu chính · ngân sách/nguồn lực · mốc quan trọng nhất | các nhóm đề xuất: chủ trì, giai đoạn, kết quả kỳ vọng | lộ trình (`steps`/`table` theo giai đoạn) | phân vai/đơn vị, rủi ro |
| Hồ sơ năng lực / giới thiệu | 4 con số quy mô nổi bật | các mảng sản phẩm/dịch vụ | kết quả, bằng chứng | đề nghị hợp tác |

Chỉ dùng số có trong nguồn hoặc `facts.md`. Số nào phải tự tính → `report.py calc "<biểu thức>"` rồi chép dòng
`computed` in ra vào `meta.computed`. Nguồn không có số cho một ô → bỏ ô đó (dùng 3 `stat`), **không** bịa.
Dàn ATBM (mục 2) chỉ dùng khi người dùng yêu cầu rõ “theo mẫu ATBM”.
