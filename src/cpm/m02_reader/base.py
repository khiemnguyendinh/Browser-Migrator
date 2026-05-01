from abc import ABC, abstractmethod
from pathlib import Path
from cpm.core.dataclasses import ProfileSnapshot
from cpm.m04_transformer.base import BaseBrowserAdapter


class BaseProfileReader(ABC):
    """
    Abstract base class for reading profile data.
    """

    def __init__(self, profile_path: Path, adapter: BaseBrowserAdapter):
        self.profile_path = profile_path
        self.adapter = adapter

    @abstractmethod
    def read_profile(self) -> ProfileSnapshot:
        """Read all profile data into a ProfileSnapshot."""
        pass

    @abstractmethod
    def read_bookmarks(self) -> list:
        pass

    @abstractmethod
    def read_cookies(self) -> list:
        pass

    @abstractmethod
    def read_passwords(self) -> list:
        pass
