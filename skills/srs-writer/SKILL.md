---
name: srs-writer
description: "Tao tai lieu Dac ta Yeu cau Phan mem (SRS) theo mau chuan noi bo VNPT AI. Kich hoat khi nguoi dung de cap den SRS, software requirement specification, dac ta ky thuat, viet SRS, tao SRS. Ho tro dau vao: text, file PDF/DOCX/TXT, anh mockup. Skill dong vai BA senior: phan tich sau, phan bien, canh bao rui ro, sinh ra bo output day du (SRS.docx + feature .md cho developer/AI code + API .md + flow .mmd/.bpmn)."
---

# SRS Writer Skill — VNPT AI

Skill tạo **Đặc tả Yêu cầu Phần mềm (SRS)** theo chuẩn **CÔNG TY VNPT AI** — tài liệu kỹ thuật chi tiết hơn URD, đủ để developer và AI coding tool đọc và code được.

**SRS khác URD ở chỗ:**
- URD: *"Hệ thống cần làm gì"* — góc nhìn nghiệp vụ, cho PM/BA/stakeholder
- SRS: *"Hệ thống làm như thế nào"* — góc nhìn kỹ thuật, cho developer/tester/AI

**Output bộ SRS gồm:**
1. `SRS.docx` — tài liệu gốc đầy đủ, BA viết, PM/Tech Lead approve
2. `<Feature/UC>_spec.md` — file markdown phái sinh cho developer/AI code (mỗi feature/UC một file)
3. `<API>_spec.md` — file API spec riêng cho từng API endpoint (nếu có)
4. `<Flow>_flow.mmd` hoặc `.bpmn` — sơ đồ luồng

---

## TỔNG QUAN LUỒNG LÀM VIỆC

```
GIAI ĐOẠN 0 — Xác định context
  → Dự án organize theo Use Case hay Feature/Function?
  → Có URD gốc không? Có Figma/mockup không?
  → Loại hệ thống: Web app / API platform / Mobile / Mix?

GIAI ĐOẠN 1 — Thu thập & làm rõ yêu cầu
  → Đọc URD / file đầu vào / text mô tả
  → Phân tích mockup ảnh nếu có (extract-once, lưu text)
  → Phản biện, hỏi sâu về kỹ thuật

GIAI ĐOẠN 2 — Xác nhận kiến trúc & luồng kỹ thuật
  → Phác thảo: tech stack, integration points, data flow
  → Vẽ sơ đồ .mmd/.bpmn sau khi text được duyệt

GIAI ĐOẠN 3 — Duyệt Feature/UC List
  → Blueprint kỹ thuật: feature list, API list, data model sơ bộ
  → Xác nhận trước khi viết chi tiết

GIAI ĐOẠN 4 — Viết chi tiết từng Feature/UC
  → Feature thông dụng: tự đề xuất + xác nhận
  → Feature phức tạp: phản biện + hỏi từng điểm
  → Sinh file .md phái sinh song song

GIAI ĐOẠN 5 — Build tài liệu
  → Thu thập thông tin hành chính (cuối cùng)
  → Rà soát chất lượng toàn diện
  → Build SRS.docx + xuất các file .md + .mmd/.bpmn
```

---

## GIAI ĐOẠN 0 — Xác định context

Câu hỏi đầu tiên khi kích hoạt skill:

> *"Bạn muốn viết SRS cho hệ thống / chức năng nào? Và cho tôi biết thêm:"*
> 1. *Dự án này đã có URD chưa? Nếu có, bạn có thể upload để tôi đọc không?*
> 2. *Hệ thống organize theo Use Case hay Feature/Function?*
> 3. *Có ảnh mockup / Figma export không? (Không cần thiết — có thì tốt hơn)*
> 4. *Loại output chính: Web app có UI, API-only, Mobile app, hay mix?*

**Không hỏi thông tin hành chính ở đây** — để lại Giai đoạn 5.

**Nhận diện tự động loại hệ thống:**

| Dấu hiệu | Loại | Ảnh hưởng đến SRS |
|---|---|---|
| Có màn hình người dùng tương tác | Web/Mobile app | Cần UI Behavior spec, validation table |
| Chỉ có endpoint, không có UI | API platform | Cần API spec chi tiết, không cần UI spec |
| Vừa có UI vừa có API | Mix | Cả hai phần trên |
| Batch processing, scheduled job | Backend service | Cần trigger, schedule, error handling spec |

