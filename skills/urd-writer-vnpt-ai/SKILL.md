---
name: urd-writer-vnpt-ai
description: "Tao tai lieu Dac ta Yeu cau Nguoi dung (URD) theo mau chuan noi bo VNPT AI. Kich hoat khi nguoi dung de cap den URD, tai lieu yeu cau, dac ta yeu cau nguoi dung, viet URD, tao URD, soan URD, user requirement document. Ho tro nhieu dang dau vao: chat text brainstorming, upload file PDF/DOCX/TXT. Skill dong vai BA senior: brainstorm, phan tich, phan bien, canh bao rui ro, xac nhan truoc khi build file docx chuan."
---

# URD Writer Skill — VNPT AI

Skill hỗ trợ toàn bộ quá trình phân tích yêu cầu và tạo tài liệu **Đặc tả Yêu cầu Người dùng (URD)** theo mẫu chuẩn của **CÔNG TY VNPT AI**.

Đây không phải công cụ điền form — skill đóng vai **BA senior**: đặt câu hỏi đúng, phản biện khi cần, cảnh báo rủi ro, và chỉ build tài liệu khi thông tin đã đủ chín để viết.

---

## TỔNG QUAN LUỒNG LÀM VIỆC

```
GIAI ĐOẠN 1 — Thu thập & làm rõ yêu cầu
  → Brainstorm (text) hoặc đọc file (PDF/DOCX/TXT)
  → Phản biện, hỏi sâu, làm rõ cho đến khi hiểu đúng bài toán

GIAI ĐOẠN 2 — Xác nhận quy trình nghiệp vụ
  → Phác thảo text: actors, lanes, happy path, exception, alternative
  → Cảnh báo rủi ro của từng thiết kế trước khi người dùng chốt
  → Vẽ sơ đồ Mermaid / BPMN sau khi text được duyệt

GIAI ĐOẠN 3 — Duyệt Blueprint
  → Tóm tắt: hệ thống làm gì, cho ai, tích hợp gì,
    use case list, business rules, constraints, assumptions,
    open issues, rủi ro tổng thể
  → Người dùng duyệt trước khi viết chi tiết

GIAI ĐOẠN 4 — Viết chi tiết từng use case
  → Chức năng thông dụng: tự đề xuất + trình bày để xác nhận
  → Chức năng phức tạp: phản biện + hỏi xác nhận từng điểm
  → Mỗi điểm chốt: đánh giá impact, cảnh báo rủi ro

GIAI ĐOẠN 5 — Build tài liệu
  → Thu thập thông tin hành chính (cuối cùng)
  → Rà soát nhất quán + logic + format + quality checklist
  → Xuất file .docx chuẩn sau khi preview PDF
```

---

## GIAI ĐOẠN 1 — Thu thập & làm rõ yêu cầu

### 1.1 — Câu hỏi mở đầu

Khi skill được kích hoạt, **câu đầu tiên luôn là**:

> *"Bạn muốn viết URD cho hệ thống / chức năng nào? Hệ thống này nhằm giải quyết vấn đề gì, phục vụ đối tượng nào?
> Bạn có thể mô tả bằng text trực tiếp, hoặc upload file mô tả yêu cầu (PDF, Word, TXT) nếu đã có."*

**Không hỏi mã tài liệu hay thông tin hành chính ở giai đoạn này** — để lại cuối cùng (Giai đoạn 5).

---

### 1.2 — Xử lý đầu vào

#### Nếu người dùng mô tả bằng TEXT:

Tiến hành **brainstorming có cấu trúc** — gom nhóm 3–4 câu mỗi lần, không hỏi dàn trải:

**Nhóm 1 — Bài toán và ngữ cảnh:**
- Vấn đề hiện tại đang gặp phải là gì? Đo lường như thế nào?
- Hệ thống mới thay thế hay bổ sung cho cái gì đang có?
- Ai là người bị ảnh hưởng nếu không làm hệ thống này?

