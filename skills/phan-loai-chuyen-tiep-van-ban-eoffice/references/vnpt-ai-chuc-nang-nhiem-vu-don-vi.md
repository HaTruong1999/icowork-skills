---
title: Cơ cấu tổ chức, chức năng, nhiệm vụ các đơn vị trực thuộc Công ty VNPT AI
purpose: Tài liệu kiến thức cho iWork phân loại vai trò (Xử lý chính / Phối hợp / Xem để biết) và chuyển tiếp văn bản eOffice tới đúng đơn vị, đúng người
source: 7 Quyết định thành lập đơn vị trực thuộc (tháng 01/2026), thư mục docs/00-icowork/13-data-hub
version: 0.2 (đã điền lãnh đạo theo danh sách nhân sự ngày 20/10/2026)
updated: 2026-10-20
---

# Cơ cấu tổ chức & chức năng nhiệm vụ đơn vị — Công ty VNPT AI

> **Dành cho iWork.** Đọc mục 1 (cách dùng) và mục 4 (ma trận phân loại) trước. Mục 5 là căn cứ chi tiết để trích dẫn. Mục 3 và các bảng "Lãnh đạo đơn vị" chứa thông tin người nhận — ô ghi `[cần bổ sung]` hoặc `[vd: …]` nghĩa là chưa có dữ liệu.

## 1. Cách iWork dùng tài liệu này

### 1.1. Quy trình phân loại một văn bản đến

1. **Đọc văn bản**: số/ký hiệu, cơ quan ban hành, trích yếu, nội dung yêu cầu, thời hạn, mục "Nơi nhận", đơn vị/người được giao đích danh, lịch sử xử lý.
2. **Ưu tiên chỉ định có sẵn**: văn bản, bút phê lãnh đạo hoặc lịch sử xử lý đã giao đích danh đơn vị/người → giữ nguyên, chỉ bổ sung đơn vị Phối hợp nếu thấy cần.
3. **Xác định lĩnh vực**: so khớp nội dung với cột "Từ khóa nhận diện" ở mục 4. Một văn bản có thể gồm nhiều việc, thuộc nhiều lĩnh vực.
4. **Gán vai trò** theo mục 2: mỗi lượt chuyển chỉ đề xuất **một** đơn vị Xử lý chính cho cả văn bản. Văn bản nhiều việc thì Xử lý chính là đơn vị làm đầu mối tổng hợp, trả lời nơi gửi; nếu mục 6 có quy tắc khớp (vd "Dự án khách hàng") thì theo quy tắc đó; nếu không, chọn đơn vị phụ trách việc nêu đầu tiên trong trích yếu, trừ khi việc khác chiếm phần lớn nội dung; đơn vị phụ trách các việc còn lại là Phối hợp, ghi rõ phần việc của từng đơn vị ở cột "Nội dung cần làm". Đơn vị chỉ cần nắm thông tin là Xem để biết.
5. **Phân xử chồng lấn**: nếu khớp nhiều đơn vị cho cùng một việc → áp quy tắc ở mục 6.
6. **Chọn người nhận** (mục 3 và bảng lãnh đạo ở mục 5). Ô `[cần bổ sung]` và ô bắt đầu bằng `[vd: …]` đều là **chưa có dữ liệu**.
   - Chuyển **cấp Công ty → đơn vị**: người nhận là Thủ trưởng đơn vị; nếu biết cấp phó phụ trách lĩnh vực khớp thì ghi thêm làm gợi ý.
   - Chuyển **trong đơn vị**: người nhận là cấp phó/người được phân công lĩnh vực khớp. Chưa có dữ liệu phân công → ghi chức danh kèm lĩnh vực (vd "Phó Giám đốc phụ trách ATTT") để người dùng tự chọn người; không đề xuất chuyển ngược lại cho chính Thủ trưởng.
   - Đơn vị chưa có Thủ trưởng nhưng có cấp phó ghi chú "Phụ trách đơn vị" → coi người đó là Thủ trưởng.
   - Chưa có dữ liệu họ tên → ghi chức danh và "chưa có dữ liệu người nhận". Không bịa họ tên, email, tài khoản.
7. **Trả kết quả** theo mẫu ở mục 8, kèm mã căn cứ (vd `QTNS.9.8`) và mức độ tin cậy.

### 1.2. Nguyên tắc

- Chỉ dựa trên chức năng, nhiệm vụ trong tài liệu này; **không suy đoán** nhiệm vụ không có căn cứ. Mã căn cứ chỉ khớp gần đúng thì ghi "(gần nhất)".
- Hai cách dùng "Trình lãnh đạo":
  - **Không xác định được** Xử lý chính → dùng vai trò "Trình lãnh đạo" thay cho dòng Xử lý chính, độ tin cậy Thấp, nêu 2 phương án khả dĩ nhất.
  - **Đã xác định được** Xử lý chính nhưng văn bản cần quyết định ở cấp Công ty (phê duyệt chủ trương, ký ban hành, nội dung gửi Tập đoàn cần lãnh đạo duyệt) → vẫn đề xuất Xử lý chính, ghi thêm "Cần trình Lãnh đạo Công ty: …" ở phần Lưu ý.
- iWork **đề xuất**, người dùng xác nhận trước khi chuyển tiếp trên eOffice.

## 2. Định nghĩa vai trò xử lý văn bản

Tên vai trò dùng đúng tên nhóm trên eOffice.

| Vai trò (eOffice) | Mã JSON | Ý nghĩa | Quy tắc gán |
|---|---|---|---|
| **Xử lý chính** | `xu_ly_chinh` | Đơn vị chịu trách nhiệm chính (chủ trì), tổ chức thực hiện, tổng hợp và trả lời/báo cáo kết quả | Đơn vị có nhiệm vụ khớp trực tiếp nhất với việc chính. Mỗi lượt chuyển chỉ một đơn vị |
| **Phối hợp** | `phoi_hop` | Tham gia, thực hiện phần việc của mình, cung cấp thông tin/nguồn lực cho đơn vị Xử lý chính | Đơn vị có nhiệm vụ liên quan một phần, phụ trách một việc phụ, hoặc là chủ quản của đối tượng được nhắc tới |
| **Xem để biết** | `xem_de_biet` | Nhận để nắm thông tin, không phải xử lý | Văn bản thông báo chung, hoặc đơn vị bị ảnh hưởng gián tiếp |
| **Trình lãnh đạo** | `trinh_lanh_dao` | Cần Lãnh đạo Công ty cho ý kiến/phân công trước | Chỉ dùng khi không xác định được Xử lý chính (xem 1.2) |

> Các vai trò trên là quy ước vận hành đề xuất cho iWork, không nằm trong các Quyết định thành lập.

## 3. Tổng quan tổ chức

### 3.1. Công ty

- **Tên**: Công ty VNPT AI – Chi nhánh Tập đoàn Bưu chính Viễn thông Việt Nam (VNPT).
- **Căn cứ pháp lý**:
  - QĐ số 268/QĐ-VNPT-HĐTV-NL ngày 10/12/2025 — thành lập Công ty VNPT AI.
  - QĐ số 314/QĐ-VNPT-HĐTV-NL ngày 31/12/2025 — Quy chế tổ chức và hoạt động.
  - QĐ số 2963/QĐ-VNPT-NL ngày 16/12/2025 — mô hình tổ chức.
- **Người ký các QĐ thành lập đơn vị**: Q. Tổng Giám đốc Nguyễn Tiến Cường (tháng 01/2026, đơn vị soạn thảo: Ban Quản trị và Nhân sự).

### 3.2. Ban Lãnh đạo Công ty

| Chức danh | Họ và tên | Khối/lĩnh vực phụ trách | Đơn vị phụ trách | Email | Tài khoản eOffice |
|---|---|---|---|---|---|
| Quyền Tổng Giám đốc | Nguyễn Tiến Cường | Toàn bộ Công ty | Tất cả đơn vị | nguyentiencuong@vnpt.vn | nguyentiencuong@vnpt.vn |
| Phó Tổng Giám đốc | Phạm Thanh Tú | [cần bổ sung] | [cần bổ sung] | tupt@vnpt.vn | tupt@vnpt.vn |
| Giám đốc Khoa học (Hội đồng tư vấn) | Vũ Đình Quyền | Hội đồng tư vấn — chức năng chưa có trong các Quyết định thành lập, không chọn làm Xử lý chính | — | vudinhquyen@vnpt.vn | vudinhquyen@vnpt.vn |

### 3.3. Danh sách đơn vị trực thuộc

| Mã | Tên đơn vị | Tên gọi khác / viết tắt | Loại | Thủ trưởng | Cấp phó |
|---|---|---|---|---|---|
| QTNS | Ban Quản trị và Nhân sự | Ban QT&NS, Ban QTNS | Ban chức năng (tham mưu) | Trưởng Ban | Phó Trưởng Ban |
| CLSHTT | Ban Chiến lược và Sở hữu trí tuệ | Ban CL&SHTT | Ban chức năng (chuyên môn) | Trưởng Ban | Phó Trưởng Ban |
| KDTV | Ban Kinh doanh và Tư vấn Công nghệ cao | Ban KD&TV CNC, Ban Kinh doanh | Ban chức năng (chuyên môn) | Giám đốc Ban | Phó Giám đốc Ban |
| NCPT | Trung tâm Nghiên cứu và Phát triển công nghệ AI | TT NC&PT, Trung tâm R&D | Trung tâm (sản xuất) | Giám đốc Trung tâm | Phó Giám đốc |
| NTAI | Trung tâm Nền tảng AI | TT Nền tảng, AI Platform | Trung tâm (sản xuất) | Giám đốc Trung tâm | Phó Giám đốc |
| PTDL | Trung tâm Phân tích dữ liệu và Ứng dụng AI đa ngành | TT PTDL, Trung tâm Dữ liệu & Ứng dụng | Trung tâm (sản xuất) | Giám đốc Trung tâm | Phó Giám đốc |
| SPTN | Trung tâm Sản phẩm & Trải nghiệm xuất sắc | TT SP&TN, Trung tâm Sản phẩm | Trung tâm (sản xuất) | Giám đốc Trung tâm | Phó Giám đốc |

**Tóm tắt một dòng mỗi đơn vị** (dùng để định hướng nhanh):

