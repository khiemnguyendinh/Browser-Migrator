# Task Assignment Matrix (RACI)

## Vai trò

- **R** = Responsible (làm việc)
- **A** = Accountable (chịu trách nhiệm cuối)
- **C** = Consulted (hỏi ý kiến)
- **I** = Informed (được thông báo)

## Phase A — RACI Matrix

| Task | Khiêm (PO) | Claude Code (Tech Lead) | Antigravity (Mid Dev) | OpenCode (Junior Dev) | Status |
|---|---|---|---|---|---|
| **1.0 Project Setup** | A | C | R | I | ✅ DONE |
| **2.1 M01 Browser Detector** | I | A | R | I | ✅ DONE |
| **2.2 M02 Profile Reader** | I | A, R (architect) | R (impl details) | I | ✅ DONE |
| **2.3 M03 Keychain Decryptor** | C (security review) | **A, R (SOLE)** | I (no access) | I (no access) | ✅ DONE |
| **2.4 M04 Data Transformer** | I | A, R (architect) | R (complex adapters) | R (simple adapters) | ✅ DONE |
| **2.5 M05 Profile Writer** | I | A, R (architect) | R (impl) | I | ✅ DONE |
| **2.6 M07 Backup & Rollback** | I | A | C | R | ✅ DONE |
| **2.7 M08 Logger** | I | A | C | R | ✅ DONE |
| **2.8 M09 GUI Interface** | C (UX feedback) | A | R | I | ✅ DONE |
| **3.0 Orchestrator** | I | **A, R (SOLE)** | I (review only) | I | ✅ DONE |
| **4.0 M06 CLI** | C (UX feedback) | A | R | I | ✅ DONE |
| **5.0 Testing** | C (UAT) | A | C | R | ✅ DONE |
| **6.0 Packaging & Docs** | C | A | C | R | ✅ DONE |


## Module Ownership

### Modules Claude Code SOLE OWNER (Critical Path)

| Module | Lý do |
|---|---|
| M03 Keychain Decryptor | Security-critical, 1 bug = leak passwords |
| Orchestrator | State machine + transaction logic, cần kinh nghiệm hệ thống |

**Antigravity KHÔNG được chạm vào 2 module này** trừ khi chỉ đọc để hiểu.

### Modules Claude Code ARCHITECT — Antigravity IMPLEMENT

| Module | Claude Code làm | Antigravity làm |
|---|---|---|
| M02 Profile Reader | Thiết kế interface, dataclasses, edge cases | Implement methods, parsing, tests |
| M04 Data Transformer | Adapter pattern, base class, transform contracts | Complex adapters (Antigravity), Simple adapters (OpenCode) |
| M05 Profile Writer | Atomic write strategy, error handling design | SQL writes, file ops, process detection |

### Modules Antigravity & OpenCode SOLE OWNER

| Module | Lý do |
|---|---|
| M01 Browser Detector | Straightforward, well-defined inputs/outputs (Antigravity) |
| M07 Backup & Rollback | tar.gz + metadata, no security-critical logic (OpenCode) |
| M08 Logger | Sanitization rules được Claude Code define, impl đơn giản (OpenCode) |
| M06 CLI Interface | Click framework, presentation layer (Antigravity) |

## Communication Cadence

### Daily (15 phút async)
- Antigravity và OpenCode post status update vào `05_Coordination/daily_log.md`:
  - Hôm qua làm gì
  - Hôm nay làm gì
  - Blockers
- Claude Code phản hồi blockers trong 4 giờ.

### Code Review SLA
- Antigravity/OpenCode submit PR → Claude Code review trong 24 giờ.
- Critical modules (M02, M04, M05): review chi tiết line-by-line.
- Non-critical: review pattern + tests.

### Mid-week sync (Wednesday)
- 30 phút Khiêm + Claude Code review tiến độ vs WBS.
- Adjust priorities nếu trễ.

### End-of-phase
- Demo full E2E migration cho Khiêm.
- Retrospective: what worked, what didn't, decisions for Phase C.

## Escalation Path

| Tình huống | Escalate to |
|---|---|
| Antigravity / OpenCode stuck > 2 giờ | Claude Code |
| Claude Code không quyết định được architecture | Khiêm (PO) |
| Conflict giữa team members | Khiêm (PO) |
| Bug security | STOP work, Claude Code + Khiêm review ngay |
| Trễ milestone > 1 ngày | Khiêm review WBS, có thể cắt scope |

## Definition of Done (per Module)

Một module được coi là **DONE** khi:

1. Code passes lint (ruff, black) và type check (mypy).
2. Unit tests coverage ≥ 80%.
3. Integration test pass (nếu module integrate với module khác).
4. Documentation strings đầy đủ cho public APIs.
5. Code review approved bởi Claude Code.
6. Merged vào main branch.

## Definition of Done (Phase A)

Phase A **DONE** khi:

1. Tất cả modules đạt DoD.
2. E2E test pass cho 4 cặp browser P0 (Chrome↔Edge, Chrome↔Brave, Edge↔Cốc Cốc, Brave↔Cốc Cốc).
3. Security tests ST-01 → ST-07 pass.
4. README user guide đầy đủ.
5. Khiêm UAT pass.
6. Phase A retrospective hoàn thành.
7. Phase C go/no-go decision recorded.
