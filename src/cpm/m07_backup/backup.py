import tarfile
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from cpm.m08_logger.logger import cpm_logger

class BackupManager:
    def __init__(self, backup_root: Optional[str] = None):
        self.backup_root = Path(backup_root) if backup_root else Path.home() / "CPM_Backups"

    def create_backup(self, profile_path: str) -> Optional[Path]:
        """
        Creates a tar.gz backup of the specified profile path.
        Returns the path to the created backup file.
        """
        profile_path = Path(profile_path).expanduser().resolve()
        if not profile_path.exists():
            cpm_logger.error(f"Backup failed: Profile path {profile_path} does not exist")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"{profile_path.name}.tar.gz"
            
            cpm_logger.info(f"Creating backup of {profile_path} to {backup_file}")
            
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(profile_path, arcname=profile_path.name)
            
            return backup_file
        except Exception as e:
            cpm_logger.error(f"Backup failed: {str(e)}")
            return None

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        """
        Restores a backup from a tar.gz file to the destination root.
        """
        backup_file = Path(backup_file).expanduser().resolve()
        destination_root = Path(destination_root).expanduser().resolve()
        
        if not backup_file.exists():
            cpm_logger.error(f"Restore failed: Backup file {backup_file} does not exist")
            return False

        try:
            cpm_logger.info(f"Restoring backup from {backup_file} to {destination_root}")
            
            with tarfile.open(backup_file, "r:gz") as tar:
                # Extract to destination root
                tar.extractall(path=destination_root, filter='data')
            
            return True
        except Exception as e:
            cpm_logger.error(f"Restore failed: {str(e)}")
            return False
