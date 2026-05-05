import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from .base import BaseBackupManager
from cpm.m08_logger.logger import cpm_logger


class MacOSBackupManager(BaseBackupManager):
    def __init__(self, backup_root: Optional[str] = None):
        self.backup_root = Path(backup_root) if backup_root else Path.home() / "CPM_Backups"

    def create_backup(self, profile_path: str) -> Optional[Path]:
        profile_path = Path(profile_path).expanduser().resolve()
        if not profile_path.exists():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"{profile_path.name}.tar.gz"

            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(profile_path, arcname=profile_path.name)
            return backup_file
        except Exception as e:
            cpm_logger.error(f"MacOS Backup failed: {e}")
            return None

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        backup_file_path = Path(backup_file).expanduser().resolve()
        destination = Path(destination_root).expanduser().resolve()

        try:
            with tarfile.open(backup_file_path, "r:gz") as tar:
                # Guard against path traversal (CVE-2007-4559 / zip-slip class).
                for member in tar.getmembers():
                    member_path = (destination / member.name).resolve()
                    if not str(member_path).startswith(str(destination)):
                        raise ValueError(
                            f"Refusing extraction of unsafe path: {member.name}"
                        )
                # filter='data' (Python 3.12+) strips unsafe metadata and absolute paths.
                # On older Python versions, we already validated members above.
                import sys
                if sys.version_info >= (3, 12):
                    tar.extractall(path=destination, filter="data")
                else:
                    tar.extractall(path=destination)
            return True
        except Exception as e:
            cpm_logger.error(f"MacOS Restore failed: {e}")
            return False