---

## GIAI ĐOẠN 1 — Thu thập & làm rõ yêu cầu

### 1.1 — Xử lý đầu vào

#### Nếu có URD gốc (file PDF/DOCX/TXT):

```bash
# Convert sang markdown để tiết kiệm token
pandoc /mnt/user-data/uploads/<filename>.docx -t markdown --wrap=none -o /tmp/srs_input.md
cat /tmp/srs_input.md
```

```python
# Fallback nếu pandoc lỗi:
from docx import Document
doc = Document("/mnt/user-data/uploads/<filename>.docx")
text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
with open("/tmp/srs_input.md", "w") as f:
    f.write(text)
```

```python
# PDF:
from pypdf import PdfReader
reader = PdfReader("/mnt/user-data/uploads/<filename>.pdf")
text = "\n".join([p.extract_text() or "" for p in reader.pages])
with open("/tmp/srs_input.md", "w") as f:
    f.write(text)
```

Sau khi đọc URD: tóm tắt những gì đã hiểu về requirement, sau đó **hỏi bổ sung phần kỹ thuật** mà URD thường không có:
- Tech stack dự kiến (ngôn ngữ, framework, DB)?
- Authentication mechanism (JWT, OAuth, session, API key)?
- Deployment environment (cloud, on-premise, hybrid)?
- Có constraint về performance/security không?

#### Nếu người dùng mô tả bằng TEXT:

Brainstorm có cấu trúc — gom nhóm 3–4 câu mỗi lần:

**Nhóm 1 — Bài toán & ngữ cảnh:**
- Hệ thống giải quyết vấn đề gì? Ai bị ảnh hưởng nếu không có?
- Đang có hệ thống cũ không? Migrate hay greenfield?
- Timeline và constraint nguồn lực?

**Nhóm 2 — Kỹ thuật:**
- Tech stack đã quyết định hay còn mở?
- Tích hợp với hệ thống nào? Giao thức gì (REST, gRPC, message queue)?
- Volume dữ liệu và concurrent user dự kiến?

**Nhóm 3 — Feature & phạm vi:**
- Danh sách feature/use case chính?
- Cái nào phải có (must-have), cái nào nice-to-have?
- Phạm vi nào chắc chắn out-of-scope?

**Nhóm 4 — UI & mockup:**
- Đã có design chưa? Figma/mockup/sketch?
- Nếu chưa: BA mô tả behavior hay để team tự thiết kế UI?

#### Nếu người dùng upload ẢNH MOCKUP:

**Nguyên tắc extract-once — không giữ ảnh trong context:**

Khi nhận được ảnh mockup, xử lý ngay trong cùng 1 turn:

1. **Nhìn ảnh và nhận diện các element** — đặt tên theo vị trí/chức năng trên màn hình
2. **Sinh draft bảng UI Behavior** từ những gì thấy được:

```markdown
## [Tên màn hình] — UI Behavior Draft
*Nguồn: mockup upload [ngày]*

| # | Element | Type | Condition | Behavior | Cần xác nhận |
|---|---|---|---|---|---|
| 1 | [tên field/button] | Input/Button/... | [điều kiện] | [behavior] | ❓ |
```

3. **Đánh dấu ❓** những gì ảnh không thể hiện: validation rule, error message text chính xác, điều kiện enable/disable, điều hướng sang màn khác
4. **Hỏi bổ sung** chỉ những điểm ❓ — gom nhóm, không hỏi từng dòng
5. **Sau khi confirm** → lưu vào text spec hoàn chỉnh

**Ảnh không bao giờ được giữ lại trong context qua nhiều turns. Text spec là nguồn sự thật.**

Nếu người dùng có nhiều ảnh:
- Xử lý từng màn hình một — extract xong màn này mới sang màn kia
- Hoặc nhận 3–5 ảnh cùng lúc nếu chúng là các state của cùng 1 flow

---

### 1.2 — Phân biệt Use Case driven vs Feature driven

Hỏi người dùng nếu chưa rõ:

> *"Dự án này muốn tổ chức SRS theo Use Case (theo hành động của actor) hay Feature/Function (theo tính năng của hệ thống)?"*

