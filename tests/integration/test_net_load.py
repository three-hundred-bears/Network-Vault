
import os
import json
from pathlib import Path
from shutil import copy as shcopy
import sys
import unittest

import hou
from PySide2 import QtWidgets, QtCore

from network_saver.ui.net_load import NetLoadDialog
from network_saver.utility import *

def _add_network(file, name, data):
    network_data = read_network_vault(file, 'r')
    network_data.update({name: data})
    with open(file, 'w') as f:
        json.dump(network_data, f)

def _remove_network(file, name):
    network_data = read_network_vault(file, 'r')
    try:
        network_data.pop(name)
    except KeyError:
        pass
    with open(file, 'w') as f:
        json.dump(network_data, f)

class TestNetLoad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        tmp_dir = os.path.join(
            os.getenv('LOCALAPPDATA'),
            "Temp",
            "houdini_temp"
        )
        os.environ['HOUDINI_TEMP_DIR'] = tmp_dir
        cls.user = "_test"
        vault_dir = os.path.join(
            Path(__file__).parents[1],
            "fixtures",
        )

        # insert dummy data for removal test
        cls.vault_file = get_vault_file(user=cls.user, vault_dir=vault_dir)
        data = read_network_vault(cls.vault_file, 'r')
        data.update({"network_C": {
            "context": "SOP",
            "notes": "notes C",
            "version": "20.0.506"
        }})
        with open(cls.vault_file, 'w') as f:
            json.dump(data, f)
        src = os.path.join(vault_dir, cls.user, "network_A.cpio")
        dst = os.path.join(vault_dir, cls.user, "network_C.cpio")
        shcopy(src, dst)

        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            sys.argv
        )
        cls.dialog = NetLoadDialog(user=cls.user, root=vault_dir)
    
    def test_get_current_selection(self):

        with self.assertRaises(RuntimeError):
            self.dialog.get_current_selection()
        self.dialog.table_view.selectRow(0)
        indexes = self.dialog.get_current_selection()
        self.assertEqual(len(indexes), 4)
        self.assertEqual(indexes[0].data(QtCore.Qt.UserRole), "network_A")
        self.assertEqual(indexes[2].data(QtCore.Qt.UserRole), "OBJ")


    def test_remove_network(self):
        # ensure setUp ran correctly
        old_data = read_network_vault(self.vault_file, 'r')
        self.assertIn("network_C", old_data.keys())

        # remove network_C from GUI/json
        self.dialog.table_view.selectRow(2)
        self.dialog.remove_network()

        # ensure it's gone again
        data = read_network_vault(self.vault_file, 'r')
        networks = data.keys()
        self.assertEqual(len(networks), 2)
        self.assertNotIn("network_C", networks)

    def test_load_network(self):

        self.dialog.table_view.selectRow(0)
        network_name = self.dialog.get_network_data()[0]
        self.dialog.load_network(root_network=hou.node('obj'))

        # network should just be a single geometry object
        self.assertEqual(len(hou.selectedNodes()), 1)
        geo = hou.selectedNodes()[0]
        self.assertEqual(geo.name(), "geo1")
        netbox = geo.parentNetworkBox()
        self.assertIsNotNone(netbox)
        self.assertEqual(network_name, netbox.comment())

    def test_refresh_networks(self):
        self.assertEqual(self.dialog.table_model.rowCount(), 3)
        network_name = "network_D"
        data = {
            "context": "DOP",
            "notes": "notes D",
            "version": "20.0.506"
        }

        _add_network(self.vault_file, network_name, data)
        self.dialog.refresh_networks()
        self.assertEqual(self.dialog.table_model.rowCount(), 4)
        _remove_network(self.vault_file, network_name)

    def test_get_network_data(self):

        self.dialog.table_view.selectRow(1)
        name, context = self.dialog.get_network_data()
        self.assertEqual(name, "network_B")
        self.assertEqual(context, "SOP")

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
