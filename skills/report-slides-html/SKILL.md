---
name: report-slides-html
description: Tạo báo cáo điều hành dạng slide HTML 16:9 và PDF từ tài liệu hoặc bảng theo dõi PDF, Excel, CSV, Word, PowerPoint, dùng giao diện chính thức VNPT AI (bộ K7). Dùng khi cần tổng hợp báo cáo cho lãnh đạo; không dùng để review tài liệu. Bản thử nghiệm - K7 (giao diện) chưa được lãnh đạo chốt chính thức; phần trích nguồn/kiểm chứng số liệu kế thừa từ report-slides-html v6.5.
---

# Báo cáo điều hành trên iWork (giao diện K7)

Giao diện (HTML/CSS, 12 mẫu slide) do bộ K7 của anh Hoàng cấp, khoá sẵn trong `k7/Tao-slide-VNPT-AI.html` - không sửa. AI chỉ viết nội dung JSON theo đúng [huong-dan-k7.md](references/huong-dan-k7.md) mục 4-9 (schema.md/writing_guide.md cũ không áp dụng nữa cho bản `-k7` này).

Đầu ra là HTML + PDF; chọn ý theo nguồn và người đọc. Giữ chất lượng, không cắt số slide hay số ý để tiết kiệm token. Cơ chế chống mất tiến độ là **lưu từng slide**, không phải rút ngắn nội dung.

## Khởi động

`SKILL_DIR` là thư mục chứa file này. Chỉ dùng entrypoint **`SKILL_DIR/iwork.py`**. Thay bằng đường dẫn tuyệt đối và đặt mọi đường dẫn trong dấu ngoặc kép. Mỗi tool call một lệnh, không `cd`, không shell variables, không ghép nhiều lệnh.

```text
python3 "SKILL_DIR/iwork.py" start "INPUT" --work "report-output"
```

`INPUT` là file đính kèm/đường dẫn thực tế của người dùng. `WORK` là thư mục kết quả mới nằm trong workspace iWork thực tế của hội thoại (lấy từ công cụ, không tự đoán nhánh RAU/TraoDoiRieng; dùng tên thư mục con tương đối theo cwd của tool). Không đưa tài liệu mẫu hoặc đáp án vào nguồn. Nhiều file thuộc cùng báo cáo thì truyền cùng lệnh; các bài độc lập hoàn tất lần lượt. Nếu người dùng chỉ định ngày báo cáo thì thêm `--date DD/MM/YYYY`; nếu không đối chiếu ngày ở đầu nguồn mà script gợi ý.

Lệnh tự kiểm môi trường, trích nguồn và tính facts. Thiếu dependency thì làm theo lệnh in ra rồi chạy lại. Không xem bước lỗi là thành công. Không sửa scripts/assets để cho qua kiểm tra.

## Viết theo từng phần và lưu ngay

1. Đọc toàn bộ `WORK/content.md`, `WORK/facts.md`, [huong-dan-k7.md](references/huong-dan-k7.md) mục 4-9 (cấu trúc, 12 mẫu, giới hạn chữ, icon). Không đọc toàn bộ ví dụ báo cáo khác nếu không cần.
2. Đơn vị báo cáo/tác giả chỉ lấy từ nguồn hoặc yêu cầu rõ của người dùng, không lấy hồ sơ tài khoản iWork hay bài cũ; nguồn không có thì để trống `meta.author` và dùng kicker theo chủ đề. Kiến nghị tự đề xuất phải ghi rõ là đề xuất, không trình bày như yêu cầu đã có trong nguồn. Tỷ lệ thấp nhất không tự chứng minh chậm kế hoạch. Với tổng do nguồn công bố qua nhiều hạng mục, giữ nguyên đơn vị đo và ghi “tổng theo bảng nguồn”, không suy ra số đối tượng duy nhất. Làm rõ phạm vi bằng nhãn/chú thích; không đổi đơn vị của số nguồn sang số dòng hoặc số bản ghi.

   Ghi `WORK/notes.md`: người đọc, ngày nguồn, thông điệp chính, nhóm việc, tiến độ, đơn vị chậm, hạn và quyết định cần chốt. Với bảng theo dõi, giữ quan hệ **mã dòng → công việc → đơn vị → hạn → trạng thái → kết quả**. Chỉ cộng các đại lượng cùng phạm vi và đơn vị đo.