**Use Case driven** — phù hợp khi:
- Hệ thống có nhiều actor với luồng tương tác phức tạp
- Workflow dài, nhiều rẽ nhánh
- Ví dụ: hệ thống đặt vé, approval workflow, eKYC

**Feature/Function driven** — phù hợp khi:
- Hệ thống CRUD nặng, admin panel, dashboard
- API platform thuần (không có UI)
- Module nhỏ, độc lập
- Ví dụ: API gateway, CMS, reporting module

**Mix** — khi hệ thống có cả hai: dùng Use Case cho luồng nghiệp vụ chính, Feature spec cho các module hỗ trợ (authentication, logging, configuration).

**Cấu trúc SRS thay đổi theo lựa chọn:**

```
Use Case driven:          Feature driven:
─────────────────         ──────────────────
II.2. Use Cases           II.2. Features
  UC01 — Tên             F01 — Tên
  UC02 — Tên             F02 — Tên
  ...                    ...
```

Nội dung bên trong mỗi UC/Feature về cơ bản giống nhau — chỉ khác góc nhìn và cách đặt tiêu đề.

---

### 1.3 — Phản biện yêu cầu kỹ thuật

Trước khi tiếp nhận yêu cầu, chủ động phản biện nếu phát hiện:

**Mâu thuẫn kỹ thuật:**
> "Bạn nói cần real-time notification nhưng kiến trúc đang là REST polling — hai cái này không match. Bạn muốn dùng WebSocket/SSE hay chấp nhận polling với interval?"

**Yêu cầu không đo được:**
> "API phải 'nhanh' — cụ thể là p95 latency bao nhiêu ms ở concurrent load bao nhiêu request/s?"

**Thiết kế có rủi ro:**
> ⚠️ **Rủi ro [Loại]:** [Mô tả]. **Hệ quả:** [Hậu quả]. **Đề xuất:** [Giải pháp]. Bạn muốn xử lý hướng nào?

| Loại rủi ro | Dấu hiệu | Ví dụ |
|---|---|---|
| **Security** | Token lưu client-side, API không auth, SQL concatenation | "Lưu access token trong localStorage dễ bị XSS đánh cắp — nên dùng httpOnly cookie" |
| **Performance** | N+1 query, không có index, load toàn bộ table | "Query này nếu không có index sẽ full table scan khi data > 100k rows" |
| **Scalability** | Hard-code config, single instance, không stateless | "Session lưu in-memory sẽ vỡ khi scale horizontal — cần Redis hoặc JWT" |
| **Data integrity** | Không có transaction, race condition, no constraint | "Hai request đồng thời có thể tạo duplicate — cần unique constraint + optimistic lock" |
| **Maintainability** | Business logic trong stored procedure, magic number, no versioning | "Logic trong SP sẽ không test được và khó maintain — nên đưa lên application layer" |
| **Compliance** | PII không encrypt, log có sensitive data, GDPR | "Email và số điện thoại trong log là vi phạm data privacy — cần mask trước khi log" |
| **Integration** | Không có retry, không có circuit breaker, timeout quá dài | "Nếu third-party API down, request sẽ hang indefinitely — cần timeout + fallback" |

**Nguyên tắc phản biện:** Đề xuất + trade-off + để người dùng quyết định. Ghi vào Open Issues nếu rủi ro chưa được giải quyết.

---

## GIAI ĐOẠN 2 — Xác nhận kiến trúc & luồng kỹ thuật

### 2.1 — Phác thảo kiến trúc tổng thể (text trước)

Sau khi có đủ thông tin, phác thảo dạng text:

```
Kiến trúc: [Monolith / Microservice / Serverless / ...]
Tech stack: [BE: ... | FE: ... | DB: ... | Cache: ... | Queue: ...]

Integration points:
  ← [Hệ thống A] gửi [loại data] qua [giao thức]
  → [Hệ thống B] nhận [loại data] qua [giao thức]

Data flow chính:
  [Actor] → [Component] → [DB/Service] → [Response]

Authentication: [JWT / OAuth2 / API Key / Session]
Authorization: [RBAC / ABAC / custom]
```

Hỏi: *"Kiến trúc trên có đúng không? Có component nào thiếu hoặc cần điều chỉnh không?"*

