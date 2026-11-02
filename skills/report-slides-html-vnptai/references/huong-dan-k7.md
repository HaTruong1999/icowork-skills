# Tham chiếu nội dung slide K7

> Dùng trong skill report-slides-html. Quy trình chạy (lệnh, thứ tự bước, khi nào dừng) nằm trong SKILL.md và output của `iwork.py`; tệp này chỉ mô tả **nội dung JSON** của từng slide. Nguồn gốc: bộ giao diện K7 (bản chung 0.5, 29/10/2026 và bản VNPT AI). Hai giao diện dùng chung 12 mẫu và cấu trúc JSON dưới đây; chỉ khác nhận diện (logo, chân trang) và danh sách ảnh dùng chung ở mục 6.

## 1. Việc của bạn

- Mỗi slide là **một tệp `parts/NN.json`** (một object có trường `mau`). Phần chung của bộ slide (`meta.ten`, `ban`, `canXacNhan`, `computed`) nằm trong `plan.json`. Driver tự ghép thành `report.json`, tự kiểm và render; không tự ghép, không viết HTML/CSS.
- Giao diện đã khoá trong `k7/<giao-diện>/Tao-slide.html` (`chung` mặc định, hoặc `vnpt-ai`): không đổi màu, phông, bố cục, cỡ chữ. Logo và chân trang do driver gắn theo lệnh `start`; không khai `meta.nhanDien`. Tràn chữ thì viết ngắn lại hoặc tách slide.
- Ví dụ hoàn chỉnh: `examples/atbm-vm/report.json` (báo cáo tiến độ, 9 slide). Chỉ tham khảo cấu trúc; không chép câu chữ hay số liệu sang báo cáo khác (build sẽ báo lỗi "chép ví dụ").

## 2. Cách chọn mạch

1. Người xem là lãnh đạo: họ cần biết kết quả, vướng mắc và quyết định cần chốt.
2. Mỗi slide **một ý**; tiêu đề là **câu kết luận**, không phải tên chủ đề.
3. Số slide theo nội dung nguồn; báo cáo ngắn thường 8–10 slide. Không cắt ý quan trọng để cho ngắn.

## 3. Mạch mẫu

| Loại bộ | Mạch gợi ý |
|---|---|
| Báo cáo lãnh đạo | Bìa → Tóm tắt điều hành (số liệu) → Kết quả theo từng nhóm việc → Vướng mắc, rủi ro (thẻ hoặc vấn đề → giải pháp) → Kiến nghị cần duyệt (thẻ/bảng) → Thời gian tới (lộ trình) |
| Giới thiệu cho khách hàng | Bìa → Mục lục → Khách hàng đang dùng (số liệu) → Kết quả thực tế → Sản phẩm → Triển khai → Lộ trình → Cảm ơn |
| Trao đổi với đối tác | Bìa (có `doiTac`) → Quy mô → Kết quả chung (số liệu, bảng) → Khó khăn → Đề xuất → Bước tiếp theo → Cảm ơn |

## 4. Cấu trúc tệp

Dưới đây là `report.json` sau khi driver ghép. Bạn viết `meta` trong `plan.json`; mỗi phần tử của `slides` là một tệp `parts/NN.json` riêng.

```json
{
  "meta": {
    "id": "vnptai-ten-bo-2026",
    "ten": {"vi": "Tên bộ slide", "en": "Deck name"},
    "ban": "Bản 1 · 22/10/2026",
    "ngonNgu": ["vi", "en"],
    "canXacNhan": ["Số liệu chưa khớp giữa hai nguồn: … (ghi cho người duyệt, không hiện trên slide)"]
  },
  "slides": [ { "mau": "bia", "...": "..." } ]
}
```

**Ngôn ngữ:** mặc định **chỉ tiếng Việt**: mọi ô chữ là chuỗi thường `"…"`, không viết `en`, không viết `loiThoai` (driver tự tổng hợp lời thoại từ chữ trên slide). Chỉ khi `start` có `--song-ngu` mới viết mọi ô chữ dạng `{"vi": "…", "en": "…"}` kèm `loiThoai`.

