from pathlib import Path
from typing import Optional, Dict, Any
from cpm.m08_logger.logger import cpm_logger
from cpm.m07_backup.backup import BackupManager
from cpm.m03_keychain.crypto import get_crypto_context, reencrypt_value, clear_context
from cpm.m04_transformer.adapters.chrome import ChromeAdapter
from cpm.m04_transformer.adapters.edge import EdgeAdapter
from cpm.m04_transformer.adapters.brave import BraveAdapter
from cpm.m04_transformer.adapters.coccoc import CocCocAdapter
from cpm.m04_transformer.adapters.comet import CometAdapter
from cpm.m02_reader.chromium_reader import ChromiumReader
from cpm.m05_writer.chromium_writer import ChromiumWriter


class MigrationOrchestrator:
    def __init__(self):
        self.backup_manager = BackupManager()

    def _get_adapter(self, browser_id: str):
        # Temporary map until OpenCode finishes other adapters
        adapters = {
            "chrome": ChromeAdapter(),
            "edge": EdgeAdapter(),
            "brave": BraveAdapter(),
            "coccoc": CocCocAdapter(),
            "comet": CometAdapter(),
        }
        # Fallback to ChromeAdapter for everything right now, to unblock development
        return adapters.get(browser_id, ChromeAdapter())

    def migrate(
        self,
        source_id: str,
        source_path: Path,
        target_id: str,
        target_path: Path,
        options: Optional[dict] = None,
    ) -> bool:
        cpm_logger.info(f"Starting migration from {source_id} to {target_id}")

        if options is None:
            options = {"passwords": True, "cookies": True, "bookmarks": True}

        # 1. Backup Target Profile
        backup_file = self.backup_manager.create_backup(str(target_path))
        if not backup_file:
            cpm_logger.error("Failed to create backup. Aborting migration.")
            return False

        source_ctx = None
        target_ctx = None

        try:
            # 2. Get Crypto Contexts
            cpm_logger.info("Acquiring cryptography contexts...")
            source_ctx = get_crypto_context(source_id, source_path)
            target_ctx = get_crypto_context(target_id, target_path)

            # 3. Read Source Profile
            cpm_logger.info("Reading source profile...")
            source_adapter = self._get_adapter(source_id)
            reader = ChromiumReader(source_path, source_adapter)
            snapshot = reader.read_profile()

            # Lọc snapshot theo options
            if not options.get("passwords", True):
                snapshot.passwords = []
            if not options.get("cookies", True):
                snapshot.cookies = []
            if not options.get("bookmarks", True):
                snapshot.bookmarks = []

            # 4. Re-encrypt Sensitive Data
            cpm_logger.info("Re-encrypting passwords and cookies...")
            for cookie in snapshot.cookies:
                cookie.encrypted_value = reencrypt_value(
                    cookie.encrypted_value, source_ctx, target_ctx
                )

            for pwd in snapshot.passwords:
                pwd.encrypted_password = reencrypt_value(
                    pwd.encrypted_password, source_ctx, target_ctx
                )

            # 5. Write Target Profile
            cpm_logger.info("Writing to target profile...")
            target_adapter = self._get_adapter(target_id)
            writer = ChromiumWriter(target_path, target_adapter)
            success = writer.write_profile(snapshot)

            # 6. Sao chép History và Auto Fill (Web Data) trực tiếp dạng file
            import shutil

            if options.get("history", True):
                cpm_logger.info("Migrating History and Autocomplete data...")
                for file_name in ["History", "Shortcuts", "Top Sites"]:
                    src_file = source_path / file_name
                    tgt_file = target_path / file_name
                    if src_file.exists():
                        try:
                            shutil.copy2(src_file, tgt_file)
                        except Exception as e:
                            cpm_logger.error(f"Failed to copy {file_name}: {e}")

            if options.get("autofill", True):
                cpm_logger.info("Migrating Auto Fill (Web Data)...")
                src_webdata = source_path / "Web Data"
                tgt_webdata = target_path / "Web Data"
                if src_webdata.exists():
                    shutil.copy2(src_webdata, tgt_webdata)

            if success:
                cpm_logger.info("Migration completed successfully.")
                return True
            else:
                raise Exception("Writer returned false.")

        except Exception as e:
            cpm_logger.error(f"Migration failed: {e}. Initiating rollback.")
            # Rollback
            self.backup_manager.restore_backup(str(backup_file), str(target_path.parent))
            return False

        finally:
            # 6. Memory Cleanup
            cpm_logger.info("Cleaning up memory contexts.")
            if source_ctx:
                clear_context(source_ctx)
            if target_ctx:
                clear_context(target_ctx)