- **QTNS** — "hậu phương" của Công ty: tổ chức, nhân sự, lương thưởng, Đảng, Công đoàn, pháp chế, thanh tra, kế hoạch – đầu tư, tài chính – kế toán, hành chính, văn thư, bảo vệ, y tế.
- **CLSHTT** — chiến lược & danh mục sản phẩm, quy trình GTM, chất lượng sản phẩm, sở hữu trí tuệ, công bố khoa học, hợp tác chiến lược, cơ chế kinh tế nội bộ.
- **KDTV** — bán hàng, tư vấn giải pháp, dự án trọng điểm, chính sách giá, thương hiệu – marketing – truyền thông bên ngoài, CSKH/CRM, đấu thầu phục vụ SXKD.
- **NCPT** — nghiên cứu công nghệ lõi và mô hình AI (NLP, Voice, CV, GenAI, mô hình tiếng Việt), bài báo khoa học, sáng chế, chuyển giao mô hình.
- **NTAI** — hạ tầng & nền tảng AI dùng chung (GPU, cloud, data lake, MLOps, API gateway), DevSecOps, triển khai đa hạ tầng, an toàn thông tin, chủ quyền công nghệ.
- **PTDL** — phân tích dữ liệu, giải pháp AI theo ngành, triển khai/tích hợp dự án AI end-to-end cho khách hàng, chuyển giao công nghệ cho khách hàng.
- **SPTN** — quản lý sản phẩm (roadmap, tính năng), UX/UI & design system, xử lý sự cố sản phẩm, hỗ trợ GTM và tài liệu sản phẩm.

## 4. Ma trận phân loại nhanh (lĩnh vực → vai trò)

> Cột "Phối hợp thường gặp" là gợi ý; chỉ gán khi nội dung văn bản thực sự liên quan.

### 4.1. Tổ chức – nhân sự – Đảng – đoàn thể

| # | Lĩnh vực | Từ khóa nhận diện | Xử lý chính | Phối hợp thường gặp | Căn cứ |
|---|---|---|---|---|---|
| 1 | Mô hình tổ chức, quy chế tổ chức hoạt động, chức năng nhiệm vụ | thành lập, sáp nhập, giải thể, kiện toàn, mô hình tổ chức, quy chế tổ chức và hoạt động | QTNS | Đơn vị bị điều chỉnh | QTNS.1.1 |
| 2 | Định mức, định biên, chức danh, mô tả công việc, điều chuyển | định biên, vị trí việc làm, JD, thư viện công việc, điều động, luân chuyển | QTNS | Đơn vị có nhân sự | QTNS.1.2–1.3 |
| 3 | Tuyển dụng, thu hút nhân tài, hội nhập | tuyển dụng, headhunt, nhân tài AI, onboarding | QTNS | Đơn vị có nhu cầu | QTNS.2.1–2.3 |
| 4 | Đào tạo nội bộ, khung năng lực, đánh giá năng lực | đào tạo, bồi dưỡng, khảo sát nhu cầu đào tạo, khung năng lực | QTNS | NCPT (nếu là nhân lực nghiên cứu AI) | QTNS.2.4–2.6; NCPT.4.3 |
| 5 | Công tác nước ngoài | đoàn ra, cử đi nước ngoài, hộ chiếu công vụ | QTNS | Đơn vị cử người | QTNS.2.7 |
| 6 | Tiền lương, thưởng, KPI, đánh giá hiệu suất | lương, thưởng, KPI, BSC, đánh giá kết quả công việc | QTNS | Các đơn vị | QTNS.3.1–3.2 |
| 7 | BHXH, BHYT, nghỉ phép, ốm đau, thai sản, phúc lợi | bảo hiểm xã hội, chế độ, nghỉ phép, quỹ phúc lợi | QTNS | — | QTNS.3.3–3.6 |
| 8 | An toàn vệ sinh lao động, y tế, PCCC, bảo vệ cơ quan | ATVSLĐ, khám sức khỏe, PCCC, an ninh trụ sở, ra vào cơ quan | QTNS | — | QTNS.3.7; QTNS.12 |
| 9 | Thi đua – khen thưởng – kỷ luật | thi đua, khen thưởng, danh hiệu, bằng khen, kỷ luật | QTNS | CLSHTT (nếu khen thưởng sáng kiến/sáng chế) | QTNS.4; CLSHTT.7.1 |
| 10 | Công tác Đảng, kiểm tra giám sát Đảng | Đảng ủy, chi bộ, đảng viên, kết nạp, nghị quyết, UBKT | QTNS | — | QTNS.6 |
| 11 | Công đoàn, Hội nghị người lao động, nghỉ mát | công đoàn, thỏa ước lao động tập thể, hội nghị người lao động, tham quan nghỉ mát | QTNS | — | QTNS.5.8–5.9 |
| 12 | Phòng chống tham nhũng, thực hành tiết kiệm | tham nhũng, buôn lậu, tiết kiệm, chống lãng phí | QTNS | — | QTNS.5.7 |
| 13 | Truyền thông nội bộ, văn hóa doanh nghiệp | truyền thông nội bộ, bản tin nội bộ, văn hóa doanh nghiệp | QTNS | — | QTNS.1.4–1.5 |

### 4.2. Tổng hợp – pháp chế – kế hoạch – tài chính – hành chính

| # | Lĩnh vực | Từ khóa nhận diện | Xử lý chính | Phối hợp thường gặp | Căn cứ |
|---|---|---|---|---|---|
| 14 | Báo cáo tổng hợp, lịch công tác, theo dõi kết luận lãnh đạo, cải cách hành chính | báo cáo định kỳ toàn Công ty, giao ban, lịch công tác, kết luận chỉ đạo | QTNS | Các đơn vị (cung cấp số liệu) | QTNS.7.1–7.3 |
| 15 | Pháp chế: rà soát văn bản pháp luật, quy chế nội bộ, thẩm định hợp đồng/MOU | luật, nghị định, thông tư, góp ý dự thảo, thẩm định pháp lý, hợp đồng, biên bản ghi nhớ | QTNS | Đơn vị chủ quản hợp đồng | QTNS.7.4–7.6 |
| 16 | Thanh tra, khiếu nại, tố cáo, tiếp dân | thanh tra, kiểm tra, khiếu nại, tố cáo | QTNS | Đơn vị bị thanh tra/liên quan | QTNS.7.7 |
| 17 | Kế hoạch SXKD, đầu tư, dự án đầu tư, quyết toán | kế hoạch SXKD, giao chỉ tiêu, đầu tư, chủ đầu tư, quyết toán dự án | QTNS | Các đơn vị | QTNS.8.1–8.3 |
| 18 | Mua sắm thường xuyên, tài sản, kiểm kê, thanh lý | mua sắm, VPP, công cụ dụng cụ, tài sản cố định, kiểm kê, thanh lý | QTNS | Đơn vị đề xuất | QTNS.8.4–8.6; QTNS.10.1, 10.3 |
| 19 | Đấu thầu mua sắm phục vụ SXKD | đấu thầu, hồ sơ mời thầu, lựa chọn nhà thầu (cho dự án/kinh doanh) | KDTV | QTNS (thủ tục tài chính, pháp chế) | KDTV.1.5 |
| 20 | Tài chính, kế toán, thuế, hóa đơn, công nợ, dòng tiền | thuế, hóa đơn, chứng từ, công nợ, thu hồi nợ, thanh toán, báo cáo tài chính, ngân sách, đối soát thanh khoản | QTNS | Đơn vị phát sinh doanh thu/chi phí | QTNS.9 |
| 21 | Hành chính, hậu cần, xe, hội nghị, lễ tân, nơi làm việc, hiếu hỷ | đặt xe, phòng họp, hội nghị, lễ tân, khánh tiết, trụ sở, điện nước | QTNS | — | QTNS.10 |
| 22 | An ninh quốc phòng, dân quân tự vệ, hậu phương quân đội | quốc phòng, dân quân tự vệ, nghĩa vụ quân sự | QTNS | — | QTNS.10.5 |
| 23 | Đối ngoại với Tập đoàn và đơn vị trong VNPT; chữ ký số; chế độ liên lạc | đối ngoại, làm việc với Tập đoàn, chữ ký số, SIM/điện thoại công vụ | QTNS | — | QTNS.10.8–10.9 |
| 24 | Văn thư – lưu trữ, con dấu, công văn đi/đến | văn thư, lưu trữ, con dấu, giấy giới thiệu, giấy đi đường, sao lục | QTNS | — | QTNS.11 |
| 25 | Chuyển đổi số quản trị nhân sự (HRM) | HRM, phần mềm nhân sự | QTNS | NTAI (nếu cần hạ tầng) | QTNS.5.3, 5.10 |

### 4.3. Chiến lược – sản phẩm – sở hữu trí tuệ

