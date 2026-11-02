---
name: report-slides-html-vnptai
description: Tạo báo cáo điều hành dạng slide HTML 16:9 và PDF từ PDF, Excel, CSV, Word hoặc PowerPoint, dùng giao diện K7 nhận diện VNPT AI (logo VNPT AI) và kiểm tra chặt số liệu, tên riêng, tràn chữ. Dùng khi cần báo cáo cho lãnh đạo mang thương hiệu VNPT AI; không dùng để review tài liệu.
---

# Báo cáo điều hành dạng slide (giao diện K7 VNPT AI)

Bạn viết **nội dung** từng slide (JSON). Driver `iwork.py` lo phần còn lại: trích nguồn, kiểm số liệu, ghép, render HTML/PDF bằng khung K7 khoá sẵn, tự kiểm chất lượng và giao. Dùng model mặc định của iWork; không gọi API riêng.

## Bắt đầu ngay, không hỏi

Người dùng chỉ chọn skill và đính kèm tệp; lời nhắn có thể chỉ là "Mở <tên skill>". **Đó đã là yêu cầu đầy đủ.** Chạy `start` NGAY với tệp đính kèm (đường dẫn tương đối iWork liệt kê). Không hỏi tệp nào, ngày, phạm vi hay có muốn bắt đầu không, và không trả lời bằng lời giải thích skill làm gì. Tệp chưa được trích xuất trong ngữ cảnh là bình thường: driver tự trích.

## Lệnh shell: chỉ MỘT dạng được phép

iWork hiện hộp xin quyền và **đứng chờ người dùng bấm** với mọi lệnh khác dạng dưới đây. Mỗi lần như vậy là một lần làm phiền người dùng.

```text
python3 "SKILL_DIR/iwork.py" start "INPUT" --work "report-output"     # chỉ MỘT lần, lệnh đầu tiên
python3 "report-output/advance.py"                                    # mọi lệnh sau: driver in sẵn, chạy nguyên văn
```

`SKILL_DIR` là thư mục chứa tệp này (đường dẫn tuyệt đối, trong ngoặc kép; Windows dùng `python`). Sau `start`, driver tạo `report-output/advance.py` và chỉ in lệnh dạng trên: **không bao giờ tự gõ lại đường dẫn skill** (gõ sai sẽ lỗi và bị hỏi quyền). Mọi đường dẫn khác là **tương đối**, trong ngoặc kép. CẤM:

- `cd`, `&&`, `;`, `|`, `>`, `2>/dev/null`, `$BIẾN`, `$(…)`, dấu huyền, `~`, vòng lặp, nhiều dòng.
- `python3 -c`, heredoc, tự viết script, `ls`/`cat`/`find`/`grep` trên thư mục skill. Cần xem tệp thì dùng công cụ `read`; cần ghi tệp thì dùng `write`/`edit`, không dùng shell. Muốn kiểm JSON hay đếm ký tự: chạy `advance`, driver đã báo đúng lỗi và số ký tự cần bớt.
- Đường dẫn ngoài workspace hiện tại. Tệp người dùng gửi: dùng đúng đường dẫn tương đối mà iWork liệt kê cho lượt này. `--work` luôn là `report-output` (không thêm tên thư mục phiên phía trước).

Đường dẫn `<S>` in ở dòng "Base directory for this skill" ngay sau nội dung skill này: chép nguyên văn, **không `ls`/`find` để tìm** (`ls` thư mục skill bị iWork hỏi quyền).

## Quy tắc không được dừng

Người dùng **không được phải nhắn thêm** để skill chạy tiếp. Mọi lệnh driver kết thúc bằng một trong ba dòng:

- `=== CHƯA XONG … ===`: làm đúng việc được nêu rồi chạy lệnh tiếp **trong cùng lượt**. Ghi xong plan, vài slide hay build đạt đều **chưa phải** là xong.
- `=== DỪNG … ===`: chỉ khi tệp trạng thái bị sửa tay hoặc không có bản nào để giao. Báo đúng trạng thái.
- `HOÀN TẤT`: trả kết quả (xem cuối trang). Bản có chữ `BẢN NHÁP` vẫn là HOÀN TẤT: giao file và nêu rõ các cảnh báo.

