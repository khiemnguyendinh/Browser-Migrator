from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class BaseBackupManager(ABC):
    """Abstract base class for backup/rollback across platforms."""
    
    @abstractmethod
    def create_backup(self, profile_path: str) -> Optional[Path]:
        pass

    @abstractmethod
    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        pass
