import json
from pathlib import Path
from typing import Dict, List, Optional
from .models import BrowserInfo, ProfileInfo

# Các path chuẩn trên macOS cho trình duyệt Chromium
BROWSER_PATHS = {
    "chrome": {
        "name": "Google Chrome",
        "path": "~/Library/Application Support/Google/Chrome",
    },
    "edge": {
        "name": "Microsoft Edge",
        "path": "~/Library/Application Support/Microsoft Edge",
    },
    "brave": {
        "name": "Brave",
        "path": "~/Library/Application Support/BraveSoftware/Brave-Browser",
    },
    "arc": {
        "name": "Arc",
        "path": "~/Library/Application Support/Arc/User Data",
    },
    "coccoc": {
        "name": "Cốc Cốc",
        "path": "~/Library/Application Support/Coccoc",
    },
    "comet": {
        "name": "Comet",
        "path": "~/Library/Application Support/Perplexity/Comet",
    },
    "vivaldi": {
        "name": "Vivaldi",
        "path": "~/Library/Application Support/Vivaldi",
    },
    "opera": {
        "name": "Opera",
        "path": "~/Library/Application Support/com.operasoftware.Opera",
    },
}

class BrowserDetector:
    """M01 - Phát hiện và đọc danh sách trình duyệt, profile trên macOS."""

    @staticmethod
    def get_installed_browsers() -> List[BrowserInfo]:
        """Trả về danh sách các trình duyệt đã cài đặt trên máy."""
        installed = []
        for browser_id, info in BROWSER_PATHS.items():
            base_path = Path(info["path"]).expanduser()
            if base_path.exists() and base_path.is_dir():
                profiles = BrowserDetector.detect_profiles(base_path)
                installed.append(
                    BrowserInfo(
                        id=browser_id,
                        name=info["name"],
                        install_path=None,  # Phase A có thể bỏ qua query Info.plist
                        profile_dir=base_path,
                        profiles=profiles,
                    )
                )
        return installed

    @staticmethod
    def detect_profiles(base_path: Path) -> List[ProfileInfo]:
        """Đọc file Local State để lấy danh sách profiles."""
        profiles = []
        local_state_path = base_path / "Local State"
        
        if not local_state_path.exists():
            # Nếu không có Local State, thử fallback bằng cách đọc folder Default
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
                    is_default = (profile_dir_name == last_used) if last_used else (profile_dir_name == "Default")
                    profiles.append(
                        ProfileInfo(
                            name=profile_name,
                            path=profile_path,
                            is_default=is_default
                        )
                    )
        except Exception:
            # Fallback nếu lỗi đọc json
            default_path = base_path / "Default"
            if default_path.exists() and default_path.is_dir():
                profiles.append(ProfileInfo(name="Default", path=default_path, is_default=True))
                
        return profiles
