
import os
import json
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
        cls.vault_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
        )
        # save test .json with two networks
        cls.app = QtWidgets.QApplication(sys.argv)
        cls.dialog = NetLoadDialog(user=cls.user, root=cls.vault_dir)
    

