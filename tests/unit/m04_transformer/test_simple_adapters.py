import unittest
from cpm.m04_transformer.adapters.edge import EdgeAdapter
from cpm.m04_transformer.adapters.brave import BraveAdapter
from cpm.m04_transformer.adapters.coccoc import CocCocAdapter
from cpm.m04_transformer.adapters.comet import CometAdapter

class TestSimpleAdapters(unittest.TestCase):
    def _assert_valid_bookmark_export(self, result):
        """export_bookmarks always returns a valid Chromium bookmarks structure."""
        self.assertIn("version", result)
        self.assertIn("checksum", result)
        self.assertIn("roots", result)
        self.assertIsInstance(result["checksum"], str)
        self.assertEqual(len(result["checksum"]), 32)  # MD5 hex digest

    def test_edge_adapter(self):
        adapter = EdgeAdapter()
        self.assertEqual(adapter.browser_id, "edge")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self._assert_valid_bookmark_export(adapter.export_bookmarks([]))

    def test_brave_adapter(self):
        adapter = BraveAdapter()
        self.assertEqual(adapter.browser_id, "brave")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self._assert_valid_bookmark_export(adapter.export_bookmarks([]))

    def test_coccoc_adapter(self):
        adapter = CocCocAdapter()
        self.assertEqual(adapter.browser_id, "coccoc")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self._assert_valid_bookmark_export(adapter.export_bookmarks([]))

    def test_comet_adapter(self):
        adapter = CometAdapter()
        self.assertEqual(adapter.browser_id, "comet")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self._assert_valid_bookmark_export(adapter.export_bookmarks([]))

if __name__ == "__main__":
    unittest.main()