**Nhấn mạnh:** bọc **một cụm** trong tiêu đề bằng dấu sao: `"Nhiều bài toán nhanh gấp *3–4 lần* GPU"` → cụm đó hiện màu xanh sáng. Tối đa 1 cụm mỗi tiêu đề. Không dùng `**`, không HTML.

**Trường chung** (có ở hầu hết mẫu):

| Trường | Bắt buộc | Giới hạn | Ghi chú |
|---|---|---|---|
| `mau` | có | | Tên mẫu ở mục 5 |
| `nhan` | nên có | 28 | Tên ngắn ở mục lục bên trái, ví dụ "Kết quả chính" |
| `dauMuc` | có (trừ bìa, chương, cảm ơn) | 32 | `"4 · Kết quả trên Qualcomm"`. **Bắt đầu bằng số phần**: số mục 4.1, 4.2… tự đánh theo số này. Chỉ dùng cách này khi deck có trang `mau:"chuong"` tương ứng. |
| `soMuc` | tuỳ chọn | 8 | Ghi đè số trong vòng tròn. Với deck không có trang chương, bắt buộc dùng số phẳng liên tục `"1"`, `"2"`, `"3"`… |
| `tieuDe` | có | 64 | **Một câu kết luận**, không phải tên chủ đề. "Fall Detection nhanh gấp *3 lần* GPU ở 30 luồng", không phải "Kết quả Fall Detection" |
| `phu` | không | 150 | Một câu giải thích dưới tiêu đề |
| `ketLuan` | không | 100 | Dải xanh cuối slide: điều người xem cần nhớ |
| `nguon` | **có với slide có số liệu** | 130 | "Nguồn: tên tài liệu (tháng/năm)." Kèm điều kiện đo nếu cần |
| `loiThoai` | chỉ khi `--song-ngu` (mặc định driver tự tổng hợp) | 1600 | Lời người trình bày; xuống dòng bằng `\n` |

## 5. Mười hai mẫu

Giới hạn là **số ký tự tối đa** (không tính dấu `*`). Cột "Số mục" là số phần tử của danh sách.

| `mau` | Tên | Khi dùng | Trường riêng | Số mục | Giới hạn ký tự |
|---|---|---|---|---|---|
| `bia` | Bìa | Mở đầu bộ slide | `the` (nhãn nhỏ), `tieuDe`, `phu`, `dong` (người trình bày / đơn vị), `doiTac` (tên đối tác, tuỳ chọn) | | tieuDe 56 · the 36 · dong 56 · phu 140 · doiTac 24 |
| `muc-luc` | Mục lục | Sau bìa, khi bộ có ≥ 3 phần | `muc[]`: `{t, d}` | 3–6 | t 28 · d 40 |
| `chuong` | Ngăn chương | Mở đầu một phần lớn | `so` ("2"), `tieuDe`, `phu` | | so 3 · tieuDe 48 · phu 140 |
| `so-lieu` | Số liệu lớn | 3–6 con số ngang hàng cần nhớ; đặt số quan trọng nhất ở ô đầu | `so[]`: `{so, nhan, icon}` | 3–6 | so 10 · nhan 56 |
| `van-de` | Vấn đề → giải pháp | Nỗi đau của khách hàng rồi cách giải | `vanDe`: `{t, y[], so, soNhan}`; `giaiPhap`: `{t, y[]}` | y: 2–4 | t 48 · y 64 · so 8 · soNhan 40 |
| `the` | Thẻ | 3–6 ý ngang hàng (sản phẩm, lợi ích, khó khăn, đề xuất) | `the[]`: `{t, d, icon}` hoặc `{t, d, logo: ["asset:…"]}` | 2–6 | t 34 · d 80 |
| `bang` | Bảng so sánh | So nhiều phương án theo cùng tiêu chí | `cot[]` (tên cột), `hang[][]` (mỗi hàng một mảng ô) | hàng: 2–5 | cột 20 · ô đầu hàng 16 · ô khác 80 |
| `lop` | Kiến trúc nhiều lớp | Nền tảng xếp tầng | `lop[]`: `{ma, t, noi}` (`noi: true` = lớp tô nổi); `quanTri`; `ghiChu`: `{t, y[]}` | lớp 3–10 · y 2–4 | ma 4 · t 56 · quanTri 80 · ghiChu.t 44 · y 64 |
| `anh` | Ảnh có chú giải | Ảnh chụp sản phẩm thật, đánh số vùng | `anh`: `{src, alt}`; `vung[]`: `{x, y, w, h}` (% của ảnh); `chuGiai[]`: `{t, d}` | 2–5 (vùng = chú giải) | t 26 · d 44 |
| `hinh-so` | Hình + số liệu | Một hình lớn (bản đồ, ảnh) kèm vài con số | `anh`: `{src, alt}`; `so[]`: `{so, nhan, icon}` | 2–4 | so 8 · nhan 40 |
| `lo-trinh` | Lộ trình | 3–6 bước, mỗi bước có thời gian hoặc nhãn | `buoc[]`: `{t, d, tg, icon}` | 3–6 | t 24 · d 40 · tg 12 |
| `cam-on` | Cảm ơn, liên hệ | Kết thúc: lời mời hành động | `tieuDe`, `phu`, `lienHe[]`: `{nhan, gt}` | 1–4 | tieuDe 44 · phu 150 · gt 44 |