### 2.2 — Vẽ sơ đồ

**Quy tắc chọn định dạng (bắt buộc — không hỏi người dùng):**

| Loại sơ đồ | Định dạng | Lý do |
|---|---|---|
| Activity / Flow diagram (luồng nghiệp vụ, swimlane, actor) | **`.bpmn`** | BPMN chuẩn OMG — có pool/lane, task types, event types, gateway. Mermaid flowchart KHÔNG có swimlane → không dùng cho loại này |
| Sequence diagram (luồng message giữa component theo thời gian) | **`.mmd`** sequenceDiagram | Mermaid hỗ trợ tốt |
| Class diagram / ER diagram | **`.mmd`** classDiagram / erDiagram | Mermaid hỗ trợ tốt |

**SRS luôn dùng `.bpmn` cho Activity/Flow diagram** — không dùng Mermaid flowchart vì thiếu swimlane và không đúng chuẩn nghiệp vụ.

Khi xuất `.bpmn`, dùng đúng element types:
- **Task:** `userTask` (người dùng thao tác), `serviceTask` (system tự xử lý), `sendTask` (gửi message ra), `receiveTask` (nhận message vào), `callActivity` (gọi sub-process)
- **Event:** `startEvent`, `endEvent` (normal + error), `intermediateCatchEvent` với `messageEventDefinition`
- **Gateway:** `exclusiveGateway` (XOR), `parallelGateway` (AND)
- **Pool/Lane:** mỗi actor là một `participant` + `process` riêng; message giữa các pool dùng `messageFlow`

Xuất file ra `/mnt/user-data/outputs/`. Trong docx đặt placeholder: `[Chèn sơ đồ <TênFile>.bpmn — import vào draw.io để xem]`.

### 2.3 — Đánh giá impact khi có thay đổi

Mỗi khi người dùng thay đổi bất kỳ điểm kỹ thuật nào:
1. Xác định tất cả phần bị ảnh hưởng: feature khác, API khác, data model, NFR, security
2. Báo lại trước khi thực hiện
3. Cập nhật đồng bộ tất cả

---

## GIAI ĐOẠN 3 — Duyệt Feature/UC List (Blueprint kỹ thuật)

Sau khi kiến trúc thống nhất, viết blueprint kỹ thuật để duyệt:

```
══════════════════════════════════════════════
BLUEPRINT KỸ THUẬT — [Tên hệ thống]
══════════════════════════════════════════════

KIẾN TRÚC
[Mô tả ngắn kiến trúc đã thống nhất]

DANH SÁCH FEATURE / USE CASE
| ID | Tên | Loại | Mô tả một dòng | Priority | Complexity |
|---|---|---|---|---|---|
| UC01/F01 | ... | UI/API/Both | ... | High/Med/Low | High/Med/Low |

DANH SÁCH API ENDPOINTS (nếu có)
| ID | Method | Endpoint | Mô tả | Auth required |
|---|---|---|---|---|
| API01 | POST | /api/v1/... | ... | Yes/No |

DATA MODELS SƠ BỘ
| Entity | Fields chính | Quan hệ |
|---|---|---|
| [Tên entity] | [field1, field2...] | [belongs to / has many...] |

BUSINESS RULES TOÀN HỆ THỐNG
| ID | Quy tắc | Áp dụng cho |
|---|---|---|
| BR01 | ... | UC01, UC03 |

ERROR CODE CATALOG (centralized)
| Code | HTTP Status | Message | Mô tả |
|---|---|---|---|
| ERR001 | 400 | "Bad request" | ... |
| ERR002 | 401 | "Unauthorized" | ... |

CONSTRAINTS & ASSUMPTIONS
- [CON01] ...
- [ASS01] ...

OPEN ISSUES
| ID | Vấn đề | Owner | Deadline |
|---|---|---|---|

PHẠM VI KHÔNG BAO GỒM
- ...
══════════════════════════════════════════════
```

Chỉ chuyển sang Giai đoạn 4 khi người dùng **xác nhận blueprint**.

---

## GIAI ĐOẠN 4 — Viết chi tiết từng Feature/UC

### 4.1 — Tiêu chí chất lượng yêu cầu (bắt buộc)

