from typing import Dict, Any
from cpm.m04_transformer.base import BaseBrowserAdapter
from cpm.core.dataclasses import BookmarkItem


class CocCocAdapter(BaseBrowserAdapter):
    @property
    def browser_id(self) -> str:
        return "coccoc"

    def transform_bookmarks(self, raw_bookmarks: Dict[str, Any]) -> list[BookmarkItem]:
        return []

    def export_bookmarks(self, standardized_bookmarks: list[BookmarkItem]) -> Dict[str, Any]:
        return {}
