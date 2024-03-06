
import os
import json
import shutil
import sys
import unittest

import hou
from PySide2 import QtWidgets

from network_saver.ui.net_save import NetSaveDialog
from network_saver.utility import *

class TestNetSave(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tmp_dir = os.path.join(
            os.getenv('LOCALAPPDATA'),
            "Temp",
            "houdini_temp"
        )
        os.environ['HOUDINI_TEMP_DIR'] = tmp_dir

        test_node = hou.node('obj').createNode('geo')
        test_node.setSelected(True, clear_all_selected=True)
        cls.selection = hou.selectedNodes()
        cls.user = "_test"

        try:
            test_dir = get_user_dir(user=cls.user)
            os.mkdir(test_dir)
        except FileExistsError:
            shutil.rmtree(test_dir)
            os.mkdir(test_dir)

        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            sys.argv
        )
        cls.dialog = NetSaveDialog(user=cls.user)

    def test_get_network_data(self):
        notes = "test notes"
        version = hou.applicationVersionString()
        context = get_node_context(self.selection[0])
        self.dialog.notes.setPlainText(notes)

        result = self.dialog.get_network_data(self.selection)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["context"], context)
        self.assertEqual(result["notes"], notes)
        self.assertEqual(result["version"], version)

    def test_get_network_name(self):
        # test valid input
        valid_name = "my name"
        self.dialog.title_edit.setPlainText(valid_name)
        result = self.dialog.get_network_name(dict())
        self.assertEqual(result, "my_name")

        # test existing name
        with self.assertRaises(RuntimeError):
            self.dialog.get_network_name({"my_name" : "notes or whatever"})

        # test invalid input
        invalid_name = "my name!"
        self.dialog.title_edit.setPlainText(invalid_name)
        with self.assertRaises(RuntimeError):
            self.dialog.get_network_name(dict())


    def test_save_network(self):
        notes = "test notes"
        network_name = "test name"
        conformed_name = "test_name"

        context = get_node_context(self.selection[0])
        version = hou.applicationVersionString() 

        self.dialog.notes.setPlainText(notes)
        self.dialog.title_edit.setPlainText(network_name)


        self.dialog.save_network()

        vault_file = get_vault_file(user=self.user)
        vault_dir = os.path.dirname(vault_file)

        # ensure cpio file was saved to correct location
        self.assertTrue(os.path.isfile(
            os.path.join(vault_dir, "test_name.cpio")
        ))

        self.assertTrue(os.path.isfile(vault_file))

        _head, tail = os.path.splitext(vault_file)
        self.assertEqual(tail, ".json")

        with open(vault_file, 'r') as f:
            data = json.load(f)

            self.assertIn(conformed_name, data)
            network_data = data[conformed_name]
            self.assertEqual(network_data["notes"], notes)
            self.assertEqual(network_data["context"], context)
            self.assertEqual(network_data["version"], version)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        shutil.rmtree(get_user_dir(user=cls.user))