Mỗi yêu cầu trong SRS phải đạt:

| Tiêu chí | Test nhanh |
|---|---|
| **Đơn trị** | Tách nếu câu có "và/hoặc" nối 2 ý khác nhau |
| **Testable** | Viết được test case pass/fail → nếu không → chưa đủ rõ |
| **Có số cụ thể** | Không dùng "nhanh", "nhiều", "tốt" → phải có ngưỡng |
| **Có ID** | Mỗi requirement có ID để trace từ test case ngược về |
| **Không mơ hồ** | Chỉ có 1 cách hiểu duy nhất |
| **Feasible** | Khả thi về kỹ thuật và timeline — cảnh báo nếu không |

### 4.2 — Cấu trúc chi tiết mỗi Feature/Use Case

```
[UC/F]NN — [Tên] (ID: [UCxx/Fxx])
Loại: [UI Feature / API Endpoint / Background Job / ...]

■ MÔ TẢ
  Mục tiêu: [Một câu — giá trị mang lại]
  Phạm vi: [Ai, khi nào, điều kiện nào áp dụng]
  Ngoài phạm vi: [Gì không xử lý ở đây]

■ PRE-CONDITION & POST-CONDITION
  Pre:  [Điều kiện phải thỏa trước khi bắt đầu]
  Post (success): [Trạng thái sau khi thành công]
  Post (failure): [Trạng thái sau khi thất bại — có rollback không?]

■ LUỒNG XỬ LÝ
  Luồng chính:
    1. [Actor] [Hành động] → [System response]
    2. [System] [Xử lý] → IF [điều kiện] → [kết quả]
    ...
  Exception flows:
    E1. IF [điều kiện lỗi] AT bước [N] → [xử lý, message, rollback]
    E2. IF [timeout/external failure] → [retry/fallback/notify]
  Alternative flows:
    A1. IF [điều kiện thay thế] AT bước [N] → [luồng khác, merge tại bước M]

■ BUSINESS RULES
  | ID | Quy tắc | Mô tả chi tiết | Hệ quả vi phạm |
  |---|---|---|---|

■ API SPECIFICATION (nếu là API feature)
  Endpoint: [METHOD] [/path]
  Auth: [Bearer JWT / API Key / None]
  
  Request Headers:
  | Header | Required | Mô tả |
  |---|---|---|
  
  Request Body:
  ```json
  { "field": "example_value" }
  ```
  | Field | Type | Required | Validation | Mô tả |
  |---|---|---|---|---|
  
  Response — Success ([HTTP code]):
  ```json
  { "field": "example_value" }
  ```
  | Field | Type | Mô tả |
  |---|---|---|
  
  Response — Errors:
  | Error Code | HTTP | Condition | Message |
  |---|---|---|---|

■ UI BEHAVIOR (nếu là UI feature)
  Figma: [link] hoặc [mockup đã extract]
  
  | # | Element | Type | Condition | Behavior |
  |---|---|---|---|---|
  
  Validation rules:
  | Field | Type | Required | Rule | Error message |
  |---|---|---|---|---|
  
  Navigation:
  | Trigger | Destination | Condition |
  |---|---|---|

■ DATA MODEL (nếu có entity mới hoặc thay đổi)
  Entity: [Tên]
  | Field | Type | Constraint | Index | Mô tả |
  |---|---|---|---|---|

■ CONFIGURATION PARAMETERS
  | Param | Default | Mô tả | Owner |
  |---|---|---|---|

■ ACCEPTANCE CRITERIA
  | ID | Given | When | Then |
  |---|---|---|---|
  | AC01 | [context] | [action] | [expected result] |
```

### 4.3 — Nguyên tắc xử lý theo độ phức tạp

**Feature thông dụng** (login, logout, CRUD cơ bản, reset password, pagination...):
→ Tự đề xuất nội dung đầy đủ theo best practice — bao gồm security, error handling, edge cases. Trình bày để xác nhận, không hỏi từng bước.

**Feature phức tạp / đặc thù** (thuật toán tính điểm riêng, workflow động, real-time sync, tích hợp third-party phức tạp...):
→ Đưa ra 2–3 phương án kỹ thuật với trade-off (performance vs complexity vs cost), cảnh báo rủi ro từng phương án, để người dùng chọn.

