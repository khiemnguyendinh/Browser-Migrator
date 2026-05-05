import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_windows_app():
    print("🚀 Starting Windows Build Process...")
    
    # 1. Clean previous builds
    dist_path = Path("dist/windows")
    build_path = Path("build/windows")
    if dist_path.exists(): shutil.rmtree(dist_path)
    if build_path.exists(): shutil.rmtree(build_path)

    # 2. PyInstaller command for Windows
    # We use --onefile for a truly portable .exe
    args = [
        'src/cpm/m09_gui/app.py',
        '--noconsole',
        '--onefile',
        '--name=ChromiumBrowserMigratorWin',
        '--add-data=src/cpm/m09_gui/web;cpm/m09_gui/web', # Windows uses ';' as separator
        '--collect-all=cpm',
        '--distpath=dist/windows',
        '--workpath=build/windows',
    ]
    
    PyInstaller.__main__.run(args)
    print("✅ Windows Portable EXE built successfully in dist/windows/")

if __name__ == "__main__":
    build_windows_app()