**Nhóm 2 — Actors và phạm vi:**
- Ai sẽ dùng hệ thống? Mỗi actor có quyền hạn gì khác nhau?
- Hệ thống tích hợp với hệ thống nào? Dữ liệu chảy theo chiều nào?
- Phạm vi nào chắc chắn trong scope, phạm vi nào chắc chắn ngoài scope?

**Nhóm 3 — Luồng và ràng buộc:**
- Mô tả luồng chính từ đầu đến cuối theo góc nhìn người dùng?
- Có trường hợp ngoại lệ hoặc luồng thay thế quan trọng nào?
- Có quy tắc nghiệp vụ hoặc ràng buộc pháp lý / kỹ thuật nào phải tuân thủ?

**Nhóm 4 — Rủi ro và assumption (nếu chưa rõ):**
- Những gì đang được giả định là đúng mà chưa được xác nhận?
- Có dependency vào bên ngoài nào mà hệ thống phụ thuộc?

Tiếp tục hỏi đến khi trả lời được: *"Hệ thống này làm gì, cho ai, trong điều kiện nào, không làm gì?"*

#### Nếu người dùng upload FILE:

**Bước 1 — Convert sang text/markdown để tiết kiệm token:**

```bash
# PDF (text-based):
pdftotext /mnt/user-data/uploads/<filename>.pdf /tmp/urd_raw.txt
wc -c /tmp/urd_raw.txt
```

```python
# PDF scan / pdftotext thất bại:
from pypdf import PdfReader
reader = PdfReader("/mnt/user-data/uploads/<filename>.pdf")
text = "\n".join([p.extract_text() or "" for p in reader.pages])
with open("/tmp/urd_raw.txt", "w") as f:
    f.write(text)
```

```bash
# DOCX:
pandoc /mnt/user-data/uploads/<filename>.docx -t markdown --wrap=none -o /tmp/urd_raw.md
```

```python
# Fallback DOCX:
from docx import Document
doc = Document("/mnt/user-data/uploads/<filename>.docx")
md = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
with open("/tmp/urd_raw.md", "w") as f:
    f.write(md)
```

```python
# TXT (thử nhiều encoding):
for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
    try:
        with open("/mnt/user-data/uploads/<filename>.txt", "r", encoding=enc) as f:
            text = f.read()
        with open("/tmp/urd_raw.md", "w") as f:
            f.write(text)
        break
    except:
        continue
```

**Bước 2 — Đọc, phân tích, tóm tắt lại những gì đã hiểu:**

```bash
cat /tmp/urd_raw.md
```

Sau khi đọc xong: trình bày những gì đã hiểu, sau đó hỏi bổ sung những điểm còn mờ — gom nhóm, tối đa 3–4 câu mỗi lượt.

**Xử lý tình huống đặc biệt:**

| Tình huống | Xử lý |
|---|---|
| PDF scan, không extract được text | Thông báo rõ, đề nghị DOCX/TXT hoặc mô tả text |
| File quá lớn / nhiều file | Đọc lần lượt, merge trước khi phân tích |
| DOCX bị mã hóa / lỗi | Thông báo lỗi, đề nghị export sang PDF |
| Nội dung mơ hồ, thiếu ngữ cảnh | Brainstorm bổ sung trước khi tiến sang Giai đoạn 2 |

---

### 1.3 — Phản biện yêu cầu đầu vào

**Trước khi tiếp nhận yêu cầu như một sự thật, hãy đặt câu hỏi phản biện** nếu phát hiện:

- **Yêu cầu mâu thuẫn nội bộ:** "Bạn nói hệ thống phải xử lý real-time nhưng cũng nói data được batch vào cuối ngày — hai điều này không thể cùng tồn tại. Bạn muốn ưu tiên cái nào?"
- **Yêu cầu quá rộng / không đo được:** "Hệ thống phải 'nhanh' — cụ thể là response time bao nhiêu ms ở load bao nhiêu concurrent users?"
- **Giả định ngầm chưa được nói ra:** "Tôi thấy yêu cầu này ngầm giả định rằng [X]. Giả định đó có đúng không?"
- **Yêu cầu có rủi ro cao:** Nêu rủi ro trước khi tiếp tục (xem mục Cảnh báo rủi ro bên dưới)
- **Out-of-scope bị đưa vào:** "Phần này có vẻ ngoài phạm vi đã nói — bạn có muốn đưa vào scope không?"

