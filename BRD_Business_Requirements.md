# BRD — Business Requirements Document

**Project:** Chromium Profile Migrator (CPM)
**Phase:** A (Personal Tool / CLI MVP)
**Document Version:** 1.0

## 1. Executive Summary

### 1.1 Bối cảnh
Người dùng macOS thường xuyên cần chuyển đổi giữa các trình duyệt Chromium-based (Chrome, Edge, Brave, Arc, Cốc Cốc, Comet, Vivaldi, Opera). Quá trình chuyển đổi hiện tại bất tiện vì:

- Trình duyệt đích chỉ import được bookmarks và history cơ bản.
- Mật khẩu đã lưu, cookies, session tokens không migrate được.
- Autofill data, payment methods, extensions phải setup lại thủ công.
- Multi-profile users (Default + Profile 1 + Profile 2…) phải làm lại từng profile.

### 1.2 Giải pháp đề xuất
CLI tool chạy native trên macOS, đọc trực tiếp profile data từ browser nguồn và ghi vào browser đích, giữ nguyên 100% trải nghiệm người dùng (đăng nhập sẵn, autofill sẵn, extensions sẵn).

### 1.3 Phạm vi Phase A
- Hỗ trợ migration giữa **5 browser** chính: Chrome, Edge, Brave, Arc, Cốc Cốc.
- CLI command-line, không có GUI.
- Single-machine migration (cùng máy Mac).
- Backup tự động trước khi ghi.

### 1.4 Phạm vi loại trừ (Out of Scope Phase A)
- Cross-machine migration (cloud sync).
- Non-Chromium browser (Safari, Firefox).
- GUI application — sẽ làm ở Phase C.
- Windows/Linux support.

## 2. Business Objectives

| Mã | Mục tiêu | Đo lường |
|---|---|---|
| BO-01 | Tiết kiệm 95% thời gian migrate so với thủ công | < 60 giây cho 1 profile |
| BO-02 | Giữ nguyên 100% session đăng nhập | User không phải nhập lại password |
| BO-03 | Validate khả thi kỹ thuật cho Phase C | Decision gate sau MVP |
| BO-04 | Tạo asset kỹ thuật nội bộ | Reusable cho team Kstudy/SAMA |

## 3. Stakeholders

| Vai trò | Người | Trách nhiệm |
|---|---|---|
| Product Owner | Khiêm | Quyết định scope, ưu tiên features |
| Tech Lead | Claude Code | Architecture, core modules |
| Mid Developer | Antigravity | Implementation M01, M06, M02/M05 theo spec |
| Junior Developer | OpenCode | Implementation M07, M08, M04 adapters đơn giản, tests, docs |
| End User (Phase A) | Khiêm + team Kstudy/SAMA | Sử dụng nội bộ, feedback |

## 4. Functional Requirements

### 4.1 FR-01: Browser Detection
- System phát hiện tự động các Chromium browser đã cài trên máy.
- Hiển thị danh sách các profile có sẵn cho mỗi browser.
- Output: tên browser, version, đường dẫn profile, số lượng profiles.

### 4.2 FR-02: Source Selection
- User chọn browser nguồn và profile cụ thể (ví dụ: Chrome → Default).
- System hiển thị thống kê dữ liệu sẽ migrate (số bookmarks, số passwords, số cookies, dung lượng).

### 4.3 FR-03: Target Selection
- User chọn browser đích.
- Nếu profile đích đã tồn tại, system cảnh báo và yêu cầu xác nhận:
  - **Option 1**: Overwrite (ghi đè, có backup).
  - **Option 2**: Merge (gộp dữ liệu, giữ lại cả hai).
  - **Option 3**: Create new profile (tạo profile mới trên browser đích).

### 4.4 FR-04: Backup & Rollback
- Trước khi ghi, system tự động backup profile đích vào thư mục `~/CPM_Backups/{timestamp}/`.
- Cung cấp lệnh rollback: `cpm rollback {backup_id}`.
- Backup giữ tối thiểu 7 ngày, sau đó user tự xóa hoặc dùng lệnh `cpm cleanup`.