| # | Lĩnh vực | Từ khóa nhận diện | Xử lý chính | Phối hợp thường gặp | Căn cứ |
|---|---|---|---|---|---|
| 26 | Chiến lược sản phẩm/dịch vụ AI cấp Công ty, nghiên cứu thị trường, đối thủ | chiến lược, định hướng phát triển, xu hướng công nghệ, đối thủ cạnh tranh, định vị | CLSHTT | SPTN, KDTV | CLSHTT.1.1–1.3 |
| 27 | Quy trình và kiểm định đưa sản phẩm ra thị trường (GTM) | GTM, go-to-market, ra mắt sản phẩm, kiểm định trước khi phát hành | CLSHTT | SPTN, KDTV | CLSHTT.1.4 |
| 28 | Danh mục sản phẩm, vòng đời, phiên bản, đánh giá hiệu quả danh mục | danh mục sản phẩm, portfolio, ngừng cung cấp, phiên bản, báo cáo hiệu quả sản phẩm | CLSHTT | SPTN | CLSHTT.3 |
| 29 | Chất lượng sản phẩm, SLA/OLA, kiểm định chất lượng, quy trình phát triển – vận hành | chất lượng dịch vụ, SLA, OLA, mức độ hài lòng, ISO, quy trình nội bộ | CLSHTT | SPTN, NTAI | CLSHTT.4 |
| 30 | Hợp tác chiến lược, hợp tác đầu tư, hệ sinh thái; ký kết với trường/viện | hợp tác chiến lược, MOU với đối tác, trường đại học, viện nghiên cứu, hệ sinh thái AI | CLSHTT | NCPT, PTDL | CLSHTT.2.1–2.4 |
| 31 | Xuất khẩu giải pháp AI, hiệp hội/diễn đàn SHTT & đổi mới sáng tạo | xuất khẩu, thị trường quốc tế, hiệp hội, diễn đàn đổi mới sáng tạo | CLSHTT | KDTV | CLSHTT.1.6, 2.2 |
| 32 | Sở hữu trí tuệ: sáng chế, bản quyền, nhãn hiệu, dữ liệu; tranh chấp, vi phạm | sở hữu trí tuệ, bằng sáng chế, giải pháp hữu ích, bản quyền phần mềm, nhãn hiệu, Cục SHTT | CLSHTT | NCPT (hồ sơ kỹ thuật) | CLSHTT.5; NCPT.2.2 |
| 33 | Chuyển giao công nghệ, thương mại hóa tài sản trí tuệ | chuyển giao công nghệ, license, thương mại hóa | CLSHTT | NCPT, KDTV | CLSHTT.2.5 |
| 34 | Quy định & quản lý công bố khoa học | quy định công bố, danh mục bài báo, kinh phí công bố, phản biện nội bộ | CLSHTT | NCPT | CLSHTT.6 |
| 35 | Cơ chế khuyến khích sáng tạo, phân chia lợi ích, lộ trình nhà nghiên cứu | sáng kiến, thưởng sáng chế, đổi mới sáng tạo nội bộ, giữ chân nhân tài nghiên cứu | CLSHTT | QTNS | CLSHTT.7 |
| 36 | Cơ chế kinh tế nội bộ | cơ chế kinh tế nội bộ, giá nội bộ, phân chia doanh thu nội bộ | CLSHTT | QTNS | CLSHTT.8 |
| 37 | Quản lý sản phẩm cụ thể: roadmap, tính năng, MVP, prototype | roadmap, tính năng mới, yêu cầu sản phẩm, PRD, MVP | SPTN | NCPT, NTAI | SPTN.1; SPTN.3 |
| 38 | Trải nghiệm người dùng, UX/UI, design system | UX, UI, design system, A/B testing, usability, trải nghiệm khách hàng | SPTN | KDTV | SPTN.2 |
| 39 | Sự cố sản phẩm, ứng cứu, phân tích nguyên nhân gốc | sự cố, gián đoạn dịch vụ, ứng cứu, RCA, postmortem | SPTN | NTAI, KDTV (thông tin khách hàng) | SPTN.4 |
| 40 | Tuyên bố giá trị, tài liệu sản phẩm, hỗ trợ GTM | value proposition, tài liệu sản phẩm, demo, brochure kỹ thuật | SPTN | KDTV | SPTN.5 |

### 4.4. Kinh doanh – thị trường – thương hiệu – khách hàng

| # | Lĩnh vực | Từ khóa nhận diện | Xử lý chính | Phối hợp thường gặp | Căn cứ |
|---|---|---|---|---|---|
| 41 | Kinh doanh, tư vấn giải pháp, dự án trọng điểm Bộ ngành, Trung ương, doanh nghiệp lớn | báo giá, đề xuất giải pháp, khách hàng Bộ/ngành, Sở/UBND địa phương, dự án trọng điểm, cơ hội kinh doanh | KDTV | PTDL, SPTN | KDTV.1.2–1.3 (mọi khách hàng); KDTV.2.1 (Bộ ngành, Trung ương, doanh nghiệp lớn) |
| 42 | Chính sách giá, chiết khấu, khuyến mại, đại lý/đối tác bán hàng | chính sách giá, bảng giá, chiết khấu, khuyến mại, đại lý | KDTV | CLSHTT, QTNS | KDTV.3.1–3.3 |
| 43 | Hỗ trợ VNPT tỉnh/thành, TTKD, đơn vị thành viên bán hàng | VNPT tỉnh, TTKD, kênh bán, đào tạo kênh bán | KDTV | SPTN | KDTV.3.4; KDTV.1.4 |
| 44 | Giám sát tiến độ, chất lượng triển khai dự án AI cho khách hàng | tiến độ dự án, vướng mắc triển khai | KDTV | PTDL, NTAI | KDTV.3.5 |
| 45 | Thương hiệu, marketing, truyền thông bên ngoài, báo chí, ấn phẩm | thương hiệu, marketing, báo chí, truyền hình, mạng xã hội, website, brochure, video | KDTV | SPTN | KDTV.4 |
| 46 | Sự kiện, hội thảo, triển lãm, xúc tiến thương mại | AI Expo, triển lãm, hội chợ, MWC, ITU, hội thảo giới thiệu sản phẩm | KDTV | SPTN, CLSHTT | KDTV.2.2; KDTV.4.7 |
| 47 | Khủng hoảng truyền thông, giám sát truyền thông | khủng hoảng truyền thông, tin xấu, media monitoring | KDTV | SPTN (nếu do sự cố sản phẩm) | KDTV.4.9 |
| 48 | Chăm sóc khách hàng, khiếu nại khách hàng, CRM | khiếu nại, phản ánh khách hàng, CSKH, CRM | KDTV | SPTN (lỗi sản phẩm) | KDTV.5 |
| 49 | Bảo hành, bảo trì dự án khách hàng đã triển khai | bảo hành, bảo trì, hỗ trợ sau bán | KDTV | PTDL | KDTV.1.4; PTDL.3.3 |

### 4.5. Công nghệ – nền tảng – dữ liệu – triển khai

| # | Lĩnh vực | Từ khóa nhận diện | Xử lý chính | Phối hợp thường gặp | Căn cứ |
|---|---|---|---|---|---|
| 50 | Nghiên cứu công nghệ lõi, mô hình AI | nghiên cứu, mô hình, LLM, NLP, xử lý giọng nói, thị giác máy tính, GenAI, mô hình tiếng Việt | NCPT | NTAI | NCPT.1 |
| 51 | Bộ dữ liệu, thư viện, thuật toán lõi | dataset, thư viện lõi, thuật toán | NCPT | — | NCPT.1.3 |
| 52 | Công bố khoa học, bài báo, hội nghị khoa học | bài báo, tạp chí, hội nghị khoa học | NCPT | CLSHTT | NCPT.2.1 |
| 53 | Đề tài/dự án nghiên cứu (quốc gia, quốc tế, cấp Tập đoàn) | đề tài KH&CN, đề tài cấp Tập đoàn, chương trình quốc gia, dự án nghiên cứu quốc tế | NCPT | PTDL chỉ khi văn bản yêu cầu mọi đơn vị cùng đề xuất | NCPT.4.2 (gần nhất); NCPT.1; PTDL.1.1 |
| 54 | Cung cấp, nâng cấp mô hình AI cho sản phẩm | chuyển giao mô hình, model release, tối ưu chi phí mô hình | NCPT | NTAI, SPTN | NCPT.3 |
| 55 | Tiêu chuẩn, khung kỹ thuật AI quốc gia | tiêu chuẩn AI, quy chuẩn kỹ thuật, khung công nghệ AI | NCPT hoặc NTAI (xem mục 6) | Đơn vị còn lại | NCPT.2.3; NTAI.4.3 |
| 56 | Hạ tầng AI: GPU, cloud, data lake, MLOps | GPU, cụm máy chủ, cloud, data lake, MLOps, hạ tầng tính toán | NTAI | — | NTAI.2.1–2.3 |
| 57 | Nền tảng dùng chung: API gateway, SDK, microservices, model hub, AIaaS | API, SDK, model hub, AIaaS, pay-per-use | NTAI | KDTV (giá AIaaS) | NTAI.2.4–2.8 |
| 58 | DevSecOps, CI/CD, triển khai đa hạ tầng, gói triển khai on-premise | CI/CD, DevOps, on-premise, triển khai tại khách hàng, container, Kubernetes | NTAI | PTDL, SPTN | NTAI.2.5; NTAI.3 |
| 59 | An toàn thông tin, bảo mật, an ninh mạng, bảo vệ dữ liệu cá nhân (hệ thống) | ATTT, an ninh mạng, lỗ hổng, rà quét, phân quyền, nhật ký truy cập, Nghị định bảo vệ dữ liệu cá nhân | NTAI | QTNS (dữ liệu nhân sự), đơn vị chủ quản hệ thống | NTAI.4.1–4.2 |
| 60 | Chủ quyền công nghệ | chủ quyền công nghệ, không phụ thuộc nước ngoài | NTAI | NCPT | NTAI.4.4 |
| 61 | PoC, sandbox thử nghiệm công nghệ mới trên nền tảng | sandbox, PoC công nghệ, đánh giá hiệu năng/chi phí | NTAI | NCPT | NTAI.1.2 |
| 62 | Phân tích dữ liệu, công cụ hỗ trợ điều hành, ra quyết định | phân tích dữ liệu, BI, dashboard, báo cáo phân tích, hỗ trợ ra quyết định | PTDL | — | PTDL.1 |
| 63 | Giải pháp AI theo ngành | chính phủ số, tài chính – ngân hàng, y tế, giáo dục, giao thông, công nghiệp, nông nghiệp | PTDL | KDTV | PTDL.2 |
| 64 | Triển khai, tích hợp dự án AI end-to-end, nghiệm thu, bàn giao | khảo sát, thiết kế giải pháp, tích hợp hệ thống khách hàng, nghiệm thu, bàn giao | PTDL | NTAI, KDTV | PTDL.3 |
| 65 | Đào tạo, chuyển giao công nghệ AI cho khách hàng, đối tác | tập huấn khách hàng, chuyển giao cho đối tác | PTDL | — | PTDL.4.1 |

## 5. Chi tiết chức năng, nhiệm vụ từng đơn vị (căn cứ trích dẫn)

### 5.0. Quyền hạn và trách nhiệm chung (áp dụng cho cả 7 đơn vị)

**Quyền hạn chung**
- Đại diện Công ty làm việc với cơ quan quản lý nhà nước, các đơn vị trong và ngoài Công ty về nội dung thuộc chức năng, nhiệm vụ, theo phân công hoặc ủy quyền.
- Yêu cầu các đơn vị trực thuộc và đơn vị liên quan phối hợp thực hiện nhiệm vụ được giao.
- Thừa lệnh Tổng Giám đốc ký văn bản triển khai công việc thuộc chức năng, nhiệm vụ khi được ủy quyền hoặc chấp thuận.
- *Riêng 4 Trung tâm (NCPT, NTAI, PTDL, SPTN)*: được tổ chức triển khai sản xuất, cung cấp sản phẩm, dịch vụ theo quy trình của Công ty và pháp luật.
- *Riêng KDTV*: được tổ chức điều hành nội bộ Ban; đề xuất bổ sung nhân lực, đào tạo, nâng lương, khen thưởng, kỷ luật người lao động theo quy định.

