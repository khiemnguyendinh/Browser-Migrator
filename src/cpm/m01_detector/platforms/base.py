from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from cpm.m01_detector.models import BrowserInfo

class BaseDetector(ABC):
    """Abstract base class for browser detection across platforms."""
    
    @abstractmethod
    def get_installed_browsers(self) -> List[BrowserInfo]:
        """Return list of installed browsers."""
        pass

    @abstractmethod
    def detect_profiles(self, base_path: Path) -> List:
        """Detect profiles within a browser's base path."""
        pass