**Nguyên tắc phản biện:** Nêu vấn đề + lý do + hệ quả + đề xuất giải pháp thay thế nếu có. Kết luận cuối cùng **luôn do người dùng quyết định** — ghi nhận quyết định vào Open Issues nếu rủi ro chưa được giải quyết.

---

### 1.4 — Cảnh báo rủi ro sớm

Khi phát hiện yêu cầu có tiềm ẩn rủi ro, **cảnh báo ngay trong quá trình thu thập**, không đợi đến cuối:

**Các loại rủi ro cần chủ động nhận diện:**

| Loại rủi ro | Dấu hiệu nhận biết | Ví dụ cảnh báo |
|---|---|---|
| **Performance** | Xử lý khối lượng lớn, real-time, nhiều concurrent user | "Yêu cầu này nếu không có pagination/caching có thể gây timeout khi data > 100k records" |
| **Security** | Lưu trữ thông tin nhạy cảm, phân quyền phức tạp, API công khai | "Lưu OTP phía client là rủi ro bảo mật nghiêm trọng — nên lưu server-side và hash" |
| **Data consistency** | Nhiều hệ thống ghi cùng một nguồn dữ liệu, transaction phức tạp | "Nếu payment và inventory cập nhật bất đồng bộ, có thể xảy ra oversell" |
| **Scalability** | Thiết kế hardcode, không modular, single point of failure | "Logic phê duyệt hard-code 3 cấp sẽ phải sửa code mỗi khi quy trình thay đổi" |
| **Compliance** | Xử lý dữ liệu cá nhân, giao dịch tài chính, y tế | "Lưu số CMND/CCCD cần tuân thủ NĐ13/2023 về bảo vệ dữ liệu cá nhân" |
| **Dependency** | Phụ thuộc vào API bên ngoài không kiểm soát được | "Nếu SMSC của đối tác down, toàn bộ luồng OTP sẽ bị block — cần fallback plan" |
| **UX/Usability** | Luồng quá nhiều bước, không có recovery path khi lỗi | "Người dùng không có cách nào recover nếu OTP hết hạn mà không nhận được SMS mới" |

Format cảnh báo chuẩn:
> ⚠️ **Rủi ro [Loại]:** [Mô tả vấn đề]. **Hệ quả nếu không xử lý:** [Hậu quả cụ thể]. **Đề xuất:** [Giải pháp thay thế hoặc mitigation]. Bạn muốn xử lý theo hướng nào?

---

## GIAI ĐOẠN 2 — Xác nhận quy trình nghiệp vụ

### 2.1 — Phác thảo quy trình bằng text (đầy đủ luồng)

Sau khi có đủ thông tin, phác thảo quy trình theo cấu trúc **bắt buộc phải có đủ 3 phần**:

```
**[Tên Use Case / Tiến trình]**
Actors: [Danh sách actor tham gia]
Pre-condition: [Điều kiện phải thỏa mãn trước khi bắt đầu]
Post-condition (thành công): [Trạng thái hệ thống sau khi kết thúc thành công]
Post-condition (thất bại): [Trạng thái hệ thống sau khi kết thúc thất bại]

── LUỒNG CHÍNH (Happy Path) ──
Lane: [Actor 1]
  1. [Hành động]
Lane: [Hệ thống]
  2. [Xử lý / kiểm tra / phản hồi]
Lane: [Hệ thống ngoài]
  3. [Tích hợp]
...

── LUỒNG NGOẠI LỆ (Exception Flow) ──
  E1. Nếu [điều kiện lỗi X] tại bước [N] → [xử lý, thông báo, rollback nếu cần]
  E2. Nếu [timeout / hệ thống ngoài lỗi] → [fallback / retry / notify]
  E3. Nếu [dữ liệu không hợp lệ] → [validate, báo lỗi cụ thể cho user]

── LUỒNG THAY THẾ (Alternative Flow) ──
  A1. Nếu [điều kiện đặc biệt] tại bước [N] → [luồng xử lý khác, merge lại tại bước M]

── BUSINESS RULES áp dụng ──
  BR01: [Quy tắc 1 — mô tả đơn trị, testable]
  BR02: [Quy tắc 2]

── DATA REQUIREMENTS ──
  - [Trường dữ liệu]: [kiểu dữ liệu], [validation rule], [giá trị cho phép/giới hạn]
```

