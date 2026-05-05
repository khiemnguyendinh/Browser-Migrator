import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from .base import BaseBackupManager
from cpm.m08_logger.logger import cpm_logger

class WindowsBackupManager(BaseBackupManager):
    def __init__(self, backup_root: Optional[str] = None):
        # Use Windows standard AppData or a custom folder
        self.backup_root = Path(backup_root) if backup_root else Path("C:/CPM_Backups")

    def create_backup(self, profile_path: str) -> Optional[Path]:
        profile_path = Path(profile_path).resolve()
        if not profile_path.exists():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"{profile_path.name}.zip"
            
            # Using shutil.make_archive for simple ZIP creation
            shutil.make_archive(
                str(backup_file).replace(".zip", ""), 
                'zip', 
                root_dir=profile_path.parent, 
                base_dir=profile_path.name
            )
            return backup_file
        except Exception as e:
            cpm_logger.error(f"Windows Backup failed: {e}")
            return None

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        backup_file = Path(backup_file).resolve()
        destination_root = Path(destination_root).resolve()
        try:
            with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                zip_ref.extractall(destination_root)
            return True
        except Exception as e:
            cpm_logger.error(f"Windows Restore failed: {e}")
            return False
