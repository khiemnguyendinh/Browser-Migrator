import unittest
import shutil
import tempfile
from pathlib import Path
from cpm.m07_backup.backup import BackupManager

class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.backup_root = self.test_dir / "backups"
        self.profile_dir = self.test_dir / "profile"
        self.profile_dir.mkdir()
        
        # Create some dummy files in profile
        (self.profile_dir / "file1.txt").write_text("content1")
        (self.profile_dir / "file2.txt").write_text("content2")
        
        self.manager = BackupManager(backup_root=str(self.backup_root))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_backup_success(self):
        backup_path = self.manager.create_backup(str(self.profile_dir))
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.suffix == ".gz")

    def test_create_backup_nonexistent_path(self):
        backup_path = self.manager.create_backup(str(self.test_dir / "nonexistent"))
        self.assertIsNone(backup_path)

    def test_restore_backup_success(self):
        backup_path = self.manager.create_backup(str(self.profile_dir))
        
        # Remove original profile
        shutil.rmtree(self.profile_dir)
        
        # Restore to test_dir (since backup includes profile folder name)
        success = self.manager.restore_backup(str(backup_path), str(self.test_dir))
        self.assertTrue(success)
        self.assertTrue(self.profile_dir.exists())
        self.assertEqual((self.profile_dir / "file1.txt").read_text(), "content1")

    def test_restore_backup_nonexistent_file(self):
        success = self.manager.restore_backup(str(self.test_dir / "no_backup.tar.gz"), str(self.test_dir))
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()
