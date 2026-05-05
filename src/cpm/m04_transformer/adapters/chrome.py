from typing import Dict, Any, List
from cpm.m04_transformer.base import BaseBrowserAdapter
from cpm.core.dataclasses import BookmarkItem


class ChromiumBookmarksMixin:
    """Shared bookmark parsing/export logic for all Chromium-based browsers."""

    def _parse_bookmark_node(self, node: Dict[str, Any]) -> BookmarkItem:
        item = BookmarkItem(
            id=node.get("id", ""),
            name=node.get("name", ""),
            type=node.get("type", "url"),
            url=node.get("url"),
        )

        if "children" in node:
            for child in node["children"]:
                item.children.append(self._parse_bookmark_node(child))

        return item

    def transform_bookmarks(self, raw_bookmarks: Dict[str, Any]) -> List[BookmarkItem]:
        roots = raw_bookmarks.get("roots", {})
        result = []
        for root_key, root_node in roots.items():
            # root_key typically: bookmark_bar, other, synced
            if isinstance(root_node, dict):
                result.append(self._parse_bookmark_node(root_node))
        return result

    def _export_bookmark_node(self, item: BookmarkItem) -> Dict[str, Any]:
        node: Dict[str, Any] = {
            "id": item.id,
            "name": item.name,
            "type": item.type,
        }
        if item.url:
            node["url"] = item.url

        if item.children:
            node["children"] = [self._export_bookmark_node(child) for child in item.children]

        return node

    def export_bookmarks(self, standardized_bookmarks: List[BookmarkItem]) -> Dict[str, Any]:
        roots = {}
        for item in standardized_bookmarks:
            # We map back based on typical chrome roots or just put everything in bookmark_bar if unknown
            # For simplicity, if it has a generic name, we map it, else dump into other
            root_key = "other"
            name_lower = item.name.lower()
            if "bar" in name_lower:
                root_key = "bookmark_bar"
            elif "sync" in name_lower:
                root_key = "synced"

            roots[root_key] = self._export_bookmark_node(item)

        return {"version": 1, "checksum": "placeholder", "roots": roots}


class ChromeAdapter(ChromiumBookmarksMixin, BaseBrowserAdapter):
    @property
    def browser_id(self) -> str:
        return "chrome"