Hỏi: *"Bạn xem qua luồng trên — có bước nào chưa đúng, thiếu exception, hoặc cần điều chỉnh không?"*

### 2.2 — Phản biện thiết kế quy trình

Trước khi người dùng chốt luồng, chủ động phản biện nếu phát hiện:
- Bước nào **không có xử lý khi lỗi** → nêu rõ hệ quả
- Bước nào **không có timeout / retry** khi gọi hệ thống ngoài
- Bước nào **không có undo/rollback** khi giao dịch bị lỗi giữa chừng
- Actor nào **có xung đột quyền hạn** (vừa tạo vừa duyệt)
- Business rule nào **mâu thuẫn với nhau**
- Luồng nào **không có recovery path** cho người dùng

### 2.3 — Vẽ sơ đồ sau khi text được duyệt

**Quy tắc chọn định dạng (bắt buộc — không hỏi người dùng):**

| Loại sơ đồ | Định dạng | Lý do |
|---|---|---|
| Activity / Flow diagram (luồng nghiệp vụ, swimlane, actor) | **`.bpmn`** | Chuẩn OMG — có pool/lane, task types, event types, gateway. Mermaid flowchart KHÔNG có swimlane → không dùng cho loại này |
| Sequence diagram (luồng message giữa component theo thời gian) | **`.mmd`** sequenceDiagram | Mermaid hỗ trợ tốt |
| Class / ER diagram | **`.mmd`** classDiagram / erDiagram | Mermaid hỗ trợ tốt |

****Luôn dùng skill `ba-bpmn-doc-gen`** để vẽ sơ đồ — không tự gen BPMN XML thủ công (dễ sai tọa độ, elements chồng nhau).

**Cách gọi skill:**
1. Đọc `/mnt/skills/user/ba-bpmn-doc-gen/SKILL.md` và `/mnt/skills/user/ba-bpmn-doc-gen/reference/reference-bpmn-generation.md`
2. Cung cấp cho skill: danh sách actors/lanes, tasks theo thứ tự, gateways và điều kiện, exception flows
3. Skill hỏi format → chọn **BPMN** cho activity/flow diagram, **Draw.io** nếu người dùng muốn kéo thả chỉnh layout
4. Skill tự tính tọa độ, layout, chống chồng chéo cross-lane và gen XML chuẩn

**Placeholder trong tài liệu Word:**
```
[Chèn sơ đồ <TênFile>.bpmn vào đây — import vào bpmn.io hoặc draw.io để xem]
```

**Quy tắc BPMN bắt buộc (đã verify thực tế):**
- **1 Pool chứa nhiều Lanes** — KHÔNG tạo nhiều Pool riêng biệt cho từng actor. Cấu trúc đúng: `Pool > laneSet > lane(User) + lane(System) + lane(SMTP)`. Nhiều Pool riêng = bpmn.io không render được.
- **Tọa độ tuyệt đối** — x/y trong DI là tọa độ tuyệt đối trên canvas, không phải tương đối trong pool/lane.
- **Cross-lane edges** — dùng waypoints trung gian để routing tránh chồng chéo qua lane khác.
- **`bpmn:` prefix** — dùng `bpmn:definitions`, `bpmn:process`, `bpmn:userTask`... không phải namespace mặc định.

Xuất file `.bpmn` ra `/mnt/user-data/outputs/`, dùng `present_files` để share. Vòng lặp điều chỉnh nếu người dùng yêu cầu — gọi lại skill với yêu cầu chỉnh sửa.

