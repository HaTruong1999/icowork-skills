# Cấu trúc report.json

Trong workflow iWork: agent viết plan.json và từng parts/01.json, parts/02.json… theo object slide dưới đây. iwork.py ghép report.json tự động; không tự sửa file ghép. Cấu trúc gốc bên dưới chỉ mô tả kết quả ghép.
Ví dụ đầy đủ, đã chạy được: `examples/atbm-vm/report.json` (7 slide, dùng gần hết các loại khối).

Quy tắc chung:
- Chữ đậm: `**...**`. Xuống dòng: `\n`. **Không** viết thẻ HTML.
- Có thể dùng dấu ngoặc kép nếu escape đúng JSON; nên dùng “ ” cho nội dung tiếng Việt.
- Không để dấu phẩy thừa trước `}` hoặc `]`.
- Số viết kiểu Việt Nam, chép **đúng như nguồn**: `33,33%`, `1.250`, `300 TB`.
- Trường lạ / thiếu trường / sai `type` / sai `tone` → `build` báo lỗi, chỉ rõ slide và khối.

## 1. Gốc

```json
{
  "meta": {
    "title": "Tên báo cáo (tiêu đề tab trình duyệt, thuộc tính PDF/Word)",
    "output_name": "Ten_file_dau_ra_khong_dau",
    "author": "Đơn vị",
    "date": "24/10/2026",
    "sources": ["file nguồn 1.pdf", "file nguồn 2.pptx"],
    "computed": [ {"value": "33,33%", "formula": "150/450 = 33,33%"} ]
  },
  "theme": { "primary": "#0b5cbf" },
  "slides": [ ... ]
}
```
- `meta.computed`: chỉ dành cho con số **tự tính** (không có nguyên văn trong nguồn), khai kèm phép tính,
  nếu không `build` báo lỗi số liệu. Số/tỷ lệ % đã có sẵn trong nguồn thì **không** cần khai.
  `formula` viết dạng phép tính thuần với số như trong nguồn, vd `"9.360 / 12.480 = 75%"`,
  `"(85.000 - 21.000) / 85.000 = 75,3%"` – script tự tính lại và báo `[3b]` nếu sai.
- `theme` (tùy chọn, thường bỏ trống): đổi màu. Khóa hợp lệ: `navy`, `navy-2`, `primary`, `sky`, `sky-soft`,
  `warn`, `highlight`, `bg`, `card`, `line`, `text`, `muted`, `next-bg`, `font`.

## 2. Ba loại slide

### cover – bìa (slide đầu)
```json
{"type": "cover", "kicker": "VNPT NET · CHUYÊN ĐỀ 05",
 "title": "Báo cáo tiến độ triển khai …", "subtitle": "Phạm vi báo cáo", "date": "Ngày 24/10/2026",
 "agenda": [ {"num": "01", "text": "Danh mục VM"}, {"num": "05", "text": "Thông điệp, kiến nghị", "gap": true} ]}
```
`agenda` ≤ 6 mục, **khớp số phần** (số phần khác số slide): mỗi phần = một nhóm slide có kicker `0i / 0N · TÊN PHẦN` (N mục), cộng
1 mục cho slide tổng hợp nền tối nếu có; mẫu số trong kicker chỉ đếm các phần đánh số, không đếm bìa hoặc tổng hợp tối (`build` báo lỗi nếu lệch). `gap: true` tạo khoảng cách trước mục đó. Tiêu đề bìa ≤ 70 ký tự,
được phép 2–3 dòng (không cần chỉnh nếu chỉ còn 1 từ ở dòng cuối).

### section – trang ngăn chương (ít dùng)
```json
{"type": "section", "kicker": "PHẦN 2", "title": "Kế hoạch quý IV", "subtitle": "…"}
```

