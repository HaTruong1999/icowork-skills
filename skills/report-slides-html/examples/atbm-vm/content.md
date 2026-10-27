# NGUỒN 1: Báo_cáo_tiến_độ_triển_khai_ATBM_hệ_thống_VM_v2.pdf

- Loại: pdf · Số trang/slide: 7
- Title: Báo cáo tiến độ triển khai ATBM hệ thống VM
- Author: Vu Duy Du
- Creator: Microsoft® PowerPoint® for Microsoft 365
- Producer: Microsoft® PowerPoint® for Microsoft 365
- CreationDate: Sat Oct 24 19:24:52 2026 +07
- ModDate: Sat Oct 24 19:24:52 2026 +07
- Custom Metadata: no
- Metadata Stream: yes
- Tagged: yes
- UserProperties: no
- Suspects: no
- Form: none
- JavaScript: no
- Pages: 7
- Encrypted: no
- Page size: 960 x 540 pts
- Page rot: 0
- File size: 169132 bytes
- Optimized: no
- PDF version: 1.7

## Trang 1

                                           01
                                           Danh mục VM
VNPT NET · CHUYÊN ĐỀ 05



Báo cáo tiến độ triển khai
                                           02
                                           Đổi mật khẩu quản trị


an toàn, bảo mật hệ                        03
                                           Sao lưu, khôi phục VM


thống VM                                   04
                                           Giải pháp an toàn, bảo mật

Hệ thống máy ảo (VM) do VNPT Net quản lý
                                           05
 Ngày 24/10/2026                           Thông điệp, kiến nghị

## Trang 2

01 / 04 · DANH MỤC VM

Rà soát, chuẩn hóa danh mục VM
Hoàn thành rà soát; đã cập nhật, gửi danh mục đối soát cho VNPT-IT trên hệ thống quản lý dự án.




   496                                                      450                                       46
   VM VNPT-IT bàn giao                                      VM do VNPT Net quản lý (90,73%)           VM ngoài phạm vi quản lý / đề xuất OFF




   Phân loại 450 VM theo loại hệ thống                                                Phân loại 46 VM còn lại

     171 Viễn thông            279 Công nghệ thông tin
                                                                                      13      VM thuộc VNPT-IT

                                                                                      02      VM thuộc VNPT Media
   38% · CPE/ACS, Mentor          62% · OSS/ERP, CSDL (TT CĐS), báo cáo,
   RAN, NMS, chống spam,          web, giám sát                                       31      VM không còn nhu cầu, đề xuất tắt (OFF)
   USSD, DNS
   Sơ bộ theo tên VM; 23 VM cần đơn vị chủ quản xác nhận.




  Tiếp theo →     Phối hợp VNPT-IT xác nhận danh mục và thực hiện tắt 31 VM sau khi hoàn tất đánh giá ảnh hưởng.

## Trang 3

01 / 04 · DANH MỤC VM · CHI TIẾT

Phân loại 450 VM: viễn thông và công nghệ thông tin
   Hệ thống viễn thông
   38% · NTL 127 · 30 PHG 44                           171                Hệ thống công nghệ thông tin
                                                                          62% · NTL 261 · 30 PHG 18                      279
   Quản lý CPE/ACS, DHCP băng rộng                            48          Ứng dụng OSS/ERP, CSDL, nền tảng (TT CĐS)          200
   Phân tích vô tuyến RAN (Mentor)                            30          Báo cáo, phân tích, KPI, web, cổng thông tin         47
   NMS giám sát thiết bị mạng                                 28          Công cụ giám sát, máy trạm vận hành                  11
   Chống spam SMS/thoại                                       25          Hạ tầng dùng chung: FTP, backup, API                 10
   DNS dịch vụ, DNS/DHCP Infoblox                              8          Công cụ hỗ trợ vận hành: Interconnect, PCRF/HLR tools, 8
   Hội nghị truyền hình                                        8          OMC, SMS tracking
                                                                          Phát hiện trạm BTS giả                                3
   Firewall, chống DDoS, RPKI, SD-WAN                          7
   USSD Gateway                                                6
   MMSC, IMS, lưu trữ CDR OCS                                  6
   PTDL mạng lưới (TTDL), chặn lọc cuộc gọi                    5



Ghi chú: phân loại sơ bộ theo tên VM và đơn vị chủ quản; 23 VM (KPI, PTML, RPNEW, GSTT, CLM) cần đơn vị xác nhận.

## Trang 4

02 / 04 · TÀI KHOẢN QUẢN TRỊ