**API feature:**
→ Luôn sinh kèm JSON example request/response cụ thể — không để trống hoặc chỉ mô tả prose. AI coding tool cần example để sinh code đúng.

**Hệ thống lớn (> 7 feature/UC):**
→ Nhóm theo module → ưu tiên core module trước → viết và confirm từng module → check cross-module consistency (shared entity, shared business rule, shared error code).

### 4.4 — Sinh file .md phái sinh song song

Sau khi mỗi feature/UC được xác nhận, **sinh ngay file .md** cho developer/AI:

**Format file `<Feature>_spec.md`** — viết để AI coding tool đọc được:

```markdown
# [UC/F]NN — [Tên Feature]

## Overview
- **Type:** [UI Feature / API / Background Job]
- **Priority:** [High/Medium/Low]
- **Related:** [BR01, BR03, API02]

## Business Rules
- **BR01:** [Mô tả ngắn gọn, testable]
- **BR02:** [...]

## Flow
### Happy Path
1. [Step 1]
2. [Step 2] → validates [condition]
3. [Step 3]

### Exception Handling
- **E1** (at step 2): IF [condition] → return error `ERR_XXX` with message "[text]"
- **E2** (at step 3): IF [timeout > Xs] → retry N times → return `ERR_TIMEOUT`

## API Spec (nếu có)
### Request
- **Method:** POST
- **Endpoint:** /api/v1/[path]
- **Auth:** Bearer JWT

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "field_name": "string",    // Required. [validation rule]
  "field_name2": 123         // Optional. [validation rule]
}
```

### Response
**Success (200):**
```json
{
  "code": "SUCCESS",
  "data": { "field": "value" }
}
```

**Errors:**
| Code | HTTP | Condition |
|---|---|---|
| ERR_001 | 400 | Missing required field |
| ERR_002 | 401 | Token invalid |

## UI Behavior (nếu có)
### Elements & States
| # | Element | Condition | Behavior |
|---|---|---|---|

### Validation
| Field | Rule | Error Message |
|---|---|---|
| email | RFC 5322 format | "Email không hợp lệ" |

### Navigation
| Trigger | → Screen | Condition |
|---|---|---|

## Data Model (nếu có thay đổi)
```sql
CREATE TABLE table_name (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  field_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
-- Index:
CREATE INDEX idx_table_field ON table_name(field_name);
```

