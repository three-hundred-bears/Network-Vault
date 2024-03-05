
import os
import json
from pathlib import Path
import shutil
import sys
import unittest

import hou
from PySide2 import QtWidgets

from network_saver.ui.net_load import NetLoadDialog
from network_saver.utility import *

class TestNetLoad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "_test"
        cls.vault_dir = os.path.join(  # TODO: remove now that we have vault file?
            Path(__file__).parents[1],
            "fixtures",
        )

        # insert dummy data for removal test
        cls.vault_file = get_vault_file(user=cls.user, vault_dir=cls.vault_dir)
        data = read_network_vault(cls.vault_file, 'r')
        data.update({"network_C": {
            "context": "SOP",
            "notes": "notes C",
            "version": "20.0.506"
        }})
        with open(cls.vault_file, 'w') as f:
            json.dump(data, f)

        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        cls.dialog = NetLoadDialog(user=cls.user, root=cls.vault_dir)

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

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
