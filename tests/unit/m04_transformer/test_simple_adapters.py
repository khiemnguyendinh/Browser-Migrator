import unittest
from cpm.m04_transformer.adapters.edge import EdgeAdapter
from cpm.m04_transformer.adapters.brave import BraveAdapter
from cpm.m04_transformer.adapters.coccoc import CocCocAdapter
from cpm.m04_transformer.adapters.comet import CometAdapter

class TestSimpleAdapters(unittest.TestCase):
    def test_edge_adapter(self):
        adapter = EdgeAdapter()
        self.assertEqual(adapter.browser_id, "edge")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self.assertEqual(adapter.export_bookmarks([]), {})

    def test_brave_adapter(self):
        adapter = BraveAdapter()
        self.assertEqual(adapter.browser_id, "brave")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self.assertEqual(adapter.export_bookmarks([]), {})

    def test_coccoc_adapter(self):
        adapter = CocCocAdapter()
        self.assertEqual(adapter.browser_id, "coccoc")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self.assertEqual(adapter.export_bookmarks([]), {})

    def test_comet_adapter(self):
        adapter = CometAdapter()
        self.assertEqual(adapter.browser_id, "comet")
        self.assertEqual(adapter.transform_bookmarks({}), [])
        self.assertEqual(adapter.export_bookmarks([]), {})

if __name__ == "__main__":
    unittest.main()
