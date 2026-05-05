# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/cpm/m09_gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[('src/cpm/m09_gui/web', 'cpm/m09_gui/web')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Chromium Browser Migrator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Chromium Browser Migrator',
)
app = BUNDLE(
    coll,
    name='Chromium Browser Migrator.app',
    icon='app_icon.png',
    bundle_identifier='com.kstudy.cpm',
    info_plist={
        'CFBundleName': 'Chromium Browser Migrator',
        'CFBundleDisplayName': 'Chromium Browser Migrator',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2026 Kstudy Academy. All rights reserved.',
    }
)
