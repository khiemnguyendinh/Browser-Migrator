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
            self.browsers = [
                b for b in detected if b.is_installed and any(p.is_default for p in b.profiles)
            ]
            return [{"id": b.id, "name": b.name} for b in self.browsers]
        except Exception:
            return []

    def start_migration(
        self, source_id: str, target_id: str, options: Optional[Dict[str, Any]] = None
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

            source_browser = next((b for b in self.browsers if b.id == source_id), None)
            target_browser = next((b for b in self.browsers if b.id == target_id), None)

            if not source_browser or not target_browser:
                return {"success": False, "message": "Browser not found."}

            source_profile = next((p for p in source_browser.profiles if p.is_default), None)
            target_profile = next((p for p in target_browser.profiles if p.is_default), None)

            if not source_profile or not target_profile:
                return {"success": False, "message": "Default profile not found."}

            orchestrator = MigrationOrchestrator()
            success = orchestrator.migrate(
                source_id, source_profile.path, target_id, target_profile.path, options
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


def start_gui():
    """Starts the PyWebView application."""
    api = Api()

    # Path to web directory
    web_dir = Path(__file__).parent / "web"
    index_html = web_dir / "index.html"

    webview.create_window(
        title="Chromium Profile Migrator",
        url=str(index_html),
        js_api=api,
        width=900,
        height=650,
        resizable=False,
        frameless=False,  # Set to true for completely custom window frame if desired
        background_color="#0f172a",
    )

    webview.start(debug=False)


if __name__ == "__main__":
    start_gui()
