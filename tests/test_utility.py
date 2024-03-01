
import unittest

import hou

from network_saver.utility import *


class TestRemapNodeCategories(unittest.TestCase):
    # TODO: expand to cover every currently supported category
    def test_output(self):
        data = "Sop"
        result = remap_node_categories(data)
        self.assertEqual(result, "SOP")
        self.assertIsInstance(result, str)

    def test_bad_input(self):
        data = "Mop"
        with self.assertRaises(RuntimeError):
            remap_node_categories(data)


class TestGetNodeContext(unittest.TestCase):

    def setUp(self):
        self.node = hou.node('obj').createNode('geo')

    def test_output(self):
        # object node
        result = get_node_context(self.node)
        self.assertEqual(result, "OBJ")
        self.assertIsInstance(result, str)

    def test_bad_input(self):
        # node that does not exist
        with self.assertRaises(AttributeError):
            get_node_context(hou.node('obj/foo'))

        # node that's not a node
        with self.assertRaises(AttributeError):
            get_node_context(42)

    def tearDown(self):
        self.node.destroy()


class TestGetNetworkContext(unittest.TestCase):

    def setUp(self):
        self.subnet = hou.node('obj').createNode('lopnet')
        self.flat = hou.node('obj').createNode('geo').createNode('add')

    def test_output(self):
        # object node containing lop network
        result = get_network_context(self.subnet)
        self.assertEqual(result, "LOP")

        # sop node containing no network
        result = get_network_context(self.flat)
        self.assertEqual(result, "SOP")
        self.assertIsInstance(result, str)

    def test_bad_input(self):
        # node that does not exist
        with self.assertRaises(AttributeError):
            get_network_context(hou.node('obj/foo'))
        
        # node that's not a node
        with self.assertRaises(AttributeError):
            get_network_context(404)
    
    def tearDown(self):
        self.subnet.destroy()
        self.flat.destroy()

if __name__ == "__main__":
    unittest.main()