**Ví dụ từng mẫu** (rút gọn, chỉ tiếng Việt cho dễ đọc; khi bật `--song-ngu` thì viết đủ `vi` và `en`):

```json
{"mau":"so-lieu","nhan":"Kết quả chính","dauMuc":"4 · Kết quả","tieuDe":"Nhiều bài toán nhanh gấp *3–4 lần* GPU",
 "so":[{"so":"3×","nhan":"nhanh hơn GPU: Fall Detection, 30 luồng","icon":"toc-do"},
       {"so":"≥30","nhan":"luồng video real-time trên server","icon":"video"},
       {"so":"17,9","nhan":"tok/s LLM trên laptop Snapdragon","icon":"laptop"}],
 "ketLuan":"Server chạy được tới 70 luồng.","nguon":"Nguồn: báo cáo kỹ thuật (20/10/2026).","loiThoai":"…"}

{"mau":"the","nhan":"Khó khăn","dauMuc":"5 · Khó khăn","tieuDe":"Sáu điểm *cần cùng giải quyết*",
 "the":[{"icon":"cai-dat","t":"Làm quen công cụ convert","d":"Lần đầu ~1 tháng; các mô hình sau ~1–2 tuần."}, …]}

{"mau":"van-de","dauMuc":"2 · Kết quả","tieuDe":"Tổng đài nghe lại được *dưới 2%* cuộc gọi",
 "vanDe":{"t":"Phần lớn hội thoại chưa được phân tích","y":["…","…"],"so":"< 2%","soNhan":"cuộc gọi được nghe và đánh giá"},
 "giaiPhap":{"t":"AI Agents phân tích mọi cuộc gọi","y":["…","…"]},"nguon":"Nguồn: …"}

{"mau":"bang","dauMuc":"4 · Kết quả","tieuDe":"Thị giác: *3 trên 5* mô hình nhanh hơn GPU",
 "cot":["Mô hình","So với GPU","Qualcomm · GPU"],
 "hang":[["Text detection","3,3× · FP16","50,5 · 15,2 FPS"],["RTMPose","2,5× · FP16","2.387 · 940 FPS"]]}

{"mau":"lo-trinh","dauMuc":"7 · Bước tiếp theo","tieuDe":"Ba *pilot chung*",
 "buoc":[{"icon":"may-chu","tg":"Server","t":"Pilot 1 · LLM Agentic","d":"Mục tiêu: giảm TTFT prompt 20k"}, …]}

{"mau":"bia","the":"Trao đổi hợp tác · 2026","doiTac":"Qualcomm",
 "tieuDe":"Cùng *Qualcomm* tối ưu, triển khai AI từ server đến edge",
 "phu":"Voice, vision và LLM đã chạy trên server AI, AI Box và laptop Snapdragon.","dong":"Chuẩn bị bởi VNPT AI · Gửi Qualcomm"}
```

