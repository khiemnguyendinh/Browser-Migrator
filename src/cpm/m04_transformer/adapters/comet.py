from typing import Dict, Any
from cpm.m04_transformer.base import BaseBrowserAdapter
from cpm.core.dataclasses import BookmarkItem


class CometAdapter(BaseBrowserAdapter):
    @property
    def browser_id(self) -> str:
        return "comet"

    def transform_bookmarks(self, raw_bookmarks: Dict[str, Any]) -> list[BookmarkItem]:
        return []

    def export_bookmarks(self, standardized_bookmarks: list[BookmarkItem]) -> Dict[str, Any]:
        return {}
