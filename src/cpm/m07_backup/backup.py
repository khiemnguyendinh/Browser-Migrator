from pathlib import Path
from typing import Optional
from cpm.core.platform import CURRENT_PLATFORM, Platform
from .platforms.macos import MacOSBackupManager
from .platforms.windows import WindowsBackupManager

class BackupManager:
    """M07 - Factory for Platform-specific Backup Managers.

    Delegates to platform-specific implementation transparently.
    """

    def __init__(self, backup_root: str = None):
        self._delegate = self._create_delegate(backup_root)

    @staticmethod
    def _create_delegate(backup_root: str = None):
        if CURRENT_PLATFORM == Platform.MACOS:
            return MacOSBackupManager(backup_root)
        elif CURRENT_PLATFORM == Platform.WINDOWS:
            return WindowsBackupManager(backup_root)
        else:
            # Fallback to macOS-style tar.gz for Linux (dev/test environments)
            return MacOSBackupManager(backup_root)

    def create_backup(self, profile_path: str) -> Optional[Path]:
        return self._delegate.create_backup(profile_path)

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        return self._delegate.restore_backup(backup_file, destination_root)
