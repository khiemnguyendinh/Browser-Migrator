# System Architecture

## 1. Architecture Overview

CPM follows a **Layered Modular Architecture** với 8 modules độc lập, giao tiếp qua well-defined interfaces.

```
┌─────────────────────────────────────────────────┐
│            M06: CLI Interface (Click)           │
│       (User Input / Output / Progress)          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Orchestrator (Migration Engine)         │
│   (Phối hợp các modules, transaction control)   │
└──┬──────┬──────┬──────┬──────┬──────┬──────────┘
   │      │      │      │      │      │
┌──▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐
│ M01 │ │M02 │ │M03 │ │M04 │ │M05 │ │M07 │
└─────┘ └────┘ └────┘ └────┘ └────┘ └────┘
                                      │
                              ┌───────▼────────┐
                              │  M08: Logger   │
                              └────────────────┘
```

## 2. Module Responsibilities

### M01 — Browser Detector
- Scan macOS để tìm các Chromium browser đã cài.
- Đường dẫn chuẩn: `~/Library/Application Support/{BrowserName}/`.
- Output: `BrowserInfo` object với metadata.

### M02 — Profile Reader
- Đọc profile data từ browser nguồn.
- Parse SQLite databases (History, Login Data, Cookies, Web Data).
- Parse JSON files (Bookmarks, Preferences, Local State).
- Output: `ProfileSnapshot` object (in-memory representation).

### M03 — Keychain Decryptor (Most Critical)
- Lấy encryption key từ macOS Keychain qua `security` CLI hoặc `keyring` lib.
- Decrypt cookies và passwords blob (AES-128-CBC trên macOS).
- Yêu cầu user authentication (Touch ID / password).

### M04 — Data Transformer
- Adapter pattern: chuyển đổi format giữa các browser versions.
- Xử lý edge cases (Brave's BAT data, Cốc Cốc's custom fields).
- Validate data integrity.

### M05 — Profile Writer
- Encrypt lại data với key của browser đích.
- Ghi vào SQLite + JSON files của browser đích.
- Atomic writes: dùng temp file + rename.

### M06 — CLI Interface
- Built on Click framework.
- Interactive prompts, progress bars (rich/tqdm).
- Subcommands: list, inspect, migrate, history, rollback, cleanup, doctor.

### M07 — Backup & Rollback
- Tar.gz toàn bộ profile folder trước khi ghi.
- Lưu vào `~/CPM_Backups/{timestamp}/`.
- Restore: untar + replace.

### M08 — Logger & Telemetry
- Structured logging (JSON format).
- Sanitize sensitive data trước khi log.
- Phase A: log local. Phase C: optional anonymous telemetry.

## 3. Data Flow — Migration Process

```
┌──────────────┐
│ User Command │ "cpm migrate --from chrome --to edge"
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ 1. Detect (M01)                  │
│    Scan installed browsers       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 2. Validate                      │
│    - Browsers closed?            │
│    - Disk space available?       │
│    - User permissions?           │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 3. Backup Target (M07)           │
│    tar.gz → ~/CPM_Backups/       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 4. Read Source (M02 + M03)       │
│    - SQLite databases            │
│    - Decrypt cookies/passwords   │
│    - Build ProfileSnapshot       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 5. Transform (M04)               │
│    Adapt format source → target  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 6. Write Target (M05 + M03)      │
│    - Encrypt with target key     │
│    - Atomic write to files       │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 7. Verify                        │
│    - Open target DBs             │
│    - Count records               │
│    - Compare checksums           │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ 8. Report (M08)                  │
│    Summary + log file path       │
└──────────────────────────────────┘
```

## 4. Key Technical Decisions

### TD-01: Python over Swift/Node
- **Lý do:** Speed of development, ecosystem rich (sqlite3 built-in, cryptography lib mature).
- **Trade-off:** Phải bundle Python runtime cho Phase C distribution. Sẽ giải quyết bằng PyInstaller.

### TD-02: SQLite via stdlib `sqlite3`
- Không dùng SQLAlchemy ORM cho Phase A (overkill).
- Direct SQL với parameterized queries.
- Phase C có thể nâng cấp nếu cần.

### TD-03: Keychain Access via `security` CLI
- Dùng subprocess gọi `/usr/bin/security` thay vì pyobjc.
- **Lý do:** Đơn giản hơn, không cần native binding, debug dễ.
- **Trade-off:** Performance thấp hơn marginal, nhưng acceptable cho use case này.

### TD-04: Atomic File Operations
- Write to `.tmp` file → fsync → rename to final path.
- Đảm bảo crash giữa chừng không corrupt data.

### TD-05: No Network in Phase A
- Hoàn toàn offline. Tránh complexity của telemetry, update check.
- Phase C sẽ thêm optional telemetry với consent rõ ràng.

## 5. Profile Data Structure (Reference)

### macOS Chromium Browser Locations

```
Chrome:    ~/Library/Application Support/Google/Chrome/
Edge:      ~/Library/Application Support/Microsoft Edge/
Brave:     ~/Library/Application Support/BraveSoftware/Brave-Browser/
Arc:       ~/Library/Application Support/Arc/User Data/
Cốc Cốc:   ~/Library/Application Support/Coccoc/
Comet:     ~/Library/Application Support/Perplexity/Comet/
Vivaldi:   ~/Library/Application Support/Vivaldi/
Opera:     ~/Library/Application Support/com.operasoftware.Opera/
```

### Profile Folder Structure (Common)

```
{Browser}/
├── Local State                 # JSON, contains encryption key (encrypted)
├── Default/                    # Hoặc "Profile 1", "Profile 2"
│   ├── Bookmarks               # JSON
│   ├── Bookmarks.bak
│   ├── History                 # SQLite
│   ├── Login Data              # SQLite (passwords, encrypted)
│   ├── Cookies                 # SQLite (encrypted values)
│   ├── Web Data                # SQLite (autofill, payments)
│   ├── Preferences             # JSON (settings)
│   ├── Secure Preferences      # JSON
│   ├── Extensions/             # Folder
│   ├── Local Storage/          # IndexedDB
│   ├── Session Storage/
│   └── ...
```

### Encryption Scheme (macOS)

```
1. Browser stores encrypted master key in:
   Keychain entry: "{Browser} Safe Storage"

2. Cookie values và passwords encrypted với AES-128-CBC
   Key derived from master key via PBKDF2 (1003 iterations, salt="saltysalt")
   IV = 16 bytes of space (0x20)

3. Encrypted values prefixed với "v10" hoặc "v11" (version marker)
```

## 6. Security Considerations

Xem chi tiết: `Security_Threat_Model.md`.

Tóm tắt:
- **Trust boundary:** User's local machine. Không cross network.
- **Sensitive data handling:** Decrypted passwords/cookies chỉ tồn tại trong RAM, không write disk plaintext.
- **Keychain prompt:** User MUST consent qua system dialog.
- **Backup encryption:** Phase A backup là plaintext tar.gz (đã trong Library protected). Phase C có thể thêm optional encryption.
