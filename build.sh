#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting build process for Chromium Browser Migrator..."

# Ensure PyInstaller is installed
pip install pyinstaller

# Define paths
ENTRY_POINT="src/cpm/m06_cli/main.py"
WEB_DIR="src/cpm/m09_gui/web"
APP_NAME="ChromiumBrowserMigrator"

echo "📦 Bundling application using PyInstaller..."

# PyInstaller command
# --noconsole: Hide the terminal window when launching the GUI app
# --onefile: (Optional) but we prefer --windowed for .app bundles on macOS
# --windowed: Create a macOS .app bundle
# --add-data: Include the web assets
# --name: Name of the final executable/app

pyinstaller --noconsole --windowed \
    --name "$APP_NAME" \
    --add-data "$WEB_DIR:cpm/m09_gui/web" \
    --collect-all cpm \
    "$ENTRY_POINT"

echo "✅ Build completed successfully!"
echo "📂 Your application is available in the 'dist' folder as $APP_NAME.app"
