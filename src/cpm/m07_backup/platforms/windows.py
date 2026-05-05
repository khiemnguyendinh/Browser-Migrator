import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from .base import BaseBackupManager
from cpm.m08_logger.logger import cpm_logger


class WindowsBackupManager(BaseBackupManager):
    def __init__(self, backup_root: Optional[str] = None):
        # Default to %LOCALAPPDATA%\CPM_Backups to avoid needing admin rights on C:\.
        if backup_root:
            self.backup_root = Path(backup_root)
        else:
            local_app_data = os.environ.get("LOCALAPPDATA") or str(Path.home())
            self.backup_root = Path(local_app_data) / "CPM_Backups"

    def create_backup(self, profile_path: str) -> Optional[Path]:
        profile_path = Path(profile_path).resolve()
        if not profile_path.exists():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"{profile_path.name}.zip"

            shutil.make_archive(
                str(backup_file).replace(".zip", ""),
                "zip",
                root_dir=profile_path.parent,
                base_dir=profile_path.name,
            )
            return backup_file
        except Exception as e:
            cpm_logger.error(f"Windows Backup failed: {e}")
            return None

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        backup_file_path = Path(backup_file).resolve()
        destination = Path(destination_root).resolve()

        try:
            with zipfile.ZipFile(backup_file_path, "r") as zf:
                # Guard against zip-slip path traversal attacks.
                for entry in zf.namelist():
                    entry_path = (destination / entry).resolve()
                    if not str(entry_path).startswith(str(destination)):
                        raise ValueError(
                            f"Refusing extraction of unsafe path: {entry}"
                        )
                zf.extractall(destination)
            return True
        except Exception as e:
            cpm_logger.error(f"Windows Restore failed: {e}")
            return False
