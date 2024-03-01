
import unittest

from network_saver.utility import *


class TestRemapNodeCategories(unittest.TestCase):

    def test_string_category(self):
        data = "Sop"
        result = remap_node_categories(data)
        self.assertEqual(result, "SOP")
    
    def test_unrecognized_category(self):
        data = "Mop"
        with self.assertRaises(RuntimeError):
            _result = remap_node_categories(data)

    def test_return_type(self):
        data = "Object"
        result = remap_node_categories(data)
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()