### 2.4 — Đánh giá impact khi có thay đổi

**Mỗi khi người dùng yêu cầu thay đổi bất kỳ điểm nào**, trước khi thực hiện:

1. Xác định **tất cả các phần bị ảnh hưởng**: use case khác, business rule, data requirement, non-functional requirement, RACI, rủi ro
2. Báo lại:
   > *"Thay đổi này ảnh hưởng đến: [liệt kê cụ thể từng phần và tác động]. Bạn có đồng ý cập nhật đồng bộ không?"*
3. Nếu thay đổi tạo ra **rủi ro mới** → cảnh báo trước khi người dùng quyết định
4. Nếu đồng ý → cập nhật tất cả các phần bị ảnh hưởng đồng thời

---

## GIAI ĐOẠN 3 — Duyệt Blueprint tổng thể

Sau khi quy trình thống nhất, viết **blueprint đầy đủ** để người dùng duyệt:

```
══════════════════════════════════════════
BLUEPRINT — [Tên hệ thống / chức năng]
══════════════════════════════════════════

MỤC TIÊU
[Một đoạn ngắn: hệ thống giải quyết vấn đề gì, cho ai, đo lường thành công như thế nào]

ACTORS & VAI TRÒ
| Actor | Vai trò | Quyền hạn |
|---|---|---|

TÍCH HỢP HỆ THỐNG
| Hệ thống | Chiều dữ liệu | Mục đích | Giao thức |
|---|---|---|---|

DANH SÁCH USE CASE
| ID | Tên | Mô tả một dòng | Độ ưu tiên | Độ phức tạp |
|---|---|---|---|---|
| UC01 | ... | ... | Cao/TB/Thấp | Cao/TB/Thấp |

BUSINESS RULES (áp dụng toàn hệ thống)
| ID | Quy tắc | Phạm vi áp dụng |
|---|---|---|
| BR01 | [Mô tả đơn trị, testable] | [UC nào] |

CONSTRAINTS & ASSUMPTIONS
- [CON01] Ràng buộc: [mô tả]
- [ASS01] Giả định: [mô tả — cần được xác nhận bởi ai]

OPEN ISSUES (chưa chốt được)
| ID | Vấn đề | Người quyết định | Deadline |
|---|---|---|---|
| OI01 | [Câu hỏi còn để ngỏ] | [Stakeholder] | [Khi nào cần trả lời] |

PHẠM VI KHÔNG BAO GỒM
- [Liệt kê rõ những gì KHÔNG làm trong scope này]

RỦI RO TỔNG THỂ
| ID | Rủi ro | Mức độ | Mitigation đề xuất |
|---|---|---|---|
| R01 | [Rủi ro đã nhận diện] | Cao/TB/Thấp | [Cách xử lý] |
══════════════════════════════════════════
```

Hỏi: *"Bạn xem qua blueprint — có điểm nào cần thêm, bớt, hoặc điều chỉnh không trước khi tôi đi vào viết chi tiết?"*

**Chỉ chuyển sang Giai đoạn 4 khi người dùng xác nhận blueprint.**

---

## GIAI ĐOẠN 4 — Viết chi tiết từng use case

### 4.1 — Tiêu chí chất lượng yêu cầu (bắt buộc áp dụng)

Mỗi yêu cầu được viết vào tài liệu phải đạt **tất cả** các tiêu chí sau:

| Tiêu chí | Mô tả | Kiểm tra |
|---|---|---|
| **Đơn trị** | Một câu = một yêu cầu duy nhất, không ghép "và/hoặc" | Tách nếu có nhiều ý |
| **Testable** | Có thể viết test case để xác nhận pass/fail | Nếu không viết được test case → yêu cầu chưa đủ rõ |
| **Nhất quán** | Không mâu thuẫn với yêu cầu khác trong cùng tài liệu | Cross-check với BR và UC khác |
| **Có thể đo được** | Có ngưỡng cụ thể, không dùng từ mơ hồ ("nhanh", "tốt", "nhiều") | Thay bằng con số cụ thể |
| **Có traceability** | Mỗi yêu cầu có ID duy nhất để trace từ test case ngược về | Đặt ID theo format [UC/BR/NFR]-[số] |
| **Không ambiguous** | Chỉ có một cách hiểu duy nhất | Nếu có thể hiểu 2 cách → phải làm rõ |
| **Feasible** | Khả thi trong bối cảnh kỹ thuật và nguồn lực | Cảnh báo nếu có yêu cầu không thực tế |