**Chọn mẫu nhanh:**
- Có 3–6 con số → `so-lieu`. Có 2–4 con số đi với một hình (bản đồ, ảnh) → `hinh-so`.
- Có nhiều chỉ số theo cùng cột (mô hình × tốc độ × độ chính xác) → `bang`. Đừng nhồi bảng vào thẻ.
- Có danh sách ý ngang hàng → `the`. Có thứ tự thời gian → `lo-trinh`.
- Có "trước / sau", "vấn đề / giải pháp" → `van-de`.
- Có ảnh chụp giao diện thật → `anh`. Không có ảnh thật thì **không** dùng mẫu này.

## 6. Icon và ảnh

**Icon** (Hugeicons, đã có sẵn trong khung). Chỉ dùng tên trong danh sách; tên khác bị lỗi M8. Mỗi ô số liệu, mỗi thẻ, mỗi bước nên có một icon **đúng nghĩa với nội dung ô đó**; không dùng một icon cho tất cả.

`nguoi` con người, đội ngũ · `cong-dong` cộng đồng, nhiều bên · `khach-hang` doanh nghiệp, tổ chức · `chinh-phu` cơ quan nhà nước · `hop-tac` hợp tác, đối tác · `ai` AI, công nghệ lõi · `agent` agent, trợ lý AI · `du-lieu` dữ liệu · `may-chu` server, hạ tầng · `chip` chip, phần cứng, NPU · `laptop` laptop · `ai-box` thiết bị đóng gói, AI Box · `camera` camera, thị giác máy tính · `video` video, luồng camera · `giong-noi` giọng nói · `dien-thoai` điện thoại, mobile · `dam-may` cloud · `bao-mat` bảo mật · `lop` nhiều lớp, đa luồng · `ket-noi` kết nối, tích hợp · `cai-dat` cấu hình, kỹ thuật · `dong-ho` thời gian · `lich` lộ trình, lịch · `toc-do` tốc độ, hiệu năng · `tang` tăng trưởng · `giam` giảm, suy giảm · `bieu-do` số liệu, báo cáo · `muc-tieu` mục tiêu, độ chính xác · `ten-lua` triển khai, bứt phá · `tim-kiem` tìm kiếm, khảo sát · `giai-thuong` giải thưởng · `nghien-cuu` nghiên cứu, công bố · `ma-nguon` mã nguồn · `khuon-mat` nhận diện khuôn mặt · `dinh-danh` xác thực, định danh · `api` API, lượt gọi · `token` token, LLM · `su-kien` sự kiện, luồng dữ liệu · `tong-dai` tổng đài, CSKH · `tiet-kiem` tiết kiệm chi phí · `canh-bao` rủi ro · `dung` đạt, cam kết · `y` ý tưởng · `email` · `goi` điện thoại liên hệ · `web` trang web · `dia-chi` địa chỉ

**Ảnh dùng chung** (viết `"asset:tên"`), tuỳ giao diện:
- Mọi giao diện: `anhMau` (giữ chỗ cho ảnh chụp màn hình), `hinhMau` (giữ chỗ cho bản đồ, sơ đồ, ảnh). Chỉ để giữ chỗ: người dùng bấm vào ảnh trên trang để thay ảnh thật.
- Chỉ giao diện `vnpt-ai`: `banDo` bản đồ 34 tỉnh, thành · `nghienCuu` trang nghiên cứu vnptai.github.io · `idecide` màn dự báo VNPT iDecide · logo sản phẩm `ekyc`, `vnface`, `smartbot`, `vncallbot`, `smartvoice`, `smartreader`, `smartvision`, `vnsocial` (dùng trong `the[].logo`).

