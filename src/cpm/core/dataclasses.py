from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class BookmarkItem:
    id: str
    name: str
    url: Optional[str] = None
    type: str = "url" # "url" or "folder"
    children: List['BookmarkItem'] = field(default_factory=list)

@dataclass
class CookieItem:
    host_key: str
    name: str
    encrypted_value: bytes
    path: str
    expires_utc: int
    is_secure: bool
    is_httponly: bool
    has_expires: bool
    is_persistent: bool
    samesite: int

@dataclass
class PasswordItem:
    origin_url: str
    action_url: str
    username_element: str
    username_value: str
    password_element: str
    encrypted_password: bytes
    date_created: int
    times_used: int

@dataclass
class ProfileSnapshot:
    browser_id: str
    profile_name: str
    bookmarks: List[BookmarkItem] = field(default_factory=list)
    cookies: List[CookieItem] = field(default_factory=list)
    passwords: List[PasswordItem] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