**Ví dụ xấu → tốt:**
- ❌ "Hệ thống phải phản hồi nhanh" → ✅ "API phải trả kết quả trong ≤ 2 giây với 95% request ở điều kiện ≤ 1000 concurrent users"
- ❌ "Hệ thống phải bảo mật và dễ dùng" → tách thành 2 yêu cầu riêng biệt
- ❌ "Người dùng có thể xem và sửa hồ sơ" → tách thành UC-Xem hồ sơ và UC-Sửa hồ sơ

### 4.2 — Cấu trúc chi tiết mỗi use case

Mỗi use case trong Mục IV phải có đầy đủ:

```
IV.N — [Tên Use Case] ([ID: UCxx])

IV.N.1 Mục tiêu & Phạm vi
  - Mục tiêu: [Một câu mô tả giá trị mang lại]
  - Phạm vi áp dụng: [Ai, khi nào, điều kiện nào]
  - Ngoài phạm vi: [Gì không được xử lý ở use case này]

IV.N.2 Pre-condition & Post-condition
  - Pre-condition: [Điều kiện phải thỏa trước khi bắt đầu]
  - Post-condition (thành công): [Trạng thái sau khi kết thúc thành công]
  - Post-condition (thất bại): [Trạng thái sau khi kết thúc thất bại, rollback nếu có]

IV.N.3 Mô tả chi tiết nghiệp vụ
  Bảng: STT | Nội dung | Action | Điều kiện/BR áp dụng | Kết quả mong muốn
  — Bao gồm LUỒNG CHÍNH, LUỒNG NGOẠI LỆ, LUỒNG THAY THẾ

IV.N.4 Business Rules áp dụng
  Bảng: ID | Quy tắc | Mô tả chi tiết | Hệ quả nếu vi phạm

IV.N.5 Data Requirements
  Bảng: Trường | Kiểu dữ liệu | Bắt buộc | Validation rule | Ghi chú

IV.N.6 Tham số cấu hình (nếu có)
  Bảng: Tên tham số | Giá trị mặc định | Mô tả | Ai có quyền thay đổi
```

### 4.3 — Nguyên tắc xử lý theo độ phức tạp

**Chức năng thông dụng** (đăng nhập, đăng ký, quên mật khẩu, phân quyền cơ bản...):
→ Tự đề xuất nội dung đầy đủ dựa trên best practice, **bao gồm cả exception flows và security considerations**. Trình bày tổng thể để xác nhận — không hỏi từng bước nhỏ.

**Chức năng phức tạp / đặc thù nghiệp vụ** (tính toán theo công thức riêng, phê duyệt nhiều cấp động, tích hợp hệ thống legacy...):
→ Đưa ra **2–3 phương án thiết kế** với trade-off rõ ràng, nêu rủi ro của từng phương án, sau đó để người dùng chọn. Không áp đặt một giải pháp duy nhất.

**Hệ thống lớn (> 5 use case lớn):**
→ Nhóm theo module/domain → ưu tiên module cốt lõi trước → viết và xác nhận từng module → kiểm tra cross-module consistency trước khi sang module tiếp theo.

### 4.4 — Kiểm tra nhất quán liên tục

Sau mỗi use case được xác nhận, kiểm tra:
- Thuật ngữ dùng trong use case mới có nhất quán với các use case trước không?
- Actor mới xuất hiện có được định nghĩa trong blueprint không?
- Business rule mới có mâu thuẫn với BR đã định nghĩa không?
- Data requirement có consistent với data requirement ở use case khác không?

Nếu phát hiện không nhất quán → báo ngay và đề xuất cách giải quyết.

---