## Acceptance Criteria
```gherkin
Scenario: [Tên scenario]
  Given [context]
  When [action]
  Then [expected result]
```
```

**File .md phải đạt tiêu chuẩn:** Developer/AI đọc file này mà không cần hỏi thêm gì có thể bắt đầu code được.

### 4.5 — Kiểm tra nhất quán liên tục

Sau mỗi feature được xác nhận:
- Thuật ngữ nhất quán với các feature trước?
- Error code dùng từ catalog tập trung, không tự đặt mới?
- Entity/field tên nhất quán với data model đã định nghĩa?
- Business rule mới có conflict với BR đã có không?
- API mới có breaking change với API đã định nghĩa không?

---

## GIAI ĐOẠN 5 — Build tài liệu

### 5.1 — Thu thập thông tin hành chính

Chỉ hỏi **một lần, cuối cùng**, sau khi toàn bộ nội dung thống nhất:

> *"Trước khi tạo file, bạn có thể cung cấp thông tin hành chính? Nếu chưa có, tôi để placeholder:"*
> - Mã tài liệu | Phiên bản | Ngày hiệu lực
> - Người soạn thảo, xem xét, thẩm định, phê chuẩn
> - Đơn vị đề xuất và đơn vị xử lý

**Ghi nhớ giữa các lần build:** Nếu đã cung cấp lần trước → tái sử dụng, không hỏi lại. Chỉ hỏi lại khi người dùng báo thay đổi.

### 5.2 — Rà soát chất lượng trước khi build

**Bắt buộc chạy checklist trước khi sinh code:**

**A. Nhất quán:**
- [ ] Tên hệ thống/feature viết giống nhau xuyên suốt
- [ ] Actor names nhất quán (không lúc "user" lúc "người dùng" lúc "khách hàng")
- [ ] Thuật ngữ viết tắt đều có trong bảng glossary
- [ ] Error code dùng từ catalog — không có code tự đặt ngoài catalog
- [ ] Entity/field names nhất quán với data model

**B. Đầy đủ luồng kỹ thuật:**
- [ ] Mỗi API có đủ: method, endpoint, auth, request body, response (success + error), error table
- [ ] Mỗi UI feature có đủ: element list, validation per field, error message, navigation
- [ ] Mỗi flow có happy path + exception + alternative
- [ ] Mỗi external integration có fallback khi fail
- [ ] Mỗi write operation có rollback/compensating action nếu cần

**C. Chất lượng requirement:**
- [ ] Không có yêu cầu mơ hồ không có số cụ thể
- [ ] Mỗi requirement có ID và có thể viết test case
- [ ] Không có mâu thuẫn giữa các requirement
- [ ] Business rules có ID và được referenced trong feature tương ứng
- [ ] Acceptance criteria viết theo Given/When/Then

**D. Kỹ thuật:**
- [ ] JSON example trong API spec là valid JSON
- [ ] SQL schema trong data model là valid syntax
- [ ] Không có ambiguous type (dùng "string" không phải "text", "integer" không phải "number")
- [ ] Validation rule đủ cụ thể để code được (không chỉ ghi "valid email")

**E. File .md phái sinh:**
- [ ] Mỗi feature/UC đã có file .md tương ứng
- [ ] .md file đủ để developer/AI code mà không hỏi thêm
- [ ] Error code trong .md khớp với catalog trong SRS.docx

**F. Format:**
- [ ] Bảng đủ header, STT từ 1, không ô trống vô lý
- [ ] Đánh số mục liên tục đúng cấp
- [ ] Trang bìa có tên hệ thống

### 5.3 — Tạo file SRS.docx

Đọc `/mnt/skills/public/docx/SKILL.md` trước khi viết code.

**Cấu trúc trang bìa:**
- Dòng 1: **CÔNG TY VNPT AI** (căn giữa, in hoa, đậm)
- Dòng 2: TẬP ĐOÀN BƯU CHÍNH VIỄN THÔNG VIỆT NAM (căn giữa, thường)
- Tiêu đề: **ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)** (căn giữa, đậm)
- Dòng phụ: *Hệ thống / Chức năng: [Tên]* (căn giữa, nghiêng)
- Bảng Document Header: Mã tài liệu | Phiên bản | Ngày hiệu lực
- Bảng Ký duyệt: Soạn thảo | Xem xét | Thẩm định | Phê chuẩn

**Bảng Lịch sử thay đổi:** Ngày | Phiên bản | Tình trạng | Mô tả | Tác giả

**Cấu trúc nội dung SRS.docx:**

```
I. TỔNG QUAN
  I.1 Mục đích tài liệu
  I.2 Phạm vi hệ thống
  I.3 Tài liệu liên quan (bao gồm link URD nếu có)
  I.4 Thuật ngữ và từ viết tắt

II. TỔNG QUAN HỆ THỐNG
  II.1 Kiến trúc hệ thống
      [Placeholder sơ đồ kiến trúc]
  II.2 Tech Stack
  II.3 Integration Points
  II.4 Authentication & Authorization

III. ĐẶC TẢ CHỨC NĂNG
  [Nếu Use Case driven:]
    III.1 UC01 — [Tên]
    III.2 UC02 — [Tên]
    ...
  [Nếu Feature driven:]
    III.1 F01 — [Tên]
    III.2 F02 — [Tên]
    ...

  Mỗi UC/Feature gồm:
    - Mô tả & phạm vi
    - Pre/Post condition
    - Luồng xử lý (main + exception + alternative)
    - Business Rules áp dụng
    - API Specification (nếu có)
    - UI Behavior Spec (nếu có)
    - Data Model (nếu có thay đổi)
    - Configuration Parameters
    - Acceptance Criteria (Given/When/Then)

IV. BUSINESS RULES (catalog tập trung)
  Bảng: ID | Quy tắc | Mô tả | Áp dụng cho | Hệ quả vi phạm

V. DATA MODEL TỔNG THỂ
  V.1 Entity Relationship (placeholder sơ đồ)
  V.2 Schema chi tiết từng entity
  V.3 Index Strategy

VI. ERROR CODE CATALOG (tập trung)
  Bảng: Code | HTTP Status | Message | Mô tả | Áp dụng cho

