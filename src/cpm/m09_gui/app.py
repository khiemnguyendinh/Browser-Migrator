import webview
from pathlib import Path
from typing import Optional, Dict, Any
from cpm.m01_detector.detector import BrowserDetector
from cpm.orchestrator import MigrationOrchestrator


class Api:
    def __init__(self):
        self.browsers = []

    def get_browsers(self):
        """Returns a list of installed browsers."""
        try:
            detected = BrowserDetector.get_installed_browsers()
            # Remove the strict len(b.profiles) > 0 filter to let the UI handle empty profiles
            self.browsers = detected
            
            result = []
            for b in self.browsers:
                profiles = [{"name": p.name, "path": str(p.path), "is_default": p.is_default} for p in b.profiles]
                result.append({
                    "id": b.id,
                    "name": b.name,
                    "profiles": profiles
                })
            return result
        except Exception as e:
            print(f"Error in get_browsers: {e}")
            return {"error": str(e)}

    def start_migration(
        self, source_id: str, source_profile_path: str, target_id: str, target_profile_path: str, options: Optional[Dict[str, Any]] = None
    ):
        """Executes the migration process."""
        try:
            if options is None:
                options = {
                    "passwords": True,
                    "cookies": True,
                    "bookmarks": True,
                    "history": True,
                    "autofill": True,
                }

            orchestrator = MigrationOrchestrator()
            success = orchestrator.migrate(
                source_id, Path(source_profile_path), target_id, Path(target_profile_path), options
            )

            if success:
                return {
                    "success": True,
                    "message": "Successfully migrated data! Please restart the target browser.",
                }
            else:
                return {
                    "success": False,
                    "message": "Migration failed. Please check the logs in ~/.cpm/logs.",
                }
        except Exception as e:
            return {"success": False, "message": str(e)}


import sys

def start_gui():
    """Starts the PyWebView application."""
    api = Api()

    # Hỗ trợ đường dẫn khi đóng gói bằng PyInstaller
    if hasattr(sys, '_MEIPASS'):
        web_dir = Path(sys._MEIPASS) / "cpm" / "m09_gui" / "web"
    else:
        web_dir = Path(__file__).parent / "web"
        
    index_html = web_dir / "index.html"

    webview.create_window(
        title="Chromium Profile Migrator",
        url=str(index_html),
        js_api=api,
        width=900,
        height=800,
        resizable=False,
        frameless=False,  # Set to true for completely custom window frame if desired
        background_color="#0f172a",
    )

    webview.start(debug=False)


if __name__ == "__main__":
    start_gui()
