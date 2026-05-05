import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from cpm.m05_writer.base import BaseProfileWriter
from cpm.core.dataclasses import ProfileSnapshot
from cpm.m08_logger.logger import cpm_logger


class ChromiumWriter(BaseProfileWriter):
    """
    Writes data to a Chromium-based browser profile.
    Uses atomic temp-file writes for SQLite to prevent corruption.
    """

    def _execute_atomic_sql_write(self, db_path: Path, setup_sql: str, insert_sql: str, data: list):
        """Copies DB to temp, writes data, replaces original."""
        if not data:
            return

        temp_dir = Path(tempfile.mkdtemp())
        temp_db = temp_dir / db_path.name

        # If DB doesn't exist, we might need to create it with the schema.
        # But for Chrome migrations, we assume the user has run the target browser at least once.
        if db_path.exists():
            shutil.copy2(db_path, temp_db)

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            if setup_sql:
                cursor.execute(setup_sql)

            cursor.executemany(insert_sql, data)
            conn.commit()
            conn.close()

            # Atomic replace
            shutil.move(temp_db, db_path)
            cpm_logger.info(f"Successfully wrote {len(data)} items to {db_path.name}")
        except Exception as e:
            cpm_logger.error(f"Error writing to DB {db_path.name}: {e}")
            raise
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def write_bookmarks(self, bookmarks: list) -> bool:
        if not bookmarks:
            return True

        bookmarks_path = self.target_profile_path / "Bookmarks"
        raw_json = self.adapter.export_bookmarks(bookmarks)

        if not raw_json:
            return True

        temp_file = bookmarks_path.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(raw_json, f, indent=3)
            # Atomic replace
            temp_file.replace(bookmarks_path)
            cpm_logger.info("Successfully wrote Bookmarks.")
            return True
        except Exception as e:
            cpm_logger.error(f"Error writing Bookmarks: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return False

    def write_cookies(self, cookies: list) -> bool:
        if not cookies:
            return True
        
        cookie_path = self.target_profile_path / "Network" / "Cookies"
        if not cookie_path.parent.exists():
            cookie_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure the table exists if we are creating a new DB
        setup_sql = """
        CREATE TABLE IF NOT EXISTS cookies (
            host_key TEXT, name TEXT, encrypted_value BLOB, path TEXT, 
            expires_utc INTEGER, is_secure INTEGER, is_httponly INTEGER, 
            has_expires INTEGER, is_persistent INTEGER, samesite INTEGER
        );
        """
        
        insert_sql = """
            INSERT OR REPLACE INTO cookies 
            (host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly, has_expires, is_persistent, samesite)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = [
            (
                c.host_key,
                c.name,
                c.encrypted_value,
                c.path,
                c.expires_utc,
                int(c.is_secure),
                int(c.is_httponly),
                int(c.has_expires),
                int(c.is_persistent),
                c.samesite,
            )
            for c in cookies
        ]
        
        try:
            self._execute_atomic_sql_write(cookie_path, setup_sql, insert_sql, data)
            return True
        except Exception:
            return False

    def write_passwords(self, passwords: list) -> bool:
        if not passwords:
            return True
        
        login_data_path = self.target_profile_path / "Login Data"
        
        insert_sql = """
            INSERT OR REPLACE INTO logins 
            (origin_url, action_url, username_element, username_value, password_element, password_value, date_created, times_used, signon_realm, blacklisted_by_user, scheme)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        data = [
            (
                p.origin_url,
                p.action_url,
                p.username_element,
                p.username_value,
                p.password_element,
                p.encrypted_password,
                p.date_created,
                p.times_used,
                p.origin_url, # signon_realm
                0, # blacklisted_by_user default
                "password", # scheme
            )
            for p in passwords
        ]
        
        try:
            self._execute_atomic_sql_write(login_data_path, "", insert_sql, data)
            return True
        except Exception:
            return False

    def write_profile(self, snapshot: ProfileSnapshot) -> bool:
        cpm_logger.info(
            f"Writing profile to {self.target_profile_path} using {self.adapter.browser_id} adapter"
        )

        success = True
        success &= self.write_bookmarks(snapshot.bookmarks)
        success &= self.write_cookies(snapshot.cookies)
        success &= self.write_passwords(snapshot.passwords)

        return success