3. Ghi `WORK/plan.json`: `{"meta":{"ten":{"vi":"…","en":"…"},"ban":"Bản 1 · dd/mm/yyyy","computed":[]},"outline":["tiêu đề từng slide"]}`. `iwork.py build` tự nhập các phép tính do công cụ phát ra trong facts.md, không cần chép tay; `meta.computed` dành cho phép tính bổ sung; nếu cần phép tính mới dùng `scripts/report.py calc` rồi chép kết quả. Số slide theo nội dung (K7: thường 10-16 slide).
4. Chạy lệnh `resume` mà script in ra. **Ghi ngay một slide** vào đường dẫn `parts/NN.json` được chỉ định, dưới dạng object slide có trường `"mau"` (1 trong 12 mẫu K7). Bìa là `parts/01.json` với `"mau":"bia"`, không tạo `00.json`. Mỗi lần ghi chỉ một slide, sau đó gọi `resume` tiếp. Không giữ toàn bộ báo cáo trong suy luận, không viết lại slide đã lưu. Không bọc phần trong `slides` hoặc `report`.
5. Khi đủ phần, chạy nguyên lệnh `build` script in ra. Nó ghép phần, kiểm tra bằng `k7/cong-cu/kiem-slide.py` (cấu trúc, giới hạn chữ, icon) và các kiểm chứng số liệu của report-slides-html (số phải có trong nguồn, nhất quán %, tên riêng không bịa), render HTML/PDF bằng khung K7 khoá sẵn, lưu `build.log`. Có lỗi thì sửa phần liên quan hoặc plan.json rồi build lại. Không sửa trực tiếp report.json vì đó là file ghép tự động. Khung K7 khoá sẵn: không tự shrink chữ khi tràn - tràn thì PHẢI rút câu/tách slide trong giới hạn ký tự của mẫu, không sửa CSS/HTML của khung. Tối đa 3 vòng sửa cho cùng lỗi; còn lỗi thì báo rõ bản nháp và log, không tuyên bố đạt.

6. Build đạt chưa phải hoàn tất: đọc TASK.md kiểm chất lượng, coverage-required.json và quality-audit.template.json; xem ảnh nếu công cụ hỗ trợ rồi viết quality-audit.json. Nếu phiên không có khả năng đọc ảnh, phải ghi rõ hạn chế; dùng kiểm tra geometry của build, không khẳng định đã xem ảnh. Dùng bằng chứng trong chính slide cuối cho từng dòng cần bao phủ. Chạy `iwork.py finish WORK` theo lệnh driver. Có lỗi nội dung thì sửa parts/plan, build và audit lại đúng hash; chỉ giao khi finish trả HOÀN TẤT. Khi đó `finish` tự dọn toàn bộ file nháp (content.md, facts.md, parts/, report.json, build.log, _preview, …) vào `WORK/_work/`, chỉ để lại `{tên}.html`, `{tên}.pdf`, `iwork-state.json` và `delivery.json` ở gốc WORK. Cần Word sau đó thì vẫn chạy `report.py docx WORK` như cũ — tự tìm report.json trong `_work/` nếu không thấy ở gốc.

## Kiểm tra chất lượng trước khi trả

- Mỗi số phải nêu đúng đối tượng, phạm vi, đơn vị đo; KPI của một đơn vị không được trình bày như tổng chung. Số có trong nguồn chưa đủ để kết luận diễn giải đúng.
- Mốc ngày gắn đúng **công việc**: hạn lập danh mục không được thay bằng hạn hardening/quét log. Không nhầm ngày nguồn với hạn công việc.
- Trạng thái một dòng không đại diện cả mục. Nếu chỉ một số dòng chưa bắt đầu, nêu mã dòng và đơn vị cụ thể. Đối chiếu thông báo validator với nguồn trước khi sửa, vì kiểm tra mẫu có thể báo nhầm.
- Phân biệt dòng nguồn, dòng có trạng thái, dòng chi tiết, dòng tổng/cha và dòng nghi trùng; không âm thầm khử rồi gọi là đầu việc duy nhất. Ghi rõ giả định nếu cần tổng tạm. Phải trình bày bất thường dữ liệu và mốc tổng khác hạn chi tiết. Không gộp nhãn quá hạn/chưa bắt đầu với số đếm chỉ thuộc một nhóm.
- Khoản kinh phí bổ sung không tự có nghĩa chưa được cấp hoặc là nguyên nhân chưa hoàn thành; đề xuất xác nhận tình trạng trước khi yêu cầu cấp vốn. So sánh theo đơn vị chỉ một số mục phải ghi rõ phạm vi, không dùng tiêu đề bao quát.
- Không bỏ các kết quả tổng hợp, vướng mắc hoặc quyết định quan trọng trong notes. Không ép báo cáo ngắn để né lỗi thực thi.
- Xem ảnh `_preview/sheets/` và sửa phần có tràn, phân cấp không rõ hoặc thiếu cảnh báo đơn vị chậm; build lại sau mọi thay đổi.

## Tiếp tục sau khi bị ngắt

Chạy `python3 "SKILL_DIR/iwork.py" resume "WORK"`. Script chỉ phần tiếp theo chưa ghi; đọc lại notes và phần nguồn cần thiết rồi tiếp tục. Không extract lại, không hỏi người dùng có muốn tiếp tục khi yêu cầu ban đầu đã rõ. Nếu runtime dừng cả lượt trước khi thực thi tool, skill không tự khởi động lại được; báo đúng trạng thái thay vì nhận đã hoàn tất.

## Trả kết quả

Chỉ nhận hoàn thành khi build cuối cùng đạt, có cả HTML/PDF, đã xem preview và finish xác nhận audit đúng hash cuối. Trả đường dẫn, số slide, nguồn/ngày báo cáo, kết quả kiểm tra và điểm còn chưa chắc. Không khẳng định độ chính xác tuyệt đối chỉ dựa vào build.
