import hashlib
import json
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
            if isinstance(root_node, dict):
                # Preserve original root key as the bookmark item id so export
                # can reconstruct the correct Chromium root structure.
                node_with_key = dict(root_node)
                node_with_key.setdefault("_root_key", root_key)
                item = self._parse_bookmark_node(node_with_key)
                item.id = root_key  # use root_key as id to survive round-trip
                result.append(item)
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
        roots: Dict[str, Any] = {}
        for item in standardized_bookmarks:
            # The item.id was set to the original root_key in transform_bookmarks.
            # Fall back to heuristic mapping only for bookmarks not created by this tool.
            root_key = item.id if item.id in ("bookmark_bar", "other", "synced") else "other"
            if root_key == "other":
                name_lower = item.name.lower()
                if "bar" in name_lower or "toolbar" in name_lower:
                    root_key = "bookmark_bar"
                elif "sync" in name_lower or "mobile" in name_lower:
                    root_key = "synced"
            roots[root_key] = self._export_bookmark_node(item)

        # Chromium validates a checksum of the roots object on load. Compute an
        # MD5 over the canonical JSON so Chrome accepts the file without warnings.
        roots_json = json.dumps(roots, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        checksum = hashlib.md5(roots_json.encode("utf-8")).hexdigest()

        return {"version": 1, "checksum": checksum, "roots": roots}


class ChromeAdapter(ChromiumBookmarksMixin, BaseBrowserAdapter):
    @property
    def browser_id(self) -> str:
        return "chrome"
