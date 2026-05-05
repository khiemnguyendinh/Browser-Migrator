import json
import os
from pathlib import Path
from typing import List
from .base import BaseDetector
from cpm.m01_detector.models import BrowserInfo, ProfileInfo

# Windows Paths typically use %LocalAppData%
BROWSER_PATHS = {
    "chrome": {
        "name": "Google Chrome",
        "path": r"%LocalAppData%\Google\Chrome\User Data",
    },
    "edge": {
        "name": "Microsoft Edge",
        "path": r"%LocalAppData%\Microsoft\Edge\User Data",
    },
    "brave": {
        "name": "Brave",
        "path": r"%LocalAppData%\BraveSoftware\Brave-Browser\User Data",
    },
    "arc": {
        "name": "Arc",
        "path": r"%LocalAppData%\Arc\User Data",
    },
    "coccoc": {
        "name": "Cốc Cốc",
        "path": r"%LocalAppData%\CocCoc\Browser\User Data",
    },
    "comet": {
        "name": "Comet",
        "path": r"%LocalAppData%\Perplexity\Comet\User Data",
    },
    "vivaldi": {
        "name": "Vivaldi",
        "path": r"%LocalAppData%\Vivaldi\User Data",
    },
    "opera": {
        "name": "Opera",
        "path": r"%LocalAppData%\Opera Software\Opera Stable",
    },
}

class WindowsDetector(BaseDetector):
    def _expand_env_vars(self, path: str) -> Path:
        return Path(os.path.expandvars(path))

    def get_installed_browsers(self) -> List[BrowserInfo]:
        installed = []
        for browser_id, info in BROWSER_PATHS.items():
            base_path = self._expand_env_vars(info["path"])
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