**Trách nhiệm chung**
- Tổ chức thực hiện đầy đủ, kịp thời chức năng, nhiệm vụ được giao.
- Chủ động phối hợp với các đơn vị trực thuộc và đơn vị liên quan trong Tập đoàn.
- Thực hiện chế độ báo cáo định kỳ, đột xuất; chịu kiểm tra, giám sát của Tổng Giám đốc.
- Quản lý, sử dụng hiệu quả nhân lực, tài chính, tài sản được giao.
- Thủ trưởng đơn vị chịu trách nhiệm trước Tổng Giám đốc về kết quả của đơn vị; cấp phó được phân công phụ trách một số lĩnh vực và chịu trách nhiệm trước Thủ trưởng.

---

### 5.1. QTNS — Ban Quản trị và Nhân sự

**Chức năng**: Tham mưu cho Tổng Giám đốc về tổ chức bộ máy, nhân sự, văn hóa doanh nghiệp, phát triển nguồn nhân lực, tiền lương, thi đua khen thưởng, chính sách xã hội, truyền thông nội bộ, hành chính văn thư, quản trị, đối ngoại, pháp chế, kế toán tài chính; tham mưu công tác xây dựng Đảng (tổ chức, cán bộ, đảng viên, bảo vệ chính trị nội bộ, kiểm tra, giám sát, kỷ luật Đảng); bảo đảm nguồn lực tài chính, quản trị nội bộ và hỗ trợ điều hành.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Trưởng Ban Quản trị và Nhân sự | Phạm Thành Ngữ | Toàn bộ | ngupt@vnpt.vn | ngupt@vnpt.vn |  |
| Phó Trưởng Ban Quản trị và Nhân sự | Nguyễn Thị Thu Hiền | [cần bổ sung] | ntt.hien@vnpt.vn | ntt.hien@vnpt.vn |  |
| Phụ trách kế toán | Phan Chí Dũng | QTNS.9 (Tài chính – Kế toán – Thống kê – Kiểm toán) | phanchidung@vnpt.vn | phanchidung@vnpt.vn | Lĩnh vực suy ra từ chức danh |
| Đầu mối văn thư | [cần bổ sung] | Tiếp nhận văn bản đến | [cần bổ sung] | [cần bổ sung] |  |

**Nhiệm vụ**

- **QTNS.1 — Tổ chức bộ máy và văn hóa doanh nghiệp**
  1. Xây dựng, trình duyệt phương án mô hình tổ chức, quy chế tổ chức và hoạt động, chức năng nhiệm vụ của Công ty và các đơn vị trực thuộc; tổ chức thực hiện bảo đảm tinh gọn, hiệu quả.
  2. Xây dựng, quản lý, hướng dẫn định mức, định biên lao động, hệ thống chức danh, vị trí công việc, mô tả công việc, thư viện công việc.
  3. Đề xuất, thực hiện bố trí, sắp xếp, điều chuyển nhân sự giữa các đơn vị, vị trí công việc.
  4. Xây dựng, triển khai kế hoạch truyền thông nội bộ định kỳ, bảo đảm thông tin hai chiều lãnh đạo – nhân viên.
  5. Xây dựng, quản lý, triển khai Văn hóa doanh nghiệp.
- **QTNS.2 — Tuyển dụng, đào tạo, phát triển nhân sự chất lượng cao**
  1. Xây dựng kế hoạch phát triển nhân sự phù hợp chiến lược Tập đoàn và Công ty.
  2. Xây dựng cơ chế tìm kiếm, thu hút nhân sự giỏi trong và ngoài nước về AI.
  3. Tiếp nhận, hướng dẫn hội nhập nhân sự mới.
  4. Xây dựng chương trình đào tạo chuyên biệt cho nhân sự nòng cốt; khảo sát nhu cầu đào tạo, lập kế hoạch đào tạo định kỳ/đột xuất.
  5. Tổ chức đào tạo nội bộ hoặc phối hợp đơn vị đào tạo bên ngoài; đánh giá hiệu quả sau đào tạo.
  6. Xây dựng khung năng lực, tiêu chí, quy trình đánh giá năng lực định kỳ (cơ sở khen thưởng, trả lương, bổ nhiệm, đào tạo).
  7. Quản lý công tác nước ngoài theo quy chế của Tập đoàn, Công ty.
- **QTNS.3 — Chế độ chính sách, lương, thưởng, phúc lợi, ATVSLĐ**
  1. Xây dựng, triển khai hệ thống đo lường hiệu suất, đánh giá kết quả công việc cá nhân, tập thể, bộ phận.
  2. Xây dựng quy chế và thực hiện công tác tiền lương, thưởng, chế độ chính sách cho người lao động.
  3. Hướng dẫn, triển khai BHXH, BHYT, BH thất nghiệp, chính sách xã hội, chế độ người có công.
  4. Quản lý, theo dõi chế độ nghỉ phép năm, ốm đau, thai sản, điều dưỡng, chăm sóc sức khỏe.
  5. Phối hợp Công đoàn tổ chức nghỉ mát, điều dưỡng theo chế độ.
  6. Xây dựng quy chế sử dụng quỹ phúc lợi, quỹ chính sách xã hội.
  7. An toàn vệ sinh lao động; y tế, chăm sóc sức khỏe.
- **QTNS.4 — Thi đua – Khen thưởng**
  1. Lập kế hoạch, triển khai phong trào thi đua theo chuyên đề, giai đoạn.
  2. Tổng hợp, thẩm định, đề xuất khen thưởng tập thể, cá nhân trong và ngoài Công ty theo chương trình của Công ty, Tập đoàn.
  3. Lập báo cáo định kỳ, đột xuất về thi đua khen thưởng.
  4. Đề xuất hình thức khen thưởng, kỷ luật cá nhân, tập thể.
- **QTNS.5 — Quản trị chung**
  1. Quản trị rủi ro thuộc nhiệm vụ phụ trách.
  2. Phối hợp bảo vệ dữ liệu cá nhân người lao động.
  3. Đề xuất, áp dụng công cụ công nghệ trong quản trị nhân sự; duy trì và hỗ trợ người dùng HRM; chuyển đổi số lĩnh vực phụ trách.
  4. Xây dựng hệ thống văn bản, quy chế, quy trình thuộc nhiệm vụ phụ trách.
  5. Thực hiện công tác nhân sự, quy hoạch, phát triển nhân sự, quan hệ lao động theo phân cấp của Tập đoàn.
  6. Quản lý hồ sơ nhân sự thuộc diện Công ty quản lý; báo cáo thống kê nhân sự; xác nhận tài liệu liên quan người lao động.
  7. Thường trực Hội đồng lương, Hội đồng thi đua khen thưởng, Hội đồng Bảo hộ lao động; Ban chỉ đạo phòng chống tham nhũng, chống buôn lậu, thực hành tiết kiệm, chống lãng phí.
  8. Công đoàn: phối hợp giám sát thực hiện Thỏa ước lao động tập thể, nội quy, quy chế.
  9. Chủ trì tổ chức tham quan nghỉ mát; thẩm định, đề xuất khen thưởng về công tác Công đoàn; phối hợp tổ chức Hội nghị người lao động hằng năm.
  10. Quản lý nhân sự trên hệ thống HRM.
  11. Nhiệm vụ khác do Lãnh đạo Công ty giao.
- **QTNS.6 — Công tác Đảng**
  1. Triển khai chỉ thị, nghị quyết, chủ trương của Đảng, Nhà nước, Đảng ủy Tập đoàn.
  2. Tham mưu Ban chấp hành Đảng ủy về công tác cán bộ, quy hoạch cán bộ.
  3. Chủ trì chuẩn bị kế hoạch, nội dung hội nghị, sự kiện của Đảng ủy Công ty.
  4. Thủ tục trình Đảng ủy Tập đoàn: giới thiệu sinh hoạt đảng, kết nạp, công nhận đảng viên chính thức, xóa tên, đảng tịch; quản lý dữ liệu đảng viên.
  5. Tham mưu UBKT Đảng ủy về kiểm tra, giám sát, thi hành kỷ luật Đảng.
  6. Xây dựng chương trình, kế hoạch kiểm tra giám sát các Chi bộ trực thuộc.
  7. Hướng dẫn, thực hiện kiểm tra, giám sát Chi bộ và đảng viên.
  8. Sơ kết, tổng kết công tác Đảng và kiểm tra, giám sát.
- **QTNS.7 — Tổng hợp – Pháp chế – Thanh tra**
  1. Thu thập, tổng hợp thông tin phục vụ chỉ đạo điều hành; báo cáo tổng hợp, định kỳ.
  2. Theo dõi thực hiện kết luận, chỉ đạo của lãnh đạo; xây dựng lịch công tác, chương trình làm việc.
  3. Cải cách hành chính, quản lý lao động, nhân sự, thi đua – khen thưởng.
  4. Cập nhật, rà soát văn bản pháp luật; thẩm định, đề xuất điều chỉnh quy chế nội bộ.
  5. Thẩm định pháp lý hợp đồng kinh tế, biên bản ghi nhớ.
  6. Xây dựng, quản lý quy chế nội bộ về chi tiêu, cấp phát trang thiết bị.
  7. Thanh tra: kế hoạch thanh tra, tiếp dân, giải quyết khiếu nại, tố cáo; kiểm tra chấp hành pháp luật và quy định nội bộ.
- **QTNS.8 — Kế hoạch – Đầu tư – Quản lý tài sản**
  1. Quản lý kế hoạch, đầu tư theo phân cấp.
  2. Xây dựng, cân đối, triển khai kế hoạch SXKD và đầu tư hằng năm.
  3. Chủ đầu tư dự án được ủy quyền; thủ tục tài chính, thanh toán, quyết toán dự án.
  4. Quản lý, kiểm kê, theo dõi tăng giảm, thanh lý tài sản.
  5. Lập kế hoạch đầu tư, mua sắm thường xuyên; mua sắm hàng hóa, vật phẩm phục vụ CSKH, sự kiện đối ngoại, giao lưu quốc tế, hội nghị/hội thảo ở nước ngoài; hướng dẫn quy trình mua sắm.
  6. Mua sắm công cụ dụng cụ, vật tư thiết bị văn phòng, văn phòng phẩm, ấn phẩm.
