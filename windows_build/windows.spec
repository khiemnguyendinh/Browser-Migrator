# PyInstaller Windows Spec File
# This is a template for the Windows build process

a = Analysis(
    ['src/cpm/m09_gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[('src/cpm/m09_gui/web', 'cpm/m09_gui/web')],
    hiddenimports=['cpm', 'cpm.m09_gui', 'cpm.m09_gui.app'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChromiumBrowserMigratorWin',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChromiumBrowserMigratorWin',
)
