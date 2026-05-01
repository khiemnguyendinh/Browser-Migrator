from abc import ABC, abstractmethod
from pathlib import Path
from cpm.core.dataclasses import ProfileSnapshot
from cpm.m04_transformer.base import BaseBrowserAdapter


class BaseProfileWriter(ABC):
    """
    Abstract base class for writing profile data to the target browser.
    """

    def __init__(self, target_profile_path: Path, adapter: BaseBrowserAdapter):
        self.target_profile_path = target_profile_path
        self.adapter = adapter

    @abstractmethod
    def write_profile(self, snapshot: ProfileSnapshot) -> bool:
        """Write a ProfileSnapshot into the target profile path."""
        pass

    @abstractmethod
    def write_bookmarks(self, bookmarks: list) -> bool:
        pass

    @abstractmethod
    def write_cookies(self, cookies: list) -> bool:
        pass

    @abstractmethod
    def write_passwords(self, passwords: list) -> bool:
        pass
