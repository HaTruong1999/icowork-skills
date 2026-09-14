---
name: ekyc-weekly-report
description: Generate the VNPT eKYC weekly status report (interactive HTML, matching the "Báo cáo Tuần — VNPT eKYC" template) from the weekly input Excel file. Trigger this whenever the user uploads a weekly eKYC report Excel file (sheet with tables like "Mã KR" / "Hoạt động / tính năng" / "Key Result" / "Đơn vị" / "Target 2026"), or asks to turn this week's Excel data into the weekly HTML report, or asks for "báo cáo tuần eKYC", "báo cáo tuần VNPT", or similar. Also use this skill if the user wants the blank input Excel template to fill in for a future week.
---

# Báo cáo Tuần eKYC (VNPT) — Excel → HTML

Converts the weekly eKYC input Excel file into the polished, interactive
"Báo cáo Tuần — VNPT eKYC" HTML report (same look/feel and editing
JavaScript as the original hand-built template).

## Files in this skill

- `assets/input_template.xlsx` — the blank Excel template the user fills in
  every week (give this to the user if they ask for a fresh copy, or if
  their uploaded file is missing a section listed below).
- `assets/part_top.html` / `assets/part_bottom.html` — static head/CSS/JS
  chrome of the report, reused unchanged every week.
- `scripts/generate_report.py` — parses the filled Excel and renders the
  final HTML report.

## Workflow

1. Locate the user's uploaded weekly Excel file (usually named like
   `eKYC_Báo_cáo_tuần.xlsx` or `eKYC_Báo_cáo_tuần_<ngày>.xlsx`).
