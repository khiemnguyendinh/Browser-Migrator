from abc import ABC, abstractmethod
from typing import Dict, Any
from cpm.core.dataclasses import ProfileSnapshot, BookmarkItem, CookieItem, PasswordItem

class BaseBrowserAdapter(ABC):
    """
    Adapter base class for data transformation between specific browsers and the unified model.
    """
    
    @property
    @abstractmethod
    def browser_id(self) -> str:
        """Return the ID of the browser this adapter handles (e.g., 'chrome', 'edge')."""
        pass

    @abstractmethod
    def transform_bookmarks(self, raw_bookmarks: Dict[str, Any]) -> list[BookmarkItem]:
        """Convert raw browser bookmarks JSON into standardized BookmarkItems."""
        pass

    @abstractmethod
    def export_bookmarks(self, standardized_bookmarks: list[BookmarkItem]) -> Dict[str, Any]:
        """Convert standardized BookmarkItems back into browser-specific JSON format."""
        pass

    def transform_cookie(self, raw_row: dict) -> CookieItem:
        """Convert a raw SQLite cookie row into a CookieItem. Can be overridden if needed."""
        return CookieItem(
            host_key=raw_row.get("host_key", ""),
            name=raw_row.get("name", ""),
            encrypted_value=raw_row.get("encrypted_value", b""),
            path=raw_row.get("path", "/"),
            expires_utc=raw_row.get("expires_utc", 0),
            is_secure=bool(raw_row.get("is_secure", 0)),
            is_httponly=bool(raw_row.get("is_httponly", 0)),
            has_expires=bool(raw_row.get("has_expires", 0)),
            is_persistent=bool(raw_row.get("is_persistent", 0)),
            samesite=raw_row.get("samesite", -1)
        )

    def transform_password(self, raw_row: dict) -> PasswordItem:
        """Convert a raw SQLite password row into a PasswordItem."""
        return PasswordItem(
            origin_url=raw_row.get("origin_url", ""),
            action_url=raw_row.get("action_url", ""),
            username_element=raw_row.get("username_element", ""),
            username_value=raw_row.get("username_value", ""),
            password_element=raw_row.get("password_element", ""),
            encrypted_password=raw_row.get("password_value", b""),
            date_created=raw_row.get("date_created", 0),
            times_used=raw_row.get("times_used", 0)
        )
