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
        """Copy DB to a temp file in the same directory, write data, then rename atomically."""
        if not data:
            return

        # Create temp file in the same directory as db_path to guarantee same-filesystem
        # rename (os.replace is atomic only within one filesystem).
        temp_dir = Path(tempfile.mkdtemp(dir=db_path.parent))
        temp_db = temp_dir / db_path.name

        if db_path.exists():
            shutil.copy2(db_path, temp_db)

        try:
            with sqlite3.connect(temp_db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if setup_sql:
                    cursor.executescript(setup_sql)
                cursor.executemany(insert_sql, data)
                conn.commit()

            # Atomic replace — safe because temp and dest are on the same filesystem.
            temp_db.replace(db_path)
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

        # UNIQUE on (host_key, name, path) enables INSERT OR REPLACE to deduplicate
        # on repeat migrations instead of accumulating duplicate rows.
        setup_sql = """
        CREATE TABLE IF NOT EXISTS cookies (
            host_key TEXT NOT NULL,
            name TEXT NOT NULL,
            encrypted_value BLOB,
            path TEXT NOT NULL,
            expires_utc INTEGER DEFAULT 0,
            is_secure INTEGER DEFAULT 0,
            is_httponly INTEGER DEFAULT 0,
            has_expires INTEGER DEFAULT 1,
            is_persistent INTEGER DEFAULT 1,
            samesite INTEGER DEFAULT -1,
            UNIQUE (host_key, name, path)
        );
        """

        insert_sql = """
            INSERT OR REPLACE INTO cookies
            (host_key, name, encrypted_value, path, expires_utc,
             is_secure, is_httponly, has_expires, is_persistent, samesite)
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
            (origin_url, action_url, username_element, username_value,
             password_element, password_value, date_created, times_used,
             signon_realm, blacklisted_by_user, scheme)
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
                p.origin_url,  # signon_realm
                0,             # blacklisted_by_user default
                "password",    # scheme
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
            f"Writing profile to {self.target_profile_path} "
            f"using {self.adapter.browser_id} adapter"
        )

        results = [
            self.write_bookmarks(snapshot.bookmarks),
            self.write_cookies(snapshot.cookies),
            self.write_passwords(snapshot.passwords),
        ]
        return all(results)