### 4.5 FR-05: Migration Execution
Migrate các loại dữ liệu sau theo thứ tự ưu tiên:

| Mã | Loại dữ liệu | Độ ưu tiên | Phase |
|---|---|---|---|
| FR-05.1 | Bookmarks | P0 | A |
| FR-05.2 | History | P1 | A |
| FR-05.3 | Cookies + Sessions | P0 | A |
| FR-05.4 | Saved Passwords | P0 | A |
| FR-05.5 | Autofill (form data, addresses) | P1 | A |
| FR-05.6 | Payment methods | P2 | A (nếu khả thi) |
| FR-05.7 | Extensions list (chỉ tên + ID) | P1 | A |
| FR-05.8 | Preferences (settings, themes) | P2 | A |
| FR-05.9 | Open tabs | P2 | C |
| FR-05.10 | Browsing history search index | P3 | C |

### 4.6 FR-06: Verification
Sau khi migrate, system tự động verify:
- Đếm số records migrate được vs số records gốc.
- Test mở SQLite databases ở browser đích không lỗi.
- Output report dạng JSON + text summary.

### 4.7 FR-07: Logging
- Log toàn bộ thao tác vào file `~/.cpm/logs/{timestamp}.log`.
- Mức log: DEBUG, INFO, WARN, ERROR.
- Không log sensitive data (passwords, cookies values).

## 5. Non-Functional Requirements

### 5.1 NFR-01: Performance
- Migrate 1 profile (10MB-500MB) trong < 60 giây.
- Memory footprint < 200MB.

### 5.2 NFR-02: Security
- Không gửi dữ liệu qua network (100% local).
- Không lưu cache plaintext của passwords/cookies.
- File backup được set permission 600 (chỉ owner đọc).
- Tool yêu cầu user xác nhận trước mỗi thao tác ghi.

### 5.3 NFR-03: Reliability
- Migration phải atomic: hoặc thành công hoàn toàn, hoặc rollback hoàn toàn.
- Browser đích phải đóng hoàn toàn trước khi migrate (system tự kiểm tra).
- Recovery rate > 99% (rollback luôn khôi phục được).

### 5.4 NFR-04: Usability (CLI)
- Câu lệnh trực quan: `cpm migrate --from chrome --to edge`.
- Interactive mode khi thiếu tham số.
- Progress bar realtime.
- Error message rõ ràng, có hướng dẫn fix.

### 5.5 NFR-05: Compatibility
- macOS 12 (Monterey) trở lên.
- Apple Silicon (M1/M2/M3) + Intel.
- Python 3.11+.

## 6. Constraints & Assumptions

### 6.1 Constraints
- Apple Keychain decryption yêu cầu user xác thực (Touch ID hoặc password) — không thể bypass.
- Mỗi browser update có thể đổi format profile → cần test định kỳ.
- Một số extension sẽ phải user cài lại thủ công (Chrome Web Store policy).

### 6.2 Assumptions
- User có quyền admin trên máy.
- User chấp nhận đóng browser khi migrate.
- Browser nguồn và đích đều cài qua kênh chính thức (không phải build tùy biến).

## 7. Risks

| Mã | Rủi ro | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|---|
| R-01 | Apple Keychain block decryption | Trung bình | Cao | Test sớm tuần 1, có fallback prompt user |
| R-02 | Cookie format khác giữa browser versions | Cao | Trung bình | Migration adapter pattern |
| R-03 | User mất data do bug | Thấp | Nghiêm trọng | Backup bắt buộc, atomic operations |
| R-04 | Browser update phá format | Cao | Thấp | Pin version check, semver compatibility |
| R-05 | Code Antigravity / OpenCode không đạt chuẩn | Trung bình | Trung bình | Code review checklist nghiêm ngặt |
