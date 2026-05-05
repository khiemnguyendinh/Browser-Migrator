# 📘 Developer Guide - Chromium Browser Migrator (CPM)

This guide provides technical details for developers (Claude Code, Antigravity, OpenCode) to maintain and extend the CPM project across multiple platforms.

## 🛠 Tech Stack
- **Language:** Python 3.11+
- **GUI:** `pywebview` (HTML/JS/CSS frontend with Python backend API)
- **CLI:** `click` & `rich`
- **Database:** `sqlite3` (Chromium Profile data)
- **Security:** 
  - macOS: `security` CLI (Keychain)
  - Windows: `pywin32` (DPAPI)
- **Packaging:** `PyInstaller`

## 🏗 Multi-Platform Architecture
CPM uses a **Factory Pattern** to handle OS-specific differences.

### Platform Detection
The core platform is detected in `src/cpm/core/platform.py` using `platform.system()`.

### Modular Layout
Each platform-sensitive module follows this structure:
`src/cpm/mXX_module/`
├── `base.py` (Interface/Abstract Base Class)
├── `platforms/`
│   ├── `macos.py` (macOS specific implementation)
│   └── `windows.py` (Windows specific implementation)
└── `module.py` (Factory: returns the correct platform instance)

### Platform-Specific Details
| Module | macOS Implementation | Windows Implementation |
|---|---|---|
| **M01 (Detector)** | `~/Library/Application Support` | `%LocalAppData%` |
| **M03 (Keychain)** | `security` CLI $\rightarrow$ Master Key | `DPAPI` $\rightarrow$ Master Key |
| **M07 (Backup)** | `tar.gz` archive | `.zip` archive |

## 🚀 Build & Packaging

### macOS Build (App Bundle)
```bash
# Sequence: PyInstaller -> Resource Injection -> Xattr Clean -> Codesign
python3 -m PyInstaller --clean --noconfirm "Chromium Browser Migrator.spec"
cp Credits.html "dist/Chromium Browser Migrator.app/Contents/Resources/Credits.html"
xattr -cr "dist/Chromium Browser Migrator.app"
codesign --force --deep --sign - "dist/Chromium Browser Migrator.app"
```

### Windows Build (Portable EXE)
Run the build script on a Windows machine:
```bash
python windows_build/build_win.py
```
This will generate a single portable `.exe` in `dist/windows/`.

## ⚠️ Critical Implementation Details

### Database Constraints
Chromium databases have strict `NOT NULL` constraints. When writing to `logins` table:
- Always provide `signon_realm` (usually = `origin_url`).
- Always provide `blacklisted_by_user` (default `0`).
- Always provide `scheme` (default `"password"`).

### macOS Integration
- **About Menu**: `Credits.html` MUST be saved with **UTF-8 with BOM** encoding for native macOS About window support.

## 🗺 Future Roadmap (Phase 2)
- [ ] **Windows Stable Release**: Finalize DPAPI testing.
- [ ] **Installer**: Create `.dmg` (Mac) and `.msi` (Win) installers.
- [ ] **UI Enhancements**: Detailed progress tracking for each migration step.
- [ ] **Telemetry**: Optional anonymous usage stats.