- **QTNS.9 — Tài chính – Kế toán – Thống kê – Kiểm toán**
  1. Tham mưu Tổng Giám đốc về tài chính, kế toán, thống kê, kiểm tra, giám sát.
  2. Áp dụng pháp luật tài chính, kế toán, thuế; góp ý dự thảo văn bản pháp luật và quy chế Tập đoàn về tài chính, kế toán, thuế.
  3. Ban hành quy chế tài chính; quy chế quản lý nợ phải thu/phải trả, hàng tồn kho, tài sản cố định, chế độ kế toán, hóa đơn, chứng từ, thanh toán với ngân sách.
  4. Hướng dẫn hóa đơn, chứng từ, chính sách thuế, ghi nhận doanh thu, chi phí khi ban hành chính sách kinh doanh; kiểm soát hóa đơn đầu ra/đầu vào; kê khai, nộp thuế, phí, lệ phí.
  5. Đề xuất cơ chế chính sách tài chính kế toán nâng cao quản trị vốn, tài sản.
  6. Hạch toán kế toán, lưu trữ chứng từ, dữ liệu kế toán.
  7. Lập, nộp báo cáo tài chính, báo cáo quản trị định kỳ, đột xuất.
  8. Xây dựng, phân rã kế hoạch thu chi tài chính hằng tháng; nộp/chuyển tiền về Tập đoàn; cân đối dòng tiền SXKD, đầu tư XDCB, nộp NSNN.
  9. Thu hồi nợ phải thu; thanh toán nợ phải trả; đối chiếu, xác nhận công nợ.
  10. Tham gia Hội đồng kiểm kê; thanh lý, nhượng bán; đánh giá lại tài sản cố định.
  11. Kiểm tra, giám sát nội bộ về tài chính kế toán, thuế; quản trị rủi ro tài chính kế toán, thuế.
  12. Quản trị tài chính kế toán trên phần mềm; cập nhật đầy đủ dữ liệu theo quy định Tập đoàn.
  13. Chủ trì quản lý doanh thu, chi phí, hiệu quả SXKD toàn Công ty; đầu mối công bố số liệu đối soát qua hệ thống đối soát thanh khoản của Tập đoàn.
  14. Nhiệm vụ khác theo phân công của Tổng Giám đốc.
- **QTNS.10 — Hành chính – Quản trị – Hậu cần**
  1. Quản lý tài sản, công cụ dụng cụ, trang thiết bị, kho bãi; phối hợp quản lý hạ tầng cơ sở; tổ chức lễ tân, khánh tiết, phục vụ hội nghị, hội thảo, cuộc họp trong và ngoài nước.
  2. Quản lý, điều hành phương tiện đi lại; bảo dưỡng, sửa chữa xe; nhiên liệu; an toàn lái xe.
  3. Mua sắm, cấp phát, quản lý, bảo trì thiết bị, công cụ văn phòng.
  4. Đề xuất trang bị cơ sở vật chất phục vụ lãnh đạo và đơn vị.
  5. Tham mưu an ninh quốc phòng, dân quân tự vệ, chính sách hậu phương quân đội.
  6. Quản trị vệ sinh, điện nước, hạ tầng trụ sở; quản lý nhà đất, mặt bằng.
  7. Giải quyết việc hiếu, hỷ theo quy định.
  8. Đầu mối hoạt động đối ngoại, phối hợp và gắn kết với Tập đoàn và các đơn vị trực thuộc.
  9. Đầu mối chế độ liên lạc, chữ ký số phục vụ điều hành SXKD.
  10. Sắp xếp, bố trí nơi làm việc cho các đơn vị.
- **QTNS.11 — Văn thư – Lưu trữ**
  1. Tổ chức, hướng dẫn công tác văn thư – lưu trữ cho các đơn vị; xây dựng quy trình xử lý văn bản.
  2. Quản lý, sử dụng con dấu theo quy định pháp luật; đào tạo cán bộ văn thư.
  3. Quản lý sổ sách, công văn đi – đến, giấy giới thiệu, giấy đi đường.
  4. Tiếp nhận, phát hành, sao lục, lưu trữ công văn, tài liệu; khai thác an toàn hồ sơ lưu trữ.
  5. Báo cáo định kỳ, đột xuất về văn thư, lưu trữ.
  6. Đề xuất ứng dụng CNTT vào văn thư – lưu trữ.
  7. Đầu mối cung cấp báo chí, tài liệu cho lãnh đạo và các đơn vị.
- **QTNS.12 — Bảo vệ – Y tế – Chăm sóc sức khỏe**
  1. Bảo vệ an ninh, an toàn cơ quan; phòng chống cháy nổ; phối hợp lực lượng chức năng.
  2. Kiểm soát khách, phương tiện ra vào; giữ trật tự cơ quan.
  3. Diễn tập PCCC; đề xuất trang bị, bảo dưỡng phương tiện an ninh, PCCC.
  4. Y tế cơ quan: chăm sóc sức khỏe, sơ cứu, khám chữa bệnh, tuyên truyền phòng bệnh, vệ sinh môi trường lao động.
  5. Công tác dân số, an toàn thực phẩm, phòng chống tệ nạn xã hội.
  6. Đề xuất cải thiện điều kiện làm việc (ánh sáng, tiếng ồn, môi trường).
  7. Vệ sinh môi trường cơ quan "Xanh – sạch – đẹp".

---

### 5.2. CLSHTT — Ban Chiến lược và Sở hữu trí tuệ

**Chức năng**: (1) Nghiên cứu, xây dựng, quản trị chiến lược phát triển sản phẩm, danh mục dịch vụ AI; (2) Quản lý, đăng ký, bảo hộ, khai thác tài sản trí tuệ; (3) Quản lý chất lượng, vòng đời và hiệu quả sản phẩm, đồng bộ với định hướng Tập đoàn và nhu cầu thị trường.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Trưởng Ban Chiến lược và Sở hữu trí tuệ | Tô Nguyễn Dũng Anh | Toàn bộ | tndunganh@vnpt.vn | tndunganh@vnpt.vn |  |
| Phó Trưởng Ban Chiến lược và Sở hữu trí tuệ | Lê Thái Hưng | [cần bổ sung] | lethaihung89@vnpt.vn | lethaihung89@vnpt.vn |  |

**Nhiệm vụ**

- **CLSHTT.1 — Nghiên cứu thị trường và xây dựng chiến lược**
  1. Nghiên cứu xu hướng công nghệ, nhu cầu khách hàng, đối thủ cạnh tranh để tham mưu chiến lược dịch vụ.
  2. Tìm kiếm sản phẩm dịch vụ mới tiềm năng, đối tác hợp tác phát triển.
  3. Xây dựng kế hoạch phát triển, nâng cấp, định vị sản phẩm dịch vụ hằng năm.
  4. Ban hành quy trình và kiểm định hoạt động đưa sản phẩm ra thị trường (GTM).
  5. Phối hợp VNPT tỉnh/thành và các kênh phân phối mở rộng thị trường.
  6. Tìm kiếm cơ hội xuất khẩu giải pháp AI ra quốc tế.
- **CLSHTT.2 — Tham vấn chuyển giao và hợp tác đầu tư**
  1. Thúc đẩy hợp tác chiến lược, mở rộng thị trường sản phẩm AI.
  2. Đại diện Công ty tại hiệp hội, diễn đàn về sở hữu trí tuệ và đổi mới sáng tạo.
  3. Ký kết hợp tác với trường đại học, viện nghiên cứu, trung tâm sáng chế.
  4. Xây dựng cơ chế hợp tác đầu tư, hình thành hệ sinh thái AI đổi mới sáng tạo.
  5. Tham mưu chuyển giao công nghệ, khai thác, thương mại hóa tài sản trí tuệ.
  6. Tham gia đào tạo, hội thảo quốc tế về quản trị tài sản trí tuệ.
- **CLSHTT.3 — Quản lý vòng đời sản phẩm**
  1. Quản lý danh mục sản phẩm dịch vụ của Công ty.
  2. Theo dõi, đánh giá hiệu quả từng sản phẩm và danh mục tổng thể.
  3. Quản lý triển khai phiên bản, vòng đời sản phẩm; báo cáo định kỳ/đột xuất.
- **CLSHTT.4 — Quản trị chất lượng và quy trình**
  1. Kiểm tra, giám sát chất lượng sản phẩm dịch vụ AI (SLA, OLA, mức độ hài lòng).
  2. Kiểm định chất lượng sản phẩm theo quy định.
  3. Xây dựng, cải tiến quy trình nội bộ về phát triển, triển khai, vận hành sản phẩm.
  4. Phối hợp đơn vị, đối tác liên quan trong công tác chất lượng.
- **CLSHTT.5 — Quản lý, đăng ký, bảo hộ tài sản trí tuệ**
  1. Quản lý toàn diện tài sản trí tuệ: sáng chế, bản quyền, nhãn hiệu, dữ liệu.
  2. Thủ tục bảo hộ quyền sở hữu trí tuệ trong nước và quốc tế.
  3. Giám sát việc sử dụng, khai thác tài sản trí tuệ; xử lý vi phạm, tranh chấp.
- **CLSHTT.6 — Quản lý và phát triển công bố khoa học**
  1. Ban hành quy định nội bộ về quản lý công bố khoa học.
  2. Khuyến khích cán bộ công bố tại hội nghị, tạp chí uy tín.
  3. Cơ chế hỗ trợ: kinh phí, mentoring, phản biện nội bộ.
  4. Quản lý, tổng hợp danh mục công bố khoa học; báo cáo định kỳ cho Ban Lãnh đạo.
- **CLSHTT.7 — Cơ chế khuyến khích sáng tạo**
  1. Cơ chế thưởng, tôn vinh sáng kiến, sáng chế, công bố khoa học.
  2. Quy định phân chia lợi ích khi thương mại hóa tài sản trí tuệ.
  3. Chương trình khuyến khích đổi mới sáng tạo nội bộ.
  4. Lộ trình nghề nghiệp cho nhà nghiên cứu, cơ chế giữ chân nhân tài.