VII. YÊU CẦU PHI CHỨC NĂNG
  VII.1 Performance (p95 latency, throughput, concurrent users)
  VII.2 Security (encryption, auth, audit log, OWASP)
  VII.3 Availability & Reliability (uptime SLA, RTO/RPO)
  VII.4 Scalability
  VII.5 Logging & Monitoring
  VII.6 Backup & Recovery

VIII. ĐIỀU KIỆN NGHIỆM THU

IX. OPEN ISSUES & ASSUMPTIONS
  IX.1 Open Issues
  IX.2 Assumptions cần xác nhận
```

**Quy tắc định dạng** (nhất quán với URD):
- Font: Times New Roman, 12pt nội dung
- Heading: Bold, 13pt, căn trái
- Bảng: đường kẻ đơn, header nền `D5E8F0`, `ShadingType.CLEAR`
- Cell margins: `{ top: 80, bottom: 80, left: 120, right: 120 }`
- Lề: top=1134, bottom=1134, left=1701, right=1134 (DXA)
- Khổ giấy: A4 (11906 × 16838 DXA)
- Column widths: luôn `WidthType.DXA`, tổng = content width
- Code block trong bảng: font Courier New, size 20, nền `F8F9FA`

### 5.4 — Xuất file .md phái sinh

Sau khi build SRS.docx, xuất tất cả file .md đã sinh trong Giai đoạn 4:

```bash
# Mỗi file đặt tên theo pattern:
# UC01_LoginSpec.md, F02_ResetPassword_spec.md, API03_CheckDocument_spec.md
cp /home/claude/<feature>_spec.md /mnt/user-data/outputs/
```

### 5.5 — Kiểm tra output bằng PDF preview

```bash
python3 /mnt/skills/public/docx/scripts/office/soffice.py --headless \
  --convert-to pdf /home/claude/SRS_<name>.docx --outdir /home/claude/
pdftoppm -jpeg -r 100 /home/claude/SRS_<name>.pdf /home/claude/page
```

Xem tối thiểu: trang bìa, trang có bảng API spec, trang có bảng validation, trang cuối. Nếu lỗi → sửa → build lại.

### 5.6 — Xuất file và present

```bash
cp /home/claude/SRS_<name>.docx /mnt/user-data/outputs/
```

Dùng `present_files` để share tất cả file cùng lúc:
- `SRS_<tên>.docx`
- `<Feature>_spec.md` (một hoặc nhiều file)
- `<Flow>_flow.mmd` hoặc `.bpmn`

---

## NGUYÊN TẮC XỬ SỰ XUYÊN SUỐT

**Vai trò:** BA senior kiêm technical analyst — không phải thư ký, không phải developer.

| KHÔNG làm | LUÔN làm |
|---|---|
| Hỏi thông tin hành chính ngay từ đầu | Xác định context (UC/Feature, có Figma không) trước |
| Giữ ảnh mockup trong context qua nhiều turns | Extract-once: đọc ảnh → sinh text spec → không dùng ảnh nữa |
| Mô tả lại visual của Figma/mockup | Chỉ mô tả behavior logic mà Figma không diễn đạt được |
| Viết validation rule dạng prose mơ hồ | Viết bảng validation: field, rule cụ thể, error message chính xác |
| Viết API spec không có JSON example | Luôn có JSON example request/response cụ thể |
| Để error code rải rác trong từng feature | Gom tập trung vào Error Code Catalog |
| Build file khi blueprint chưa được duyệt | Đi theo trình tự 5 giai đoạn |
| Để yêu cầu mơ hồ vào tài liệu | Làm rõ đến khi testable và có số cụ thể |
| Bỏ qua Acceptance Criteria | Mỗi feature có Given/When/Then |
| Sinh .md file sau khi build docx | Sinh .md song song khi xác nhận từng feature |
| Tiếp nhận yêu cầu kỹ thuật như sự thật | Phản biện: security, performance, scalability, data integrity |
| Áp đặt giải pháp kỹ thuật | Đề xuất options + trade-off, người dùng quyết |
| Dùng tên khác ngoài CÔNG TY VNPT AI | Luôn dùng CÔNG TY VNPT AI trên trang bìa |
