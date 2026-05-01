# Task Assignment Matrix (RACI)

## Vai trò

- **R** = Responsible (làm việc)
- **A** = Accountable (chịu trách nhiệm cuối)
- **C** = Consulted (hỏi ý kiến)
- **I** = Informed (được thông báo)

## Phase A — RACI Matrix

| Task | Khiêm (PO) | Claude Code (Tech Lead) | Antigravity (Mid Dev) | OpenCode (Junior Dev) |
|---|---|---|---|---|
| **1.0 Project Setup** | A | C | R | I |
| 1.1 Repo init | I | C | R | I |
| 1.2 Python env | I | C | R | I |
| 1.3 Folder structure | I | A | R | I |
| 1.4 Pre-commit hooks | I | C | R | I |
| **2.1 M01 Browser Detector** | I | A | R | I |
| **2.2 M02 Profile Reader** | I | A, R (architect) | R (impl details) | I |
| 2.2.1 SQLite reader skeleton | I | R | C | I |
| 2.2.2 JSON reader skeleton | I | C | R | I |
| 2.2.3 ProfileSnapshot dataclass | I | R | I | I |
| 2.2.4 Unit tests | I | C | C | R |
| **2.3 M03 Keychain Decryptor** | C (security review) | **A, R (SOLE)** | I (no access) | I (no access) |
| 2.3.1 Keychain CLI wrapper | I | R | I | I |
| 2.3.2 Cryptography logic | I | R | I | I |
| 2.3.3 Memory hygiene | I | R | I | I |
| 2.3.4 Tests | I | R | I | I |
| **2.4 M04 Data Transformer** | I | A, R (architect) | R (complex adapters) | R (simple adapters) |
| 2.4.1 Adapter base class | I | R | I | I |
| 2.4.2 Chrome adapter | I | C | R | I |
| 2.4.3 Edge adapter | I | C | R | I |
| 2.4.4 Brave adapter | I | C | R | I |
| 2.4.5 Cốc Cốc adapter | I | C | R | I |
| 2.4.6 Arc adapter | I | C | R | I |
| **2.5 M05 Profile Writer** | I | A, R (architect) | R (impl) | I |
| 2.5.1 Atomic write logic | I | R | C | I |
| 2.5.2 Process detection | I | C | R | I |
| **2.6 M07 Backup & Rollback** | I | A | C | R |
| **2.7 M08 Logger** | I | A | C | R |
| **3.0 Orchestrator** | I | **A, R (SOLE)** | I (review only) | I |
| **4.0 M06 CLI** | C (UX feedback) | A | R | I |
| **5.0 Testing** | C (UAT) | A | C | R |
| 5.1 Unit tests | I | C | C | R |
| 5.2 Integration tests | C | A | C | R |
| 5.3 Security tests | C | R | C | I |
| 5.4 Performance benchmark | I | A | R | I |
| **6.0 Documentation** | C | A | C | R |
| **Code Review (mọi PR)** | I | **A, R** | I | I |
| **Phase A Retrospective** | A, R | C | C | I |
| **Phase C Decision** | A, R | C | I | I |

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
