# Chromium Browser Migrator (CPM)

**Chromium Browser Migrator (CPM)** is a powerful, secure, and seamless utility for users to transfer their browsing data between different Chromium-based browsers across **macOS and Windows**.

## 🌟 Features

Easily migrate your digital life between **Chrome, Edge, Cốc Cốc, Brave, and Comet** with selective data transfer:

- 🔐 **Passwords**: Securely transfer saved logins.
- 🍪 **Cookies**: Move session data and preferences.
- 🔖 **Bookmarks**: Transfer your curated list of sites.
- 🕒 **History**: Keep your browsing timeline intact.
- ✍️ **Auto Fill**: Migrate addresses and form data.

## 🛡️ Security First

Your privacy and security are our top priorities:

- **100% Offline**: All decryption and migration processes happen locally on your machine.
- **Zero Server Interaction**: No data is ever sent to any external server or intermediate cloud.
- **Native OS Integration**: 
  - **macOS**: Utilizes the native Local Keychain for secure data decryption.
  - **Windows**: Utilizes the Windows Data Protection API (DPAPI) for secure decryption.
- **Safety Net**: Automated backups are created before any write operation, allowing for instant rollback.

## 🚀 Getting Started

### Interfaces
CPM provides two ways to interact with the tool:
1. **GUI**: A modern, intuitive interface for a guided migration experience.
2. **CLI**: A fast, command-line interface for power users.

### Usage (Developer/Manual)
**Running the GUI:**
```bash
# Using the CLI entry point
cpm gui
```

**Running the CLI Migration:**
```bash
cpm migrate --from <browser_a> --to <browser_b>
```

## 🛠 Build Instructions

### For macOS (.app)
```bash
# Sequence: PyInstaller -> Resource Injection -> Xattr Clean -> Codesign
python3 -m PyInstaller --clean --noconfirm "Chromium Browser Migrator.spec"
cp Credits.html "dist/Chromium Browser Migrator.app/Contents/Resources/Credits.html"
xattr -cr "dist/Chromium Browser Migrator.app"
codesign --force --deep --sign - "dist/Chromium Browser Migrator.app"
```

### For Windows (.exe Portable)
Run the dedicated build script on a Windows machine:
```bash
python windows_build/build_win.py
```

## 📄 License
Internal Project - Phase A (MVP)
