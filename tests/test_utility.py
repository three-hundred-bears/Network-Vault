
import json
import os
import unittest

import hou

from network_saver.utility import *


class TestRemapNodeCategories(unittest.TestCase):

    def test_output(self):
        recognized_categories = [
            "Shop", "CopNet", "Cop2", "ChopNet", "Chop", "Object",
            "Driver", "Sop", "Vop", "Lop", "TopNet", "Top", "Dop"
        ]
        for data in recognized_categories:
            result = remap_node_categories(data)
            self.assertEqual(result, CATEGORY_MAP[data])
            self.assertIsInstance(result, str)

    def test_bad_input(self):
        data = "Mop"
        with self.assertRaises(RuntimeError):
            remap_node_categories(data)

class TestGetVaultDir(unittest.TestCase):

    def test_get_data_dir(self):
        data_dir = get_data_dir()
        self.assertTrue(os.path.isdir(data_dir))
        self.assertEqual(
            data_dir,
            os.path.abspath("data")
        )

    def test_get_data_file(self):
        data_file = os.path.join(
            get_data_dir(),
            'vault_dir.txt'
        )
        self.assertTrue(os.path.isfile(data_file))

    def test_get_vault_dir(self):
        vault_dir = get_vault_dir()
        self.assertTrue(os.path.isdir(vault_dir))

class TestGetUserDir(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "_monty"
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
        )
        cls.user_dir = os.path.join(cls.fixture_dir, cls.user)
        os.mkdir(cls.user_dir)

    def test_output(self):
        user_dir = get_user_dir(user=self.user, vault_dir=self.fixture_dir)
        self.assertTrue(os.path.isdir(user_dir))
        self.assertEqual(
            user_dir,
            os.path.abspath("tests/fixtures/_monty")
        )

    def test_bad_output(self):
        # should not be making or validating these directories
        user_dir = get_user_dir(user="_alan", vault_dir=self.fixture_dir)
        self.assertFalse(os.path.isdir(user_dir))

    @classmethod
    def tearDownClass(cls):
        os.rmdir(cls.user_dir)


class TestGetVaultFiles(unittest.TestCase):

    def test_get_vault_files(self):
        vault_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures"
        )
        for user in os.listdir(vault_dir):
            vault_file = get_vault_file(user=user, vault_dir=vault_dir)
            self.assertTrue(os.path.isfile(vault_file))


class TestGetNodeContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.node = hou.node('obj').createNode('geo')

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

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy()


class TestGetNetworkContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.subnet = hou.node('obj').createNode('lopnet')
        cls.flat = hou.node('obj').createNode('geo').createNode('add')

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

    @classmethod
    def tearDownClass(cls):
        cls.subnet.destroy()
        cls.flat.destroy()

class TestReadNetworkVault(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "_test"
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
        )
        cls.filepath = os.path.join(
            cls.fixture_dir,
            cls.user,
            "networks.json"
        )

    def test_read(self):
        self.assertTrue(os.path.isfile(self.filepath))
        data = read_network_vault(self.filepath, 'r')

        network_data = data["network_A"]
        self.assertTrue(network_data["context"], "OBJ")

    def test_write(self):
        newfile = os.path.join(self.fixture_dir, self.user, "write_test.json")
        if os.path.isfile(newfile):
            os.remove(newfile)

        # Test file creation
        data = read_network_vault(newfile, 'w')
        self.assertTrue(os.path.isfile(newfile))

        # Write data, read it back
        data.update({"foo": "bar"})
        with open(newfile, 'w') as f:
            json.dump(data, f)
        data = read_network_vault(newfile, 'w')

        self.assertEqual(data["foo"], "bar")
        os.remove(newfile)

    def test_unrecognized_mode(self):
        with self.assertRaises(ValueError):
            read_network_vault(self.filepath, 'x')

    def test_bad_filepath(self):
        with self.assertRaises(ValueError):
            read_network_vault("monty", 'r')


class TestReadUserData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "_test"
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
        )

    def test_read(self):
        data = read_user_data(user=self.user, vault_dir=self.fixture_dir)
        network_data = data["network_A"]
        self.assertTrue(network_data["context"], "OBJ")

    def test_bad_user(self):
        with self.assertRaises(RuntimeError):
            read_user_data(user="lk@fs&*(12)", vault_dir=self.fixture_dir)

# delete_network_data() and remove_cpio_file() are both tested in
# integration\test_net_load.TestNetLoad.test_remove_network()


if __name__ == "__main__":
    unittest.main()