### content – slide nội dung (mặc định, không cần ghi `type`)
```json
{"kicker": "01 / 04 · DANH MỤC VM",
 "title": "Rà soát, chuẩn hóa danh mục VM",
 "lead": "Một câu tóm tắt (tùy chọn)",
 "dark": false,
 "rows": [ {"cols": [1, 1, 1], "grow": false, "blocks": [ khối, khối, khối ]} ],
 "next": "Việc tiếp theo (thanh xanh nhạt 'Tiếp theo →', tùy chọn)",
 "note": {"label": "Ghi chú", "text": "chú thích cuối slide (tùy chọn)"}}
```
- `rows`: các hàng xếp từ trên xuống. Mỗi hàng là lưới cột: `cols` = tỷ lệ bề rộng, **số phần tử bằng số khối**.
  Ví dụ `[1.1, 0.9]` = cột trái rộng hơn một chút.
- `grow: true` ở hàng: hàng giãn hết chiều cao còn lại. Không hàng nào ghi `grow` → hàng cuối tự giãn.
  Hàng chỉ giãn khi thiếu ≤ 120px; thiếu nhiều hơn thì giữ chiều cao tự nhiên (tránh hộp trống).
- `dark: true`: nền xanh đậm (dùng cho slide tổng hợp cuối).
- `note` có thể là chuỗi đơn giản.

## 3. Các loại khối (`blocks`)

| type | Dùng khi | Trường | tone |
|---|---|---|---|
| `stat` | 1 con số lớn + ý nghĩa | `value`, `label` | `primary` (thẻ xanh), `warn` (số cam), `dark`, `accent` (số xanh nhạt, slide tối), `highlight` (thẻ cam) |
| `split` | 1 tổng chia 2–3 phần (thanh tỷ lệ) | `title`, `parts[{value,label,weight,desc}]`, `note`; `weight` = số lượng thô (171, 279) | – |
| `numlist` | 2–6 dòng “số – ý nghĩa” (số dài như 3,04 triệu vẫn được) | `title`, `items[{value,text,tone?:"warn"}]` | – |
| `category` | Bảng phân loại có tổng (đầu thẻ màu) | `title`, `sub`, `total`, `rows[{label,value}]` | `primary`, `dark` |
| `progress` | Tiến độ % có thanh chạy. **Chỉ dùng cho tiến độ làm xong việc (tăng là tốt). KHÔNG dùng cho số đo rủi ro/sự cố** (vd 4/6 VCenter bị chiếm quyền = 66,7%): dùng `stat` tone `warn` hoặc `panel` danger. Mỗi `progress` cao ~170px: tối đa 2 cái xếp chồng trong một cột; nhiều hơn thì dùng `bars` | `label`, `value` (chữ), `percent` (số 0–100), `caption` | – |
| `panel` | Hộp tiêu đề + gạch đầu dòng/đoạn | `title`, `bullets[]` và/hoặc `text` | `light`, `warn` (khó khăn), `danger` (vướng mắc), `dark` (kiến nghị) |
| `status_table` | Hạng mục – trạng thái – mô tả | `rows[{item,status,desc,tone?}]`, `title?` | – |
| `status_list` | Nhóm việc theo trạng thái | `items[{status,text,tone?}]` | – |
| `steps` | Danh sách việc đánh số (nền tối) | `title`, `items[]` | – |
| `text` | Tiêu đề màu + đoạn văn (hợp slide tối) | `title`, `text` | `accent` (xanh), `highlight` (cam) |
| `table` | Bảng số liệu thường | `title?`, `columns[]`, `rows[[...]]`, `num_cols[]` (chỉ số cột số, căn phải) | – |
| `bars` | So sánh nhiều đơn vị/hạng mục | `title`, `items[{label,value,percent,tone?}]`, `max?`, `label_width?` | tone mục: `warn`, `done` |
| `stack` | Xếp nhiều khối chồng dọc trong **một cột** | `blocks[]` (không lồng stack) | – |

Mọi khối có thể thêm `"grow": true` (trong `stack`: khối đó giãn hết phần còn lại của cột).

