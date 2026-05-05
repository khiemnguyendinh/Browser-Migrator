import json
from pathlib import Path
from typing import List
from .base import BaseDetector
from cpm.m01_detector.models import BrowserInfo, ProfileInfo

BROWSER_PATHS = {
    "chrome": {
        "name": "Google Chrome",
        "app": "Google Chrome.app",
        "path": "~/Library/Application Support/Google/Chrome",
    },
    "edge": {
        "name": "Microsoft Edge",
        "app": "Microsoft Edge.app",
        "path": "~/Library/Application Support/Microsoft Edge",
    },
    "brave": {
        "name": "Brave",
        "app": "Brave Browser.app",
        "path": "~/Library/Application Support/BraveSoftware/Brave-Browser",
    },
    "arc": {
        "name": "Arc",
        "app": "Arc.app",
        "path": "~/Library/Application Support/Arc/User Data",
    },
    "coccoc": {
        "name": "Cốc Cốc",
        "app": "Cốc Cốc.app",
        "path": "~/Library/Application Support/CocCoc/Browser",
    },
    "comet": {
        "name": "Comet",
        "app": None,
        "path": "~/Library/Application Support/Perplexity/Comet",
    },
    "vivaldi": {
        "name": "Vivaldi",
        "app": "Vivaldi.app",
        "path": "~/Library/Application Support/Vivaldi",
    },
    "opera": {
        "name": "Opera",
        "app": "Opera.app",
        "path": "~/Library/Application Support/com.operasoftware.Opera",
    },
}

class MacOSDetector(BaseDetector):
    def _is_app_installed(self, app_name: str) -> bool:
        if not app_name:
            return True
        return Path(f"/Applications/{app_name}").exists() or Path(f"~/Applications/{app_name}").expanduser().exists()

    def get_installed_browsers(self) -> List[BrowserInfo]:
        installed = []
        for browser_id, info in BROWSER_PATHS.items():
            # In the latest version, we check base_path directly
            base_path = Path(info["path"]).expanduser()
            if base_path.exists() and base_path.is_dir():
                profiles = self.detect_profiles(base_path)
                installed.append(
                    BrowserInfo(
                        id=browser_id,
                        name=info["name"],
                        install_path=None,
                        profile_dir=base_path,
                        profiles=profiles,
                    )
                )
        return installed

    def detect_profiles(self, base_path: Path) -> List[ProfileInfo]:
        profiles = []
        local_state_path = base_path / "Local State"

        if not local_state_path.exists():
            default_path = base_path / "Default"
            if default_path.exists() and default_path.is_dir():
                profiles.append(ProfileInfo(name="Default", path=default_path, is_default=True))
            return profiles

        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                state = json.load(f)

            profile_info_cache = state.get("profile", {}).get("info_cache", {})
            last_used = state.get("profile", {}).get("last_used", "")

            for profile_dir_name, info in profile_info_cache.items():
                profile_path = base_path / profile_dir_name
                if profile_path.exists() and profile_path.is_dir():
                    profile_name = info.get("name", profile_dir_name)
                    is_default = (
                        (profile_dir_name == last_used)
                        if last_used
                        else (profile_dir_name == "Default")
                    )
                    profiles.append(
                        ProfileInfo(name=profile_name, path=profile_path, is_default=is_default)
                    )
        except Exception:
            default_path = base_path / "Default"
            if default_path.exists() and default_path.is_dir():
                profiles.append(ProfileInfo(name="Default", path=default_path, is_default=True))

        return profiles