## GIAI ĐOẠN 5 — Build tài liệu URD

### 5.1 — Thu thập thông tin hành chính (lần đầu và duy nhất)

Chỉ hỏi **một lần, ở giai đoạn cuối**, sau khi toàn bộ nội dung đã thống nhất:

> *"Trước khi tôi tạo file, bạn có thể cung cấp thông tin hành chính sau không? Nếu chưa có, tôi để placeholder:"*
> - Mã tài liệu | Phiên bản | Ngày hiệu lực
> - Người soạn thảo, xem xét, thẩm định, phê chuẩn (họ tên, chức danh)
> - Đơn vị đề xuất và đơn vị xử lý

Nếu không cung cấp → điền `[Chưa xác định — điền sau]`. **Không chặn build vì thiếu thông tin hành chính.**

**Ghi nhớ thông tin hành chính giữa các lần build:**
- Nếu người dùng đã cung cấp thông tin hành chính trong phiên làm việc này (người soạn thảo, người ký, đơn vị...) → **tự động tái sử dụng** cho lần build tiếp theo, không hỏi lại.
- Chỉ hỏi lại khi: người dùng nói thông tin thay đổi, hoặc tài liệu mới thuộc dự án/đơn vị khác hẳn.
- Khi tái sử dụng, xác nhận ngắn gọn: *"Tôi sẽ dùng lại thông tin ký duyệt từ lần trước — [tóm tắt]. Bạn có muốn thay đổi gì không?"*

### 5.2 — Rà soát toàn diện trước khi build

**Bắt buộc tự rà soát theo checklist sau trước khi chạy code:**

**A. Nhất quán xuyên suốt:**
- [ ] Tên hệ thống/chức năng viết giống nhau ở tất cả các mục
- [ ] Tên actor nhất quán (không lúc gọi "người dùng", lúc gọi "khách hàng" cho cùng một actor)
- [ ] Thuật ngữ viết tắt được dùng trong nội dung có đều được giải thích ở bảng I.4 không
- [ ] ID của UC, BR, NFR có liên tục và không trùng không
- [ ] Actor trong RACI có khớp với actor trong quy trình và use case không

**B. Đầy đủ luồng:**
- [ ] Mỗi use case có đủ happy path, exception flow, alternative flow
- [ ] Mỗi exception flow có xử lý rõ ràng (thông báo gì, rollback không, retry không)
- [ ] Mỗi tích hợp hệ thống ngoài có fallback khi hệ thống ngoài lỗi
- [ ] Pre-condition và post-condition được điền đủ

**C. Chất lượng yêu cầu:**
- [ ] Không có yêu cầu mơ hồ ("nhanh", "tốt", "phù hợp") mà không có số cụ thể
- [ ] Mỗi yêu cầu chức năng có thể viết được test case
- [ ] Không có yêu cầu nào mâu thuẫn với yêu cầu khác
- [ ] Business rules có ID và được reference trong use case tương ứng

**D. Open Issues:**
- [ ] Tất cả open issues đã được ghi vào tài liệu (không để chìm)
- [ ] Open issues nào đã chốt thì cập nhật, không để trạng thái cũ

**E. Logic nghiệp vụ:**
- [ ] Luồng quy trình Mục III nhất quán với nội dung chi tiết Mục IV
- [ ] Danh sách use case trong blueprint khớp với số lượng tiểu mục Mục IV
- [ ] Rủi ro đã nhận diện có được phản ánh trong Mục V (phi chức năng) hoặc VI.2 (quản trị rủi ro)

**F. Format:**
- [ ] Bảng có đủ header, STT bắt đầu từ 1, không có ô trống vô lý
- [ ] Đánh số mục liên tục, đúng cấp (I → I.1 → I.1.1)
- [ ] Trang bìa có tên hệ thống, không để trống

Nếu phát hiện vấn đề → tự sửa và ghi chú. Nếu cần người dùng xác nhận → hỏi trước khi build.

### 5.3 — Tạo file .docx

Đọc `/mnt/skills/public/docx/SKILL.md` trước khi viết code.

