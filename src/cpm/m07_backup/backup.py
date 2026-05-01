import tarfile
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
        resolved_path = Path(profile_path).expanduser().resolve()
        if not resolved_path.exists():
            cpm_logger.error(f"Backup failed: Profile path {resolved_path} does not exist")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_root / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)

            backup_file = backup_dir / f"{resolved_path.name}.tar.gz"

            cpm_logger.info(f"Creating backup of {resolved_path} to {backup_file}")

            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(resolved_path, arcname=resolved_path.name)

            return backup_file
        except Exception as e:
            cpm_logger.error(f"Backup failed: {str(e)}")
            return None

    def restore_backup(self, backup_file: str, destination_root: str) -> bool:
        """
        Restores a backup from a tar.gz file to the destination root.
        """
        resolved_backup = Path(backup_file).expanduser().resolve()
        resolved_dest = Path(destination_root).expanduser().resolve()

        if not resolved_backup.exists():
            cpm_logger.error(f"Restore failed: Backup file {resolved_backup} does not exist")
            return False

        try:
            cpm_logger.info(f"Restoring backup from {resolved_backup} to {resolved_dest}")

            with tarfile.open(resolved_backup, "r:gz") as tar:
                # Extract to destination root
                tar.extractall(path=resolved_dest, filter="data")

            return True
        except Exception as e:
            cpm_logger.error(f"Restore failed: {str(e)}")
            return False