- **CLSHTT.8 — Cơ chế kinh tế**
  1. Quản lý, thực hiện cơ chế kinh tế nội bộ của Tập đoàn; xây dựng cơ chế kinh tế nội bộ của Công ty (nếu có).

---

### 5.3. KDTV — Ban Kinh doanh và Tư vấn Công nghệ cao

**Chức năng**: (1) Tham mưu Ban Tổng Giám đốc điều hành kinh doanh sản phẩm, dịch vụ, giải pháp; phát triển thị trường; chăm sóc khách hàng; quảng bá thương hiệu VNPT AI thành thương hiệu quốc gia vươn tầm quốc tế. (2) Chủ trì tư vấn, bán hàng, quảng bá sản phẩm; phối hợp các đơn vị kinh doanh trong hệ thống VNPT mở rộng thị trường trong nước và quốc tế.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Giám đốc Ban Kinh doanh và Tư vấn Công nghệ cao | Vũ Trọng Đạo | Toàn bộ | trongdao@vnpt.vn | trongdao@vnpt.vn |  |
| Phó Giám đốc Ban Kinh doanh và Tư vấn Công nghệ cao | Hoàng Thị Thu | [cần bổ sung] | hoangthithu@vnpt.vn | hoangthithu@vnpt.vn |  |

**Nhiệm vụ**

- **KDTV.1 — Phát triển và tư vấn sản phẩm AI chủ lực**
  1. Khảo sát nhu cầu thị trường, xu hướng công nghệ, đối thủ để đề xuất dòng sản phẩm AI chủ lực cho nội bộ Tập đoàn và khách hàng ngoài VNPT.
  2. Phát triển, đóng gói, tư vấn ứng dụng sản phẩm AI chủ lực cho các phân khúc khách hàng.
  3. Tư vấn toàn diện vòng đời dự án AI: khảo sát, thiết kế giải pháp, triển khai, vận hành, tối ưu.
  4. Tổ chức nguồn lực tư vấn, đào tạo kênh bán, bảo hành, bảo trì dự án khách hàng đã triển khai.
  5. Tổ chức/phối hợp tổ chức đấu thầu mua sắm phục vụ hoạt động SXKD.
- **KDTV.2 — Chiếm lĩnh thị trường trong nước và mở rộng quốc tế**
  1. Trực tiếp kinh doanh dự án, giải pháp AI trọng điểm cấp Bộ ngành, Trung ương, doanh nghiệp lớn.
  2. Xúc tiến thương mại, hội thảo, triển lãm trong và ngoài nước.
- **KDTV.3 — Phối hợp kinh doanh toàn hệ thống VNPT**
  1. Xây dựng, trình duyệt, triển khai chính sách giá GTM cho sản phẩm AI chủ lực theo phân khúc, kênh, thị trường.
  2. Ban hành chính sách ưu đãi (chiết khấu, khuyến mại, đại lý/đối tác).
  3. Định kỳ rà soát, cập nhật chính sách giá và ưu đãi.
  4. Điều hành, hỗ trợ VNPT tỉnh/thành, Trung tâm kinh doanh, đơn vị thành viên trong bán hàng, tư vấn, triển khai dịch vụ AI.
  5. Giám sát tiến độ, chất lượng triển khai dự án AI; tháo gỡ khó khăn.
  6. Phối hợp các đơn vị trong VNPT AI và VNPT-IT bảo đảm đồng bộ kinh doanh và CSKH.
- **KDTV.4 — Xây dựng và phát triển thương hiệu VNPT AI**
  1. Xây dựng, quản lý thương hiệu VNPT AI.
  2. Chiến lược thương hiệu cho sản phẩm AI chủ lực.
  3. Thiết kế, sản xuất ấn phẩm truyền thông (brochure, profile, video, infographic, báo cáo thường niên AI).
  4. Marketing, truyền thông, quan hệ đối tác phát triển thương hiệu.
  5. So sánh định vị giá trị với đối thủ, hỗ trợ chiến lược giá; tư vấn gói giải pháp linh hoạt (SaaS, subscription, pay-per-use).
  6. Chiến dịch truyền thông tích hợp (IMC) đa kênh: báo chí, truyền hình, mạng xã hội, website, hội nghị, triển lãm.
  7. Chủ trì tổ chức/tham gia sự kiện AI trong nước và quốc tế (AI Expo, ITU Digital Summit, MWC…).
  8. Thu thập phản hồi khách hàng, nghiên cứu thị trường để đề xuất cải tiến sản phẩm.
  9. Quản trị khủng hoảng truyền thông: kịch bản xử lý, phân công, kênh phản hồi; giám sát truyền thông.
- **KDTV.5 — Chăm sóc khách hàng và hỗ trợ dịch vụ**
  1. Thiết lập kênh giao tiếp, CSKH; xử lý yêu cầu, khiếu nại kịp thời.
  2. Vận hành CRM và công cụ CNTT quản lý thông tin khách hàng, dữ liệu kinh doanh.
- **KDTV.6 — Nhiệm vụ khác**
  1. Nhiệm vụ khác do Lãnh đạo giao.
  2. Xây dựng kế hoạch phát triển sản phẩm dựa trên xu hướng thị trường và nhu cầu khách hàng.

---

### 5.4. NCPT — Trung tâm Nghiên cứu và Phát triển công nghệ AI

**Chức năng**: (1) Đầu mối nghiên cứu, làm chủ, phát triển công nghệ AI tiên tiến; (2) Xuất bản công trình khoa học, đăng ký sáng chế; (3) Xây dựng, huấn luyện, chuyển giao mô hình AI dùng chung cho sản phẩm và ứng dụng trong Tập đoàn.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Giám đốc Trung tâm Nghiên cứu và Phát triển công nghệ AI | Cao Thanh Hà | Toàn bộ | hact3@vnpt.vn | hact3@vnpt.vn |  |

**Nhiệm vụ**

- **NCPT.1 — Nghiên cứu và phát triển công nghệ lõi**
  1. Nghiên cứu, thiết kế, huấn luyện, tối ưu mô hình AI tiên tiến: NLP, Voice Processing, Computer Vision, Generative AI, Data Science… đạt chuẩn quốc tế.
  2. Phát triển mô hình AI dành riêng cho tiếng Việt, tối ưu đa lĩnh vực.
  3. Phát triển thư viện, bộ dữ liệu, thuật toán lõi cho sản phẩm AI của VNPT.
- **NCPT.2 — Công bố nghiên cứu khoa học và sáng chế**
  1. Nghiên cứu, công bố tại hội nghị, tạp chí khoa học uy tín quốc tế.
  2. Đăng ký, bảo hộ sáng chế, giải pháp hữu ích, bản quyền phần mềm AI do VNPT AI phát triển.
  3. Tham gia xây dựng tiêu chuẩn, tham số kỹ thuật, khung công nghệ AI quốc gia.
- **NCPT.3 — Chuyển giao mô hình AI**
  1. Xây dựng, cung cấp, duy trì nâng cấp mô hình AI cho sản phẩm của Công ty.
  2. Bảo đảm tính khả chuyển, an toàn, hiệu năng, tối ưu chi phí mô hình.
- **NCPT.4 — Hợp tác nghiên cứu và đào tạo**
  1. Hợp tác với trường đại học, viện nghiên cứu, doanh nghiệp trong và ngoài nước.
  2. Tham gia dự án nghiên cứu quốc gia, quốc tế về AI.
  3. Đào tạo, bồi dưỡng nhân lực nghiên cứu AI chất lượng cao cho VNPT và cộng đồng.

---

### 5.5. NTAI — Trung tâm Nền tảng AI

**Chức năng**: (1) Nghiên cứu, phát triển, vận hành nền tảng AI triển khai linh hoạt trên hạ tầng CNTT truyền thống, cloud của VNPT và public cloud (AWS, Azure…), bảo đảm bền vững, mở rộng, chủ quyền công nghệ; (2) Quản lý, khai thác, tối ưu tài sản công nghệ được giao: hạ tầng tính toán AI, hệ thống dữ liệu, nền tảng dịch vụ AI.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Phó Giám đốc phụ trách Trung tâm Nền tảng AI | Trương Ngọc Sơn | Toàn bộ | tnson@vnpt.vn | tnson@vnpt.vn | Phụ trách đơn vị (chưa có Giám đốc) |

**Nhiệm vụ**

- **NTAI.1 — Phối hợp nghiên cứu và chuyển giao công nghệ**
  1. Phối hợp NCPT tiếp nhận, thử nghiệm, chuẩn hóa công nghệ lõi (NLP, Voice, CV, GenAI, Data Science…) thành thành phần tái sử dụng trên nền tảng.
  2. Thử nghiệm nhanh (sandbox, PoC) đánh giá khả thi, hiệu năng, chi phí công nghệ mới.
  3. Hỗ trợ nhóm sản phẩm, dự án tích hợp công nghệ lõi vào nền tảng và triển khai tới khách hàng.
- **NTAI.2 — Phát triển và vận hành nền tảng AI**
  1. Quản lý GPU cluster, cloud AI, data lake, hệ thống MLOps.
  2. Bảo đảm năng lực huấn luyện, suy luận mô hình quy mô lớn.
  3. Tối ưu hiệu suất, chi phí vận hành hạ tầng AI.
  4. Xây dựng, vận hành nền tảng AI dùng chung: API gateway, SDK, microservices, MLOps platform, AI model hub.
  5. Thiết lập, duy trì quy trình DevSecOps (CI/CD) tự động hóa triển khai.
  6. Bảo đảm kiến trúc mở, module hóa, dễ tích hợp, dễ mở rộng.
  7. Phát triển AI-as-a-Service (AIaaS) theo mô hình SaaS, subscription, pay-per-use.
  8. Tích hợp quản lý vòng đời mô hình (ML lifecycle) rút ngắn nghiên cứu → thử nghiệm → production.
- **NTAI.3 — Tối ưu triển khai đa hạ tầng**
  1. Thiết kế, triển khai, quản lý dịch vụ trên cloud, máy chủ vật lý, hệ thống tính toán hiệu năng cao.
  2. Tích hợp công cụ orchestration, containerization, virtualization.
  3. Xây dựng gói triển khai tiêu chuẩn (deployment package) cho khách hàng có hạ tầng khác nhau.
  4. Tối ưu kiến trúc nền tảng, dịch vụ AI về tốc độ, hiệu suất, chi phí.