Triển khai đổi mật khẩu quản trị

  505                                                 Kết quả thực hiện
                                                       • Hoàn thành thống kê 505 tài khoản quản trị trên 450 VM.
                                                       • Đã đổi mật khẩu quản trị cho 150 VM; tiếp tục triển khai 300 VM còn lại.
  Tài khoản quản trị đã thống kê trên 450
  VM

                                                      Khó khăn, rủi ro
  Tiến độ đổi mật khẩu VM                              • Một số hệ thống viễn thông cần thống nhất phương án với đối tác, nhà cung


  33,33%
                                                         cấp thiết bị trước khi thay đổi.
                                                       • Đổi mật khẩu cần thực hiện trong khung giờ thấp điểm, có phương án kiểm
                                                         tra và khôi phục, tránh ảnh hưởng dịch vụ.

  150/450 VM đã hoàn thành · còn 300 VM




 Tiếp theo →     Phân nhóm VM theo mức độ rủi ro, thống nhất lịch triển khai và đẩy nhanh tiến độ đổi mật khẩu.

## Trang 5

03 / 04 · SAO LƯU, KHÔI PHỤC


Triển khai sao lưu, khôi phục VM
                                                                    Theo quy trình VHKT hiện hành; sao lưu về dung lượng VNPT-IT cấp
  Backup mức cấu hình                         Hoàn thành
                                                                    cho VNPT Net và phân vùng lưu trữ nội bộ VNPT Net.

  Snapshot toàn bộ VM – Site 30
                                              Hoàn thành            Đã phối hợp hoàn thành trên hệ thống backup VNPT-IT.
  PHG

                                                                    Snapshot trên hệ thống backup VNPT-IT; chưa hoàn thành do thiếu
  Snapshot toàn bộ VM – Site NTL             Chưa hoàn thành
                                                                    dung lượng lưu trữ.

                                                                    Đang phối hợp đối tác đánh giá khả năng hỗ trợ snapshot và rủi ro ảnh
  Hệ thống viễn thông đặc thù                 Đang đánh giá
                                                                    hưởng dịch vụ.


   Vướng mắc trọng tâm                                               Kiến nghị VNPT-IT
    • Sao lưu: chưa đủ dung lượng lưu trữ phục vụ sao lưu tập         • Ưu tiên backup mức snapshot cho 171 VM hệ thống viễn thông.
      trung tại tenant Backup.                                        • Cấp đủ 300 TB dung lượng lưu trữ đã phân bổ cho VNPT Net.
    • Khôi phục: hệ thống viễn thông của VNPT Net có tính             • Hỗ trợ sao lưu tập trung, thay thế lưu trữ phân tán qua OAM.
      đặc thù, việc cài đặt lại cần sự phối hợp của đối tác.          • VNPT Net đã có văn bản gửi VNPT-IT về nhu cầu dung lượng.




Mục tiêu: nâng cao an toàn dữ liệu, khả năng quản lý và khôi phục hệ thống khi xảy ra sự cố.

## Trang 6

04 / 04 · GIẢI PHÁP ATBM

Triển khai các giải pháp an toàn, bảo mật
Tiếp nhận khuyến nghị của VNPT-IT về Hardening, rà soát mã độc và triển khai các biện pháp tăng cường ATBM.


    Hoàn thành                                                                             Trọng tâm thời gian tới
   Chuyển đổi, cấu hình DNS Tập đoàn; ngắt card mạng kết nối Internet không cần            1 Hoàn thành kết nối SIEM và đổi mật khẩu
   thiết theo thiết kế.                                                                      cho 300 VM còn lại.

                                                                                           2 Tiếp tục Hardening, rà soát và đóng
    Đang triển khai                                                                          các port không cần thiết.
   Đổi mật khẩu (150/450 VM); kết nối SIEM (150/450 VM); rà soát, đóng các                 3 Phối hợp đối tác đánh giá, thử nghiệm
   cổng dịch vụ không sử dụng theo thiết kế.                                                 EDR/EPP trước khi triển khai diện rộng.

    Đang đánh giá

   Cài đặt EDR/EPP trên các hệ thống viễn thông; đánh giá tính tương thích và
   nguy cơ ảnh hưởng đến thiết bị, dịch vụ mạng lưới.




Nguyên tắc: bảo đảm an toàn, bảo mật nhưng không làm gián đoạn hoạt động của các hệ thống viễn thông.

## Trang 7

THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO

Kết quả chính và kiến nghị

  450                               505                               33,33%                            300 TB
  VM đã chuẩn hóa danh mục          Tài khoản quản trị đã thống kê    Tiến độ đổi mật khẩu, kết nối     Dung lượng Backup kiến nghị
                                                                      SIEM                              VNPT-IT cấp đủ



Đã đạt được                                                          Kiến nghị
Hoàn thành chuẩn hóa danh mục 450 VM do VNPT Net quản lý,            VNPT-IT sớm cấp đủ 300 TB dung lượng Backup, đồng thời phối
thống kê 505 tài khoản quản trị và sao lưu cấu hình các hệ thống.    hợp đánh giá các giải pháp EDR/EPP và snapshot trên hệ thống
Tiến độ đổi mật khẩu và kết nối SIEM đạt 33,33%; đã hoàn thành       viễn thông đặc thù để bảo đảm triển khai an toàn, không ảnh hưởng
snapshot tại site 30 PHG, site NTL còn vướng dung lượng lưu trữ.     dịch vụ.