Nền, logo, hoa văn, chân trang do khung tự đặt; **không** khai báo.
Cần ảnh khác: đặt tạm `"asset:hinhMau"` (hoặc `"asset:anhMau"` với ảnh màn hình) và ghi vào `meta.canXacNhan` "Slide N cần ảnh …". Người sửa bấm vào ảnh trên trang HTML để thay. Không bịa đường dẫn ảnh, không chèn ảnh từ Internet.

## 7. Viết chữ

- **Tiêu đề là kết luận**, có số nếu có: "Vinaphone: *30 triệu* cuộc gọi được AI phân tích mỗi năm".
- Câu ngắn, mỗi câu một ý. Nói lợi ích bằng ngôn ngữ của người xem, không bằng tên kỹ thuật.
- Số giữ **đúng cách viết của nguồn** ở cả bản Việt và bản Anh: `1.272`, `11,88%`, `5,8 tỷ đ` (không đổi thành `1,272`, `11.88%`). Bản dịch chỉ dịch chữ.
- Ngày `dd/mm/yyyy`. Khoảng `3–4` dùng gạch ngang dài `–`. Nhân `×`.
- Không viết HOA cả câu, không emoji, không `**`, không "Hãy …". Xưng "anh/chị" với người xem khi cần.
- **Không bịa số.** Mọi con số phải có trong tài liệu nguồn. Slide có số liệu phải có `nguon`.
- **Nguồn mâu thuẫn:** không tự chọn im lặng. Chọn số có dữ liệu chi tiết đi kèm, rồi ghi vào `meta.canXacNhan` (ví dụ "Fall Detection ở 30 luồng: khối Con số chính ghi 1,8×, biểu đồ ghi 3×; đang dùng 3×").
- Bản tiếng Anh (chỉ khi `--song-ngu`): dịch ý, giữ nguyên số như bản Việt, cùng độ dài để không tràn ô.

## 8. Không làm

- Không thêm trường lạ, không đổi tên trường, không lồng HTML vào chữ.
- Không dùng mẫu ngoài 12 mẫu. Thiếu mẫu phù hợp: dùng mẫu gần nhất và ghi đề xuất vào `meta.canXacNhan`.
- Không vượt giới hạn ký tự bằng cách bỏ dấu cách hay viết tắt khó hiểu; hãy viết lại ngắn hơn hoặc tách slide.
- Không đặt logo, màu, cỡ chữ: khung tự lo.

## 9. Tự kiểm trước khi trả

| Mã | Kiểm | Mức |
|---|---|---|
| C1, C2 | Có `meta.ten`, `slides`; đủ trường bắt buộc của mẫu | lỗi |
| M1 | `mau` thuộc 12 mẫu | lỗi |
| M2 | Mọi ô trong giới hạn ký tự (cả `vi` và `en`) | lỗi |
| M4 | Số mục trong khoảng; ảnh có chú giải: số vùng = số chú giải | lỗi |
| M5 | Slide `so-lieu`, `hinh-so`, `van-de` có `nguon` | lỗi |
| M8 | Icon thuộc danh sách | lỗi |
| M9 | Ảnh `asset:` thuộc danh sách | lỗi |
| M10 | Dấu `*` chẵn; tiêu đề tối đa 1 cụm nhấn mạnh | lỗi |
| M3 | Có bản tiếng Anh (chỉ khi `--song-ngu`) | nhắc |
| M6 | Có lời thoại (chỉ khi `--song-ngu`) | nhắc |
| M7 | Chữ không tràn khung khi hiển thị (build tự kiểm bằng trình duyệt) | lỗi |

Thêm phần tự rà bằng mắt: mỗi slide một ý; tiêu đề là câu kết luận; số quan trọng nhất ở ô đầu; icon đúng nghĩa; mạch đi từ người xem.

Ghi chú giao diện (khung tự làm, AI không cần đặt): các ô đồng cấp luôn cùng một kiểu, không tô riêng ô nào; nền xanh đặc chỉ dành cho khối khác cấp (cột giải pháp, ghi chú bên cạnh kiến trúc, dải kết luận).
