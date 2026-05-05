import json
from pathlib import Path
from typing import List
from .models import BrowserInfo, ProfileInfo
from cpm.core.platform import CURRENT_PLATFORM, Platform
from .platforms.macos import MacOSDetector
from .platforms.windows import WindowsDetector

class BrowserDetector:
    """M01 - Factory for Platform-specific Browser Detection."""
    
    _instance = None

    @classmethod
    def get_detector(cls):
        if cls._instance is None:
            if CURRENT_PLATFORM == Platform.MACOS:
                cls._instance = MacOSDetector()
            elif CURRENT_PLATFORM == Platform.WINDOWS:
                cls._instance = WindowsDetector()
            else:
                raise RuntimeError(f"Unsupported platform: {CURRENT_PLATFORM}")
        return cls._instance

    @staticmethod
    def get_installed_browsers() -> List[BrowserInfo]:
        """Returns a list of installed browsers using the appropriate platform detector."""
        return BrowserDetector.get_detector().get_installed_browsers()

    @staticmethod
    def detect_profiles(base_path: Path) -> List[ProfileInfo]:
        """Detects profiles using the appropriate platform detector."""
        return BrowserDetector.get_detector().detect_profiles(base_path)
