from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class ProfileInfo:
    name: str
    path: Path
    is_default: bool

@dataclass
class BrowserInfo:
    id: str
    name: str
    install_path: Optional[Path]
    profile_dir: Path
    profiles: List[ProfileInfo]

    @property
    def is_installed(self) -> bool:
        return self.profile_dir.exists() and self.profile_dir.is_dir()