Trạng thái (`status`) tự tô màu theo chữ: “Hoàn thành/Đã …” → xanh lá; “Đang triển khai/Đang …” → xanh dương;
“Đang đánh giá/Chờ …/Xem xét” → cam; “Chưa …/Chậm/Trễ/Vướng” → đỏ. Muốn ép màu: `tone`: `done` | `doing` | `eval` | `todo` | `neutral`.

### Mẫu từng khối
```json
{"type": "stat", "value": "450", "label": "VM do VNPT Net quản lý (90,73%)", "tone": "primary"}

{"type": "split", "title": "Phân loại 450 VM theo loại hệ thống",
 "parts": [ {"value": "171", "label": "Viễn thông", "weight": 171, "desc": "**38%** · CPE/ACS, RAN"},
            {"value": "279", "label": "Công nghệ thông tin", "weight": 279, "desc": "**62%** · OSS/ERP"} ],
 "note": "Sơ bộ theo tên VM"}

{"type": "numlist", "title": "Phân loại 46 VM còn lại",
 "items": [ {"value": "13", "text": "VM thuộc VNPT-IT"}, {"value": "31", "text": "đề xuất tắt", "tone": "warn"} ]}

{"type": "category", "title": "Hệ thống viễn thông", "sub": "38% · NTL 127", "total": "171", "tone": "primary",
 "rows": [ {"label": "Quản lý CPE/ACS", "value": "48"} ]}

{"type": "progress", "label": "Tiến độ đổi mật khẩu VM", "value": "33,33%", "percent": 33.33,
 "caption": "**150/450 VM** đã hoàn thành · còn **300 VM**"}

{"type": "panel", "title": "Khó khăn, rủi ro", "tone": "warn", "bullets": ["…", "…"]}

{"type": "status_table", "rows": [ {"item": "Backup mức cấu hình", "status": "Hoàn thành", "desc": "…"} ]}

{"type": "status_list", "items": [ {"status": "Đang triển khai", "text": "…"} ]}

{"type": "steps", "title": "Trọng tâm thời gian tới", "items": ["…", "…", "…"]}

{"type": "text", "title": "Kiến nghị", "tone": "highlight", "text": "…"}

{"type": "table", "title": "Tiến độ theo đơn vị", "columns": ["Đơn vị", "Kế hoạch", "Đạt"],
 "rows": [ ["TT1", "120", "80"], ["TT2", "90", "90"] ], "num_cols": [1, 2]}

{"type": "bars", "title": "Tỷ lệ hoàn thành", "items": [ {"label": "TT1", "value": "66,7%", "percent": 66.7} ]}

{"type": "stack", "blocks": [ {"type": "stat", …}, {"type": "progress", …, "grow": true} ]}
```

## 4. Sức chứa một slide (để không tràn chữ)

Tràn ít thì script tự thu nhỏ chữ vùng nội dung (tối đa còn 85%) và báo ở `[4]`; tràn nhiều mới báo lỗi.
Vùng nội dung dưới tiêu đề cao khoảng **420 px** (bớt ~45 px nếu có `lead`, ~55 px nếu có `next`).
Ước lượng: hàng `stat` ≈ 130 px; mỗi gạch đầu dòng 1 dòng ≈ 24 px (cột rộng 1/2 slide chứa ~65 ký tự/dòng);
`status_table` ≈ 50 px/hàng; `category` ≈ 75 px + 33 px/hàng.

Giới hạn khuyến nghị:
- `title` ≤ 60 ký tự (1 dòng); `lead` ≤ 130 ký tự; `kicker` ≤ 45 ký tự.
- Tối đa **3 hàng**/slide; tối đa **4 khối**/hàng.
- `stat.value` ≤ 8 ký tự; `stat.label` ≤ 60 ký tự.
- `panel`: ≤ 4 gạch đầu dòng, mỗi gạch ≤ 120 ký tự (cột 1/2 slide).
- `status_table` ≤ 5 hàng; `category` ≤ 10 hàng; `table` ≤ 8 hàng × 5 cột; `bars` ≤ 8 mục.

Vượt mức → tách thành slide “… · CHI TIẾT” ngay sau (như slide 3 của ví dụ).