Thêm:
1. **Không hỏi lại, không xin xác nhận, không đưa lựa chọn** (ngày, số slide, chương, mẫu, bỏ qua bước nào): tự quyết theo nguồn; điểm chưa chắc ghi vào `meta.canXacNhan`. Mọi lỗi driver báo đều tự sửa được rồi chạy lại.
2. **Mỗi bước chỉ làm đúng việc driver nêu, không phân tích dài.** Nghĩ lâu trên một quyết định là cách duy nhất khiến lượt bị cắt đứt giữa chừng. Thiếu chắc chắn thì chọn phương án đơn giản nhất.
3. **Không tạo tệp ngoài** `notes.md`, `plan.json`, `parts/NN.json` trong WORK; không sửa `iwork-state.json`, `job-step.json`, `report.json`. Driver tự sửa lỗi icon và số chương/số mục, tự lập bản kiểm chất lượng và tự `finish`.
4. **Bị ngắt hay nén ngữ cảnh**: đọc `notes.md`, chạy lại `advance "report-output"`; không `start` lại, không viết lại slide đã đạt.

**Sau khi bị nén ngữ cảnh hoặc người dùng bảo "làm tiếp":** việc đầu tiên là chạy `python3 "report-output/advance.py"`; lệnh này luôn đúng và làm tiếp từ chỗ dừng. Không tìm lại tệp nguồn (`ls`, `find`), không `init`/`start` lại. **Luôn gọi công cụ bash thật.** Tuyệt đối không viết lệnh thành chữ như `[Assistant tool call]: bash(...)` trong câu trả lời: chữ đó không chạy được, lượt kết thúc và người dùng phải nhắn lại.

**Người dùng báo lỗi tệp sau khi đã `HOÀN TẤT`** (trang trắng, chữ tràn, sai số, muốn sửa chữ): đó là việc của driver, không phải của bạn tự điều tra. **Cấm** mở HTML/PDF bằng `python3 -c`, `grep`, `cat`, `fitz`: các lệnh đó bị iWork hỏi quyền và không sửa được gì. Việc đúng: nếu cần đổi chữ thì sửa `report-output/_work/parts/NN.json` bằng công cụ `edit`, rồi chạy `python3 "report-output/_work/advance.py"`. Driver tự kiểm đầu ra thật (kể cả slide trắng), tự sửa lỗi cơ học, dựng lại HTML/PDF và in `HOÀN TẤT` khi xong.

## Các bước

```text
python3 "SKILL_DIR/iwork.py" start "INPUT" --work "report-output"
```

`INPUT` là tệp người dùng gửi (nhiều tệp cùng một báo cáo thì truyền cùng lệnh). Thêm `--date DD/MM/YYYY` khi người dùng nêu ngày, `--author` khi nêu rõ đơn vị. Mặc định **chỉ tiếng Việt, không lời thoại** (nhanh hơn một nửa); chỉ thêm `--song-ngu` khi người dùng yêu cầu bản tiếng Anh. Thiếu thư viện thì chạy lệnh cài driver in ra rồi `start` lại.

**Giao diện và logo:** skill này dùng giao diện **VNPT AI** (logo VNPT AI ở mọi slide, chân trang "VNPT AI"); người xem đổi được logo bằng nút **Logo và chân trang** trong trang HTML. Cần bộ slide không gắn thương hiệu VNPT AI thì dùng skill `report-slides-html`. Người dùng đưa tệp logo thay logo VNPT AI thì thêm `--logo "<tệp ảnh>"` vào `start`; muốn chữ chân trang riêng thì `--chan-trang "VNPT"`. Logo đến sau khi đã giao: chạy lại `start` cùng `--work` với `--logo`, rồi `advance`.