2. Run:
   ```
   python3 /mnt/skills/.../ekyc-weekly-report/scripts/generate_report.py <input.xlsx> <output.html>
   ```
   (copy the skill's `scripts/` and it will find `assets/part_top.html` /
   `part_bottom.html` automatically next to it — keep the two directories
   together, don't move the script alone.)
3. Copy the output `.html` to `/mnt/user-data/outputs/`, then call
   `present_files` so the user can open/download it. Do not just print the
   HTML in chat — it must be delivered as a file for the interactive
   editor and print/PDF button to work.
4. Briefly tell the user which sections were auto-filled from data vs.
   left as placeholders (e.g. "chưa có dữ liệu điểm nổi bật tuần này" if
   that section was empty in their Excel), so they know what to touch up
   using the report's own "✏️ Bật sửa toàn bộ chữ" button.

If the user doesn't have a filled Excel yet and asks for the blank
template, just share `assets/input_template.xlsx` directly via
`present_files` (copy it to the outputs dir first).

## Expected Excel layout

The script looks for each of these by scanning cell values — sections can
be in any row order, and rows/columns can be added or removed freely by
the user, as long as the header text matches. Missing optional sections
just produce sensible placeholder content in the HTML (never an error).

### 1. KR năm table (required for section 5 of the report)
A row containing the header **"Mã KR"** starts the table. Columns:
`Mã KR | Key Result | Đơn vị | Target 2026 | Tuần trước | Tuần này | Ghi chú | Trạng thái (tuỳ chọn)`.
- Progress % = Tuần này ÷ Target (numeric target) or Tuần này treated as a
  0–1 ratio (qualitative target like "GTM"). If Tuần này is blank, Tuần
  trước is used instead.
- Status badge (Đúng tiến độ ≥85% teal / Có rủi ro 50–85% amber / Trễ
  tiến độ <50% red) is computed automatically, **unless** the optional
  "Trạng thái" column is filled with one of those three exact strings, in
  which case that overrides the computed value.

### 2. Hoạt động trọng tâm table (required for section 2, and feeds sections 3 & 4)
A row containing the header **"Hoạt động / tính năng"** starts the table.
Columns: `Hoạt động / tính năng | Trạng thái | Gắn KR / BAU / Khác | Đã làm | Sắp tới | Vướng`.
- `Trạng thái` free text is colored by keyword match ("triển khai"→blue,
  "vận hành"/"hoàn thành"→teal, "trễ"/"chậm"→red, "hỗ trợ"/"rủi ro"→amber,
  default blue).
- `Đã làm`: lines starting with `-` become bullet points in the activity's
  detail column (section 2).
- `Sắp tới`: each non-empty row is appended as one bullet in section 4
  ("Kế hoạch Trọng tâm Tuần tới"), prefixed with the activity name in bold.
- `Vướng`: each non-empty row becomes one risk/blocker card in section 3,
  with a placeholder "[Điền đề xuất cụ thể]" for the escalation ask — the
  user should fill that in manually in the browser editor since the
  specific ask to leadership isn't derivable from the data.

### 3. "THÔNG TIN CHUNG" section (optional — header fields)
A cell containing "THÔNG TIN CHUNG" marks the section title; the next row
is the header (`Trường | Giá trị`), followed by rows:
`GĐ Sản phẩm`, `Kỳ báo cáo`, `Trạng thái chung tuần`.
`Trạng thái chung tuần` text is colored by keyword ("tốt"/"ổn định"→teal,
"lưu ý"/"cảnh báo"→amber, "rủi ro"/"trễ"/"chậm"→red, default blue).

### 4. "CHỈ SỐ VẬN HÀNH TUẦN" section (optional — section 1 metric cards)
Marked by a cell containing "CHỈ SỐ VẬN HÀNH TUẦN". Header row:
`Tên chỉ số | Icon (tuỳ chọn) | Màu thẻ (tuỳ chọn) | Giá trị tuần này | Giá trị tuần trước | % thay đổi (tuỳ chọn) | Xu hướng | Ghi chú / tag`.
- `Màu thẻ`: one of `blue/teal/purple/amb/red`; blank → colors rotate
  automatically.
- `Xu hướng`: one of `tăng-tốt / giảm-tốt / tăng-xấu / giảm-xấu / ổn định`
  — controls the arrow direction and whether it's shown green (good) or
  red (bad).
- If this whole section is missing, section 1 renders with 0 cards and a
  visible "➕ Thêm ô chỉ số" button for manual entry.

### 5. "ĐIỂM NỔI BẬT TRONG TUẦN" section (optional — highlights)
Marked by a cell containing "ĐIỂM NỔI BẬT". Header row:
`Loại (hợp đồng / sự cố / nâng cấp / khác) | Nội dung (dùng **chữ** để in đậm)`.
- `Loại` maps to an icon + color block: hợp đồng→💼 blue, sự cố→🚨 red,
  nâng cấp→🚀 teal, khác/blank→📌 teal.
- `Nội dung` supports `**bold**` markdown-style bolding; everything else
  is shown as plain text (newlines become `<br>`).
- If missing, a single placeholder highlight explains the section is
  empty and points at the "➕ Thêm điểm nổi bật" button.

## Notes / gotchas

- Any row whose first cell starts with "Ghi chú" (the in-sheet instructional
  notes explaining how to fill each section, e.g. "Ghi chú: 'Trạng thái' để
  trống sẽ được tự tính...") is treated as sheet-only guidance and is
  **skipped** by `read_table` — it must never become a fake KR / activity /
  metric card in the generated report. This is handled by `is_note_row()` in
  `generate_report.py`. Do not remove this filter when editing the script.
- The generated HTML keeps the original template's built-in floating
  toolbar with exactly three user-facing buttons, always visible (not
  hidden) in the bottom-right corner:
  - **"✏️ Chỉnh sửa"** — turns on full inline text editing across the whole
    report; toggles to "✅ Hoàn tất chỉnh sửa" while active. While editing,
    a **"💾 Xuất file mới (.html)"** button appears to save the edited
    report as a new standalone HTML file (and "Huỷ bỏ" to discard edits).
  - **"📄 Tóm tắt"** — builds a plain-text summary of the week (overall
    status, KPI cards, highlights, activity progress, escalation asks) from
    whatever is currently in the report and copies it to the clipboard, so
    the user can paste it straight into Zalo/Slack/email for their manager.
  - **"🖨️ Xuất PDF"** — calls the browser print dialog (`window.print()`),
    which the user can save as PDF.
  These three buttons are the only editor controls that should be surfaced
  to the user; keep their ids (`edtbtn`, `edtcopy`, `edtprint`) stable in
  `part_bottom.html` since the accompanying JS wires up by id.
- Numbers/text are HTML-escaped; don't worry about the user pasting raw
  `<`, `>`, `&` in cells.
- If the uploaded Excel has a totally different table layout (renamed
  headers, single flat table, etc.), don't force-fit it into this script —
  read it directly and build the sections by hand instead, reusing
  `assets/part_top.html` / `part_bottom.html` as the static chrome.