- **NTAI.4 — An toàn thông tin, bảo mật và chủ quyền công nghệ**
  1. Bảo mật mô hình, dữ liệu, nền tảng; phân quyền, nhật ký truy cập, giám sát an ninh.
  2. Tuân thủ pháp luật về bảo vệ dữ liệu cá nhân, an toàn thông tin, an ninh mạng.
  3. Chủ trì xây dựng, áp dụng chuẩn kỹ thuật nền tảng AI theo định hướng quốc gia; phối hợp cơ quan quản lý, tổ chức quốc tế về tiêu chuẩn AI.
  4. Đề xuất giải pháp chủ quyền công nghệ: làm chủ công cụ, không phụ thuộc hạ tầng nước ngoài, giữ tương thích quốc tế.

---

### 5.6. PTDL — Trung tâm Phân tích dữ liệu và Ứng dụng AI đa ngành

**Chức năng**: (1) Triển khai phân tích dữ liệu và ứng dụng AI trong nhiều ngành, lĩnh vực; (2) Nghiên cứu, phát triển, cung cấp giải pháp, sản phẩm, dịch vụ AI cho SXKD của Công ty và khách hàng trong nước, quốc tế.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm / ngành) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Phó Giám đốc phụ trách Trung tâm Phân tích dữ liệu và Ứng dụng AI đa ngành | Trần Hữu Cương | Toàn bộ | tranhuucuong@vnpt.vn | tranhuucuong@vnpt.vn | Phụ trách đơn vị (chưa có Giám đốc) |

**Nhiệm vụ**

- **PTDL.1 — Quản lý và phân tích dữ liệu**
  1. Nghiên cứu, phát triển mô hình AI và mô hình phân tích dữ liệu trong tài chính, y tế, giáo dục, sản xuất, giao thông và lĩnh vực khác.
  2. Phát triển công cụ hỗ trợ điều hành, ra quyết định; tích hợp kết quả phân tích cho nội bộ Công ty, Tập đoàn và khách hàng ngoài VNPT.
- **PTDL.2 — Phát triển giải pháp AI đa ngành**
  1. Xây dựng, đóng gói giải pháp AI cho chính phủ số, tài chính – ngân hàng, y tế, giáo dục, giao thông, công nghiệp, nông nghiệp.
  2. Thiết kế mô hình AI theo đặc thù từng ngành.
  3. Triển khai PoC, đánh giá, hoàn thiện, thương mại hóa sản phẩm, giải pháp AI.
- **PTDL.3 — Tích hợp và triển khai dự án AI**
  1. Khảo sát nhu cầu, lập phương án, triển khai dự án AI end-to-end.
  2. Tích hợp giải pháp AI vào hệ thống CNTT hiện có của khách hàng.
  3. Nghiệm thu, bàn giao, hỗ trợ vận hành, bảo trì, tối ưu sau triển khai.
- **PTDL.4 — Hợp tác và chuyển giao công nghệ**
  1. Đào tạo, tập huấn, chuyển giao công nghệ AI cho khách hàng, đối tác.
  2. Hợp tác viện nghiên cứu, trường đại học, doanh nghiệp mở rộng nghiên cứu, ứng dụng AI.

---

### 5.7. SPTN — Trung tâm Sản phẩm & Trải nghiệm xuất sắc

**Chức năng**: (1) Quản lý, điều phối vòng đời sản phẩm AI; bảo đảm sản phẩm đáp ứng thị trường, đạt chất lượng, trải nghiệm tốt; (2) Phối hợp chặt với KDTV đưa sản phẩm ra thị trường thành công.

**Lãnh đạo đơn vị**

| Chức danh | Họ và tên | Lĩnh vực phụ trách (mã nhóm / sản phẩm) | Email | Tài khoản eOffice | Ghi chú |
|---|---|---|---|---|---|
| Phó Giám đốc phụ trách Trung tâm Sản phẩm và Trải nghiệm xuất sắc | Nguyễn Quang Huy | Toàn bộ | quanghuy@vnpt.vn | quanghuy@vnpt.vn | Phụ trách đơn vị (chưa có Giám đốc) |

**Nhiệm vụ**

- **SPTN.1 — Phát triển và thiết kế sản phẩm**
  1. Xây dựng chiến lược phát triển sản phẩm theo xu hướng thị trường, nhu cầu khách hàng, mục tiêu kinh doanh.
  2. Lập kế hoạch, thiết kế tính năng mới, phát triển sản phẩm.
- **SPTN.2 — Quản lý trải nghiệm người dùng (UX/CX)**
  1. Xây dựng design system và bộ quy chuẩn UX/UI chung toàn Công ty.
  2. Đo lường, phân tích trải nghiệm khách hàng; A/B testing, usability testing; trải nghiệm đồng nhất trên web, mobile, API.
- **SPTN.3 — Đổi mới và cải tiến liên tục**
  1. Áp dụng dữ liệu & AI vào phát triển sản phẩm (predictive UX, personalization).
  2. Cơ chế thử nghiệm nhanh (rapid prototyping, MVP); theo dõi xu hướng, đề xuất cải tiến.
- **SPTN.4 — Chính sách xử lý sự cố sản phẩm**
  1. Ban hành quy trình chuẩn phát hiện, phân loại, phản hồi, khắc phục sự cố.
  2. Cơ chế phối hợp các trung tâm trong ứng cứu, khôi phục dịch vụ.
  3. Tổng kết, phân tích nguyên nhân gốc rễ, cải tiến sau sự cố.
- **SPTN.5 — Hỗ trợ kinh doanh và Marketing**
  1. Bộ tiêu chí tuyên bố giá trị cho từng phân khúc khách hàng.
  2. Hỗ trợ chiến lược GTM, tài liệu sản phẩm, trải nghiệm sản phẩm.
  3. Phối hợp Marketing bảo đảm thông điệp truyền thông khớp trải nghiệm thực tế.

## 6. Vùng chồng lấn và quy tắc phân xử

| Chủ đề | Đơn vị cùng có nhiệm vụ | Quy tắc chọn Xử lý chính |
|---|---|---|
| Chiến lược / kế hoạch phát triển sản phẩm | CLSHTT.1.3, SPTN.1.1, KDTV.6.2 | Cấp **Công ty / danh mục** (định hướng, định vị, kế hoạch năm) → CLSHTT. Cấp **một sản phẩm cụ thể** (tính năng, roadmap) → SPTN. Đề xuất xuất phát từ **nhu cầu thị trường/khách hàng** → KDTV phối hợp |
| Vòng đời sản phẩm | CLSHTT.3, SPTN (chức năng 1) | Quản lý danh mục, đánh giá hiệu quả, báo cáo vòng đời → CLSHTT. Điều phối phát triển, cải tiến sản phẩm → SPTN |
| GTM | CLSHTT.1.4, KDTV.3.1, SPTN.5.2 | **Quy trình, kiểm định** GTM → CLSHTT. **Chính sách giá** GTM → KDTV. **Tài liệu, trải nghiệm** sản phẩm cho GTM → SPTN |
| Chất lượng vs sự cố | CLSHTT.4, SPTN.4 | Giám sát chất lượng định kỳ, SLA/OLA, kiểm định → CLSHTT. Sự cố đang xảy ra hoặc phân tích sau sự cố → SPTN (NTAI phối hợp nếu do hạ tầng) |
| Sở hữu trí tuệ | CLSHTT.5, NCPT.2.2 | Thủ tục bảo hộ, quản lý, tranh chấp → CLSHTT. Văn bản yêu cầu nội dung kỹ thuật của sáng chế/bản quyền → NCPT phối hợp |
| Công bố khoa học | CLSHTT.6, NCPT.2.1 | Quy định, chính sách hỗ trợ, thống kê → CLSHTT. Bài báo, hội nghị chuyên môn cụ thể → NCPT |
| Hợp tác với trường/viện | CLSHTT.2.3, NCPT.4.1, PTDL.4.2 | Ký kết thỏa thuận khung/hợp tác chiến lược → CLSHTT. Hợp tác nghiên cứu cụ thể → NCPT. Hợp tác ứng dụng theo ngành → PTDL |
| Tiêu chuẩn AI quốc gia | NCPT.2.3, NTAI.4.3 | Tiêu chuẩn về mô hình, thuật toán, tham số kỹ thuật → NCPT. Chuẩn kỹ thuật nền tảng, hạ tầng, bảo mật → NTAI |
| Dự án khách hàng | KDTV.2.1, KDTV.3.5, PTDL.3 | Giai đoạn **kinh doanh** (cơ hội, báo giá, hồ sơ thầu, hợp đồng) → KDTV. Giai đoạn **triển khai kỹ thuật** (khảo sát, tích hợp, nghiệm thu) → PTDL. Giám sát tiến độ tổng thể → KDTV |
| Bảo hành, bảo trì | KDTV.1.4, PTDL.3.3 | Mặc định KDTV tổ chức nguồn lực; PTDL phối hợp nếu dự án do PTDL triển khai |
| Mua sắm | QTNS.8.5–8.6, KDTV.1.5 | Mua sắm thường xuyên, văn phòng, sự kiện → QTNS. Đấu thầu phục vụ SXKD/dự án → KDTV |
| Truyền thông | QTNS.1.4, KDTV.4 | Nội bộ, văn hóa doanh nghiệp → QTNS. Bên ngoài, báo chí, thương hiệu → KDTV |
| Đối ngoại / hợp tác | QTNS.10.8, CLSHTT.2.1 | Quan hệ công tác với Tập đoàn, đơn vị VNPT; lễ tân, đoàn khách → QTNS. Hợp tác chiến lược với đối tác ngoài → CLSHTT |
| Khen thưởng | QTNS.4, CLSHTT.7.1 | Thi đua – khen thưởng chung → QTNS. Thưởng sáng kiến, sáng chế, công bố khoa học → CLSHTT, QTNS phối hợp |
| Đào tạo | QTNS.2.4–2.5, NCPT.4.3, KDTV.1.4, PTDL.4.1 | Đào tạo nội bộ chung → QTNS. Nhân lực nghiên cứu AI → NCPT. Kênh bán → KDTV. Khách hàng, đối tác → PTDL |
| Dữ liệu cá nhân, bảo mật | QTNS.5.2, NTAI.4.1–4.2 | Dữ liệu người lao động → QTNS. Hệ thống, sản phẩm, dữ liệu khách hàng, ATTT → NTAI |
| Tài sản | QTNS.8.4, QTNS.10.1, NTAI (chức năng 2) | Tài sản hành chính, văn phòng, kiểm kê → QTNS. Hạ tầng tính toán AI, hệ thống dữ liệu → NTAI quản lý khai thác, QTNS phối hợp kiểm kê |
| Phân tích thị trường | CLSHTT.1.1, KDTV.1.1, KDTV.4.8 | Phục vụ chiến lược → CLSHTT. Phục vụ bán hàng, sản phẩm chủ lực → KDTV |

