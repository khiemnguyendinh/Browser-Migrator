# Chromium Profile Migrator (CPM)

**Project Codename:** CPM
**Owner:** Khiêm
**Strategy:** Phase A (CLI MVP) → Phase C (Open-Source GUI Utility)
**Tech Stack Phase A:** Python 3.11+ / Click / SQLAlchemy / pytest
**Target Platform:** macOS 12+ (Apple Silicon + Intel)
**Last Updated:** 2026-05-01

## Cấu trúc thư mục dự án

```
CPM/
├── README.md                          # File này — tổng quan dự án
├── 01_Business_Analysis/              # Phân tích nghiệp vụ
│   ├── BRD_Business_Requirements.md
│   ├── User_Personas_Use_Cases.md
│   └── Success_Metrics_KPI.md
├── 02_Technical_Architecture/         # Kiến trúc kỹ thuật
│   ├── System_Architecture.md
│   ├── Data_Flow_Diagram.md
│   └── Security_Threat_Model.md
├── 03_Work_Breakdown/                 # Phân rã công việc
│   ├── WBS_Work_Breakdown_Structure.md
│   ├── Task_Assignment_Matrix.md
│   └── Timeline_Milestones.md
├── 04_Module_Specs/                   # Đặc tả từng module
│   ├── M01_Browser_Detector.md
│   ├── M02_Profile_Reader.md
│   ├── M03_Keychain_Decryptor.md
│   ├── M04_Data_Transformer.md
│   ├── M05_Profile_Writer.md
│   ├── M06_CLI_Interface.md
│   ├── M07_Backup_Rollback.md
│   └── M08_Logger_Telemetry.md
├── 05_Coordination/                   # Phối hợp Claude Code + Antigravity
│   ├── Claude_Code_Brief.md           # Brief cho Claude Code (Tech Lead)
│   ├── Antigravity_Brief.md           # Brief cho Antigravity (Developer)
│   ├── Handoff_Protocol.md
│   └── Code_Review_Checklist.md
└── 06_Standards/                      # Tiêu chuẩn dự án
    ├── Coding_Standards.md
    ├── Git_Workflow.md
    └── Testing_Strategy.md
```

## Quick Start

1. Đọc `01_Business_Analysis/BRD_Business_Requirements.md` để nắm bối cảnh nghiệp vụ.
2. Đọc `02_Technical_Architecture/System_Architecture.md` để hiểu kiến trúc tổng thể.
3. Đọc `03_Work_Breakdown/Task_Assignment_Matrix.md` để biết ai làm gì.
4. Claude Code đọc `05_Coordination/Claude_Code_Brief.md`.
5. Antigravity đọc `05_Coordination/Antigravity_Brief.md`.

## Phân chia vai trò

- **Claude Code (Tech Lead — 60% việc khó):** Architecture, core logic, security-critical modules, code review.
- **Antigravity (Developer — 40% thực thi):** Implementation chi tiết theo spec, unit tests, documentation, CLI polish.

## Phase A — Mục tiêu MVP (2 tuần)

CLI tool chuyển toàn bộ profile từ Chromium browser A → B trên macOS:
- Bookmarks, History, Autofill, Extensions list
- Cookies (giữ nguyên session)
- Saved Passwords (qua macOS Keychain)
- Profile preferences

**Success Criteria:** Migrate Chrome → Edge thành công 100%, user đăng nhập lại Gmail/Facebook không cần nhập mật khẩu.