1. **Đọc một lần** `content.md` và `facts.md`. Bảng 12 mẫu K7 (trường, số mục, giới hạn ký tự, icon) do `start` in sẵn: **không cần đọc** [huong-dan-k7.md](references/huong-dan-k7.md), chỉ mở khi cần ví dụ. Rồi ghi **`notes.md`** (tối đa 25 dòng): thông điệp chính, ngày nguồn, số liệu cần dùng kèm vị trí, nhóm việc, hạn, kiến nghị. Đây là bộ nhớ của bạn; các lô sau không đọc lại toàn bộ nguồn.
2. **`plan.json`**: `{"meta":{"ten":"…","ban":"Bản 1 · dd/mm/yyyy","computed":[],"canXacNhan":[]},"outline":["tiêu đề slide 1","tiêu đề slide 2"]}` (`outline` là danh sách CHUỖI). Báo cáo ngắn thường 8–10 slide; có tiến độ/rủi ro/kiến nghị thì có slide tóm tắt điều hành. Số liệu tự tính chỉ khai trong `meta.computed` dạng `{"value","formula":"a+b"}`.
   - Có chương (nguồn chia phần rõ): ít nhất hai slide `mau:"chuong"`; slide nội dung ghi `dauMuc` chữ. Không có chương: chỉ dùng `dauMuc` chữ. **Đánh số do driver tự lo**, bạn không cần tính.
3. **`parts/NN.json`**: driver giao từng lô tối đa 6 slide. Ghi cả lô bằng nhiều lệnh `write` **trong cùng một bước**. Mỗi tệp là một object slide có `"mau"` (1 trong 12 mẫu) và `"tieuDe"`; bìa là `01.json`; không bọc trong `slides`.
4. **`advance`** sau mỗi lô. Đủ slide thì driver tự build và kiểm (cấu trúc K7, giới hạn chữ, số có trong nguồn, nhất quán %, tên riêng, tràn chữ, PDF). Có lỗi: sửa **tất cả** lỗi trong danh sách rồi `advance`. Tràn chữ thì viết ngắn lại hoặc tách slide, không sửa khung. Hết 4 lượt build lỗi thì driver tự giao bản nháp kèm cảnh báo.
5. Build đạt thì driver **tự kiểm chất lượng và `finish`** trong cùng lệnh, rồi in `HOÀN TẤT`. Bạn không viết file kiểm. Chỉ khi driver in `BUILD ĐẠT nhưng còn … yêu cầu bao phủ` thì mở `TASK.md`, sửa slide nêu đủ mã dòng/đơn vị/hạn được liệt kê rồi `advance`.

## Luật nội dung (độ chính xác)

- **Không bịa.** Mọi số, tên vùng/đơn vị, chủ sở hữu, nguyên nhân, mốc hạn phải có trong nguồn. Kiến nghị tự đề xuất phải ghi rõ là đề xuất. Slide có số liệu phải có `nguon`.
- **Đúng phạm vi.** Mỗi số nêu đúng đối tượng, phạm vi, đơn vị đo; KPI của một đơn vị không trình bày như tổng chung. Chỉ cộng các đại lượng cùng phạm vi và đơn vị. Đối chiếu nhãn từng ô số với câu nguồn chứa nó (vd "VM bàn giao" khác "VM đã rà soát").
- **Đúng mốc và trạng thái.** Mốc ngày gắn đúng công việc; tỷ lệ thấp nhất không tự chứng minh chậm kế hoạch. Trạng thái một dòng không đại diện cả mục: nêu mã dòng, đơn vị cụ thể.
- **Giữ cách viết số của nguồn** (`9.360`, `48,5`).
- Tác giả/đơn vị chỉ lấy từ nguồn hoặc yêu cầu rõ của người dùng; không có thì để trống.
- Biểu đồ trong nguồn: không xem được ảnh thì không đoán số.
- Validator có thể báo nhầm: đối chiếu nguồn trước khi sửa, không xoá nội dung đúng chỉ để qua kiểm.

## Trả kết quả

Chỉ trả khi driver in `HOÀN TẤT`. Nêu: đường dẫn HTML/PDF (dạng liên kết tương đối), số slide, ngày báo cáo, các điểm trong `meta.canXacNhan` và `uncertainties` của `delivery.json`. Luôn nói thật hai hạn chế: **chưa xem ảnh slide** (bố cục chỉ kiểm bằng phép đo trình duyệt) và bảng `doi_chieu_so` trong `delivery.json` là để người duyệt kiểm nhãn từng con số. Bản `BẢN NHÁP` thì mở đầu bằng cảnh báo và liệt kê lỗi còn lại. Không khẳng định chính xác tuyệt đối chỉ vì build đạt. Cuối cùng thêm đúng câu: **"File HTML có thể được chia sẻ bằng link thông qua iView trên Go Connect."** Không tự tạo link.