**Quy tắc chung khi vẫn còn mơ hồ**
1. Văn bản yêu cầu **báo cáo tổng hợp chung toàn Công ty** (tình hình SXKD, hoạt động, kết quả thực hiện chỉ đạo) → QTNS xử lý chính phần tổng hợp (QTNS.7.1); các đơn vị liên quan phối hợp cung cấp số liệu. Báo cáo **chuyên đề** (SHTT, chất lượng sản phẩm, ATTT…) thì đơn vị phụ trách lĩnh vực đó xử lý chính, không áp quy tắc này.
2. Văn bản **chỉ đạo chung "các đơn vị" của Công ty** → đơn vị phụ trách lĩnh vực của nội dung chỉ đạo xử lý chính (đầu mối đôn đốc, tổng hợp); các đơn vị phải thực hiện là Phối hợp; đơn vị chỉ cần nắm thông tin là Xem để biết. "Các đơn vị" trong văn bản của Tập đoàn là các đơn vị của VNPT, không phải các đơn vị trực thuộc VNPT AI.
3. Văn bản về **quy trình nội bộ** của một lĩnh vực → đơn vị phụ trách lĩnh vực đó xử lý chính; quy trình phát triển – vận hành sản phẩm nói chung → CLSHTT (CLSHTT.4.3).
4. Không xác định được → vai trò "Trình lãnh đạo", độ tin cậy "Thấp", nêu 2 phương án khả dĩ nhất.

## 7. Ví dụ phân loại (minh họa)

> Các văn bản dưới đây là ví dụ giả định để minh họa cách áp dụng, không phải văn bản thật.

| Văn bản đến (trích yếu) | Xử lý chính | Phối hợp | Xem để biết | Căn cứ |
|---|---|---|---|---|
| Tập đoàn đề nghị báo cáo kết quả SXKD 9 tháng và kế hoạch quý IV | QTNS | KDTV, các Trung tâm | — | QTNS.7.1, QTNS.8.2, QTNS.9.13 |
| Bộ Y tế đề nghị VNPT tư vấn giải pháp AI hỗ trợ chẩn đoán hình ảnh | KDTV | PTDL, NCPT | SPTN | KDTV.2.1; PTDL.2.1; NCPT.1.1 |
| Cục Sở hữu trí tuệ thông báo kết quả thẩm định đơn đăng ký sáng chế | CLSHTT | NCPT | — | CLSHTT.5.2; NCPT.2.2 |
| Cục An toàn thông tin cảnh báo lỗ hổng trên nền tảng container | NTAI | SPTN | — | NTAI.4.1; NTAI.3.2; SPTN.4.2 |
| VNPT tỉnh phản ánh khách hàng không sử dụng được dịch vụ eKYC | SPTN (xử lý sự cố) | NTAI, KDTV (phản hồi khách hàng) | CLSHTT | SPTN.4.1; KDTV.5.1 |
| Đảng ủy Tập đoàn hướng dẫn kiểm điểm, đánh giá đảng viên cuối năm | QTNS | — | Tất cả đơn vị (chi bộ) | QTNS.6.1, QTNS.6.8 |
| Trường Đại học đề nghị ký thỏa thuận hợp tác đào tạo và nghiên cứu AI | CLSHTT | NCPT, QTNS (thẩm định MOU) | — | CLSHTT.2.3; NCPT.4.1; QTNS.7.5 |
| Ban tổ chức AI Expo mời tham gia gian hàng triển lãm | KDTV | SPTN, QTNS (mua sắm, thủ tục) | — | KDTV.4.7; QTNS.8.5 |

## 8. Mẫu kết quả iWork trả về

```markdown
### Đề xuất chuyển tiếp văn bản

**Văn bản:** <số/ký hiệu> — <trích yếu>
**Lĩnh vực nhận diện:** <lĩnh vực 1>, <lĩnh vực 2>
**Độ tin cậy:** Cao | Trung bình | Thấp

| Vai trò | Đơn vị | Người nhận | Nội dung cần làm | Căn cứ |
|---|---|---|---|---|
| Xử lý chính | <tên đơn vị> | <họ tên – chức danh> hoặc "chưa có người nhận" | <việc cụ thể> | <mã nhiệm vụ> |
| Phối hợp | ... | ... | ... | ... |
| Xem để biết | ... | ... | — | ... |

**Thời hạn:** <hạn xử lý nếu có>
**Lưu ý:** <điểm mơ hồ, đề xuất trình lãnh đạo, dữ liệu nhân sự còn thiếu>
```

Dạng JSON (khi cần tích hợp):

```json
{
  "document": { "number": "", "summary": "", "deadline": null },
  "domains": [""],
  "confidence": "high | medium | low",
  "assignments": [
    {
      "role": "xu_ly_chinh | phoi_hop | xem_de_biet | trinh_lanh_dao",
      "unitCode": "QTNS | CLSHTT | KDTV | NCPT | NTAI | PTDL | SPTN",
      "recipient": { "name": null, "title": null, "eofficeAccount": null },
      "action": "",
      "basis": ["QTNS.7.1"]
    }
  ],
  "notes": ""
}
```

**Câu lệnh mẫu để thử nghiệm với iWork** (khi không dùng skill phân loại văn bản eOffice):

> Đọc toàn bộ tài liệu chức năng nhiệm vụ đơn vị VNPT AI này. Với văn bản eOffice đính kèm, hãy phân loại vai trò Xử lý chính / Phối hợp / Xem để biết cho các đơn vị của VNPT AI theo đúng quy trình ở mục 1 và quy tắc ở mục 6, chọn người nhận theo bảng lãnh đạo, rồi trả kết quả theo mẫu ở mục 8. Không tự chuyển văn bản, chỉ đề xuất.

## 9. Phụ lục — Nguồn và ghi chú làm sạch dữ liệu

**Tệp nguồn** (lưu nội bộ tại `docs/00-icowork/13-data-hub`, không đưa lên URL):

| Mã | Tệp |
|---|---|
| QTNS | `Quyết_định_thành_lập_Ban_Quản_trị_và_Nhân_sự_13012026_2.docx` |
| CLSHTT | `Quyết_định_thành_lập_Ban_Chiến_lược_và_Sở_hữu_trí_tuệ_13012026.docx` |
| KDTV | `Quyết_định_thành_lập_Ban_Kinh_doanh_và_Tư_vấn_Công_nghệ_cao_13012026.docx` |
| NCPT | `Quyết_định_thành_lập_Trung_tâm_Nghiên_cứu_và_Phát_triển_công_nghệ.docx` |
| NTAI | `Quyết_định_thành_lập_Trung_tâm_Nền_tảng_AI_13012026.docx` |
| PTDL | `Quyết_định_thành_lập_Trung_tâm_Phân_tích_dữ_liệu_và_Ứng_dụng_AI.docx` |
| SPTN | `Quyết_định_thành_lập_Trung_tâm_Sản_phẩm_&_Trải_nghiệm_xuất_sắc_13012026.docx` |

**Dữ liệu lãnh đạo** (mục 3.2 và bảng "Lãnh đạo đơn vị"): sheet "Lãnh đạo đơn vị" do team nhân sự điền, nhận ngày 20/10/2026. Tài khoản eOffice dùng chính email. Lĩnh vực phụ trách của phần lớn cấp phó còn trống; vị trí không có người đã bỏ khỏi bảng.

**Tình trạng văn bản nguồn**: cả 7 tệp là bản dự thảo/bản chưa điền số — số quyết định, ngày ký và số eOffice còn để trống ("Số: /QĐ-VNPT AI-QTNS", "ngày … tháng 01 năm 2026").

**Đã làm sạch**
- Gộp phần "Quyền hạn" và "Trách nhiệm" (gần như giống nhau ở 7 đơn vị) vào mục 5.0; giữ riêng phần khác biệt của KDTV và 4 Trung tâm.
- Đánh mã nhiệm vụ `ĐƠN_VỊ.nhóm.mục` để iWork trích dẫn căn cứ.
- Sửa lỗi gõ: "Trưởng Ban Ban …" → "Trưởng Ban …"; "chịu chịu trách nhiệm" → "chịu trách nhiệm"; "về việc về việc" → "về việc"; "khen hưởng" → "khen thưởng"; "các đơn Công ty" → "các đơn vị"; "DevSecOps( CI/CD )" → "DevSecOps (CI/CD)"; "Trưởng Chiến lược và Sở hữu trí tuệ" → "Trưởng Ban Chiến lược và Sở hữu trí tuệ".
- Tách câu bị dính: "…được giao cho Tổ chức lễ tân…" (QTNS.10.1); "…khung công nghệ AI quốc gia.Điều 3. Chuyển giao…" (NCPT.2.3 / NCPT.3); "…khắc phục sự cố;- Thiết lập…" (SPTN.4.1 / 4.2).
- Gộp 2 ý trùng trong nhóm Văn thư (QTNS.11) về "thực hiện văn thư, lưu trữ, quản lý con dấu, hướng dẫn các đơn vị" vào QTNS.11.1–11.2.
- Rút gọn câu chữ nhưng giữ nguyên phạm vi nhiệm vụ.

**Khác biệt tên gọi cần lưu ý**
- Tên tệp "Trung tâm Nghiên cứu và Phát triển công nghệ" — tên chính thức trong QĐ: "Trung tâm Nghiên cứu và Phát triển công nghệ **AI**".
- Tên tệp "Trung tâm Phân tích dữ liệu và Ứng dụng AI" — tên chính thức trong QĐ: "… Ứng dụng AI **đa ngành**".
- KDTV dùng chức danh **Giám đốc Ban / Phó Giám đốc Ban**, khác 2 Ban còn lại (**Trưởng Ban / Phó Trưởng Ban**).
