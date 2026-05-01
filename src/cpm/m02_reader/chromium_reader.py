import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from cpm.m02_reader.base import BaseProfileReader
from cpm.core.dataclasses import ProfileSnapshot
from cpm.m08_logger.logger import cpm_logger


class ChromiumReader(BaseProfileReader):
    """
    Reads data from a Chromium-based browser profile.
    """

    def _copy_db_to_temp(self, db_path: Path) -> Path:
        """Copy SQLite DB to temp file to avoid lock issues when browser is open."""
        temp_dir = Path(tempfile.mkdtemp())
        temp_db = temp_dir / db_path.name
        try:
            shutil.copy2(db_path, temp_db)
            return temp_db
        except Exception as e:
            cpm_logger.error(f"Failed to copy DB {db_path}: {e}")
            raise

    def read_bookmarks(self) -> list:
        bookmarks_path = self.profile_path / "Bookmarks"
        if not bookmarks_path.exists():
            cpm_logger.info("No Bookmarks file found.")
            return []

        try:
            with open(bookmarks_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self.adapter.transform_bookmarks(data)
        except Exception as e:
            cpm_logger.error(f"Error reading bookmarks: {e}")
            return []

    def read_cookies(self) -> list:
        # Chromium uses 'Network/Cookies' or 'Cookies'
        cookie_path = self.profile_path / "Network" / "Cookies"
        if not cookie_path.exists():
            cookie_path = self.profile_path / "Cookies"

        if not cookie_path.exists():
            cpm_logger.info("No Cookies DB found.")
            return []

        temp_db = self._copy_db_to_temp(cookie_path)
        cookies = []
        try:
            conn = sqlite3.connect(f"file:{temp_db}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Chromium Cookie schema: host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite, encrypted_value...
            cursor.execute("SELECT * FROM cookies")
            for row in cursor.fetchall():
                cookies.append(self.adapter.transform_cookie(dict(row)))

        except Exception as e:
            cpm_logger.error(f"Error reading cookies: {e}")
        finally:
            conn.close()
            shutil.rmtree(temp_db.parent, ignore_errors=True)

        return cookies

    def read_passwords(self) -> list:
        login_data_path = self.profile_path / "Login Data"
        if not login_data_path.exists():
            cpm_logger.info("No Login Data DB found.")
            return []

        temp_db = self._copy_db_to_temp(login_data_path)
        passwords = []
        try:
            conn = sqlite3.connect(f"file:{temp_db}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM logins")
            for row in cursor.fetchall():
                passwords.append(self.adapter.transform_password(dict(row)))

        except Exception as e:
            cpm_logger.error(f"Error reading passwords: {e}")
        finally:
            conn.close()
            shutil.rmtree(temp_db.parent, ignore_errors=True)

        return passwords

    def read_profile(self) -> ProfileSnapshot:
        cpm_logger.info(
            f"Reading profile from {self.profile_path} using {self.adapter.browser_id} adapter"
        )

        # Read preferences (just a basic read for now)
        prefs = {}
        prefs_path = self.profile_path / "Preferences"
        if prefs_path.exists():
            try:
                with open(prefs_path, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
            except Exception:
                pass

        snapshot = ProfileSnapshot(
            browser_id=self.adapter.browser_id,
            profile_name=self.profile_path.name,
            bookmarks=self.read_bookmarks(),
            cookies=self.read_cookies(),
            passwords=self.read_passwords(),
            preferences=prefs,
        )
        return snapshot