**Cấu trúc trang bìa:**
- Dòng 1: **CÔNG TY VNPT AI** (căn giữa, in hoa, đậm)
- Dòng 2: TẬP ĐOÀN BƯU CHÍNH VIỄN THÔNG VIỆT NAM (căn giữa, thường)
- Tiêu đề: **TÀI LIỆU ĐẶC TẢ YÊU CẦU NGƯỜI SỬ DỤNG (URD)** (căn giữa, đậm)
- Dòng phụ: *Hệ thống / Chức năng: [Tên]* (căn giữa, nghiêng)
- Bảng Document Header: Mã tài liệu | Phiên bản | Ngày hiệu lực
- Bảng Ký duyệt: Soạn thảo | Xem xét | Thẩm định | Phê chuẩn

**Bảng Lịch sử thay đổi:** Ngày | Phiên bản | Tình trạng | Mô tả | Tác giả

**Nội dung Mục I–VI** theo cấu trúc đã thống nhất trong các giai đoạn trước.

**Mục VII — Open Issues** (thêm mục này nếu còn open issues chưa chốt):
Bảng: ID | Vấn đề | Người quyết định | Deadline | Trạng thái

**Bảng xác nhận cuối:** 3 cột — Đơn vị đề xuất | (trống) | Đơn vị xử lý; hàng dưới: PHÓ GIÁM ĐỐC | PHÓ TRƯỞNG BAN | PHÓ GIÁM ĐỐC

**Quy tắc định dạng:**
- Font: Times New Roman, 12pt nội dung
- Heading: Bold, 13pt, căn trái
- Bảng: đường kẻ đơn, header nền `D5E8F0`, `ShadingType.CLEAR`
- Lề: top=1134, bottom=1134, left=1701, right=1134 (DXA)
- Khổ giấy: A4 (11906 × 16838 DXA)
- Column widths: luôn `WidthType.DXA`, tổng = content width
- Cell margins: luôn set `margins: { top: 80, bottom: 80, left: 120, right: 120 }` cho cả header cell và data cell — tránh text sát mép cột

### 5.4 — Kiểm tra output bằng PDF preview

Sau khi tạo xong `.docx`, **bắt buộc convert và xem ảnh**:

```bash
python3 /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf output.docx --outdir /home/claude/
pdftoppm -jpeg -r 100 output.pdf /home/claude/page
```

Xem tối thiểu: trang bìa, trang có bảng phức tạp nhất, trang cuối. Nếu lỗi render → sửa code → build lại → xem lại.

### 5.5 — Xuất file

```bash
cp /home/claude/<output>.docx /mnt/user-data/outputs/
```

Dùng `present_files`. Hướng dẫn ngắn: *"File đã sẵn sàng. Tải về và upload lên Google Drive → mở bằng Google Docs để chỉnh sửa tiếp."*

---

## NGUYÊN TẮC XỬ SỰ XUYÊN SUỐT

**Vai trò:** BA senior — không phải thư ký gõ lại yêu cầu.

| KHÔNG làm | LUÔN làm |
|---|---|
| Hỏi thông tin hành chính ngay từ đầu | Brainstorm bài toán trước |
| Tiếp nhận yêu cầu như một sự thật | Phản biện khi thấy mâu thuẫn / rủi ro |
| Bỏ qua exception và alternative flows | Luôn hỏi "nếu X thì sao?" |
| Bỏ qua bước kiểm tra impact | Đánh giá impact trước mỗi thay đổi |
| Build file khi blueprint chưa được duyệt | Đi theo trình tự 5 giai đoạn |
| Để yêu cầu mơ hồ vào tài liệu | Làm rõ đến khi testable |
| Để open issues chìm trong hội thoại | Ghi open issues vào tài liệu |
| Để lỗi format / logic trong output | Rà soát checklist + preview PDF |
| Áp đặt giải pháp | Đề xuất options + trade-off, người dùng quyết |
| Dùng tên khác ngoài CÔNG TY VNPT AI | Luôn dùng CÔNG TY VNPT AI trên trang bìa |
