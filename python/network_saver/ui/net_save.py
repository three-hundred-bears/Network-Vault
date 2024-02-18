"""Contains a GUI allowing a user to save their Houdini network to disk."""

import io
import os
from getpass import getuser
import json
import re
import shutil

from PySide2 import QtCore, QtWidgets
import hou

from network_saver.utility import get_vault_dir, get_node_context


class NetSaveDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NetSaveDialog, self).__init__(parent)

        self.setWindowTitle('Save Selected Network')

        form = QtWidgets.QFormLayout()

        self.title_edit = QtWidgets.QPlainTextEdit(self)
        self.title_edit.setFixedHeight(30)
        form.addRow("Network Name: ", self.title_edit)

        notes_label = QtWidgets.QLabel("Notes:")
        self.notes = QtWidgets.QPlainTextEdit(self)
        self.notes.setFixedHeight(64)
        form.addRow(notes_label)
        form.addRow(self.notes)

        self.save_button = QtWidgets.QPushButton('Ok', self)
        form.addRow(self.save_button)

        self.setLayout(form)

        self.save_button.clicked.connect(self.save_network)

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def save_network(self):

        selection = hou.selectedNodes()
        if not selection:
            hou.ui.displayMessage("No nodes selected!", severity=hou.severityType.Warning)
            return

        vault_dir = get_vault_dir()
        user = getuser()
        config_name = "networks.json"

        network_name = self.title_edit.toPlainText()  # TODO: check if network with name already exists, notify user
        network_description = self.notes.toPlainText()

        if not re.match(r'^[a-zA-Z0-9_ ]+$', network_name):
            hou.ui.displayMessage(
                "Please make ensure network name is alphanumeric!\n"
                "(only numbers, letters, spaces, or underscores)",
                severity=hou.severityType.Warning
            )
            return

        hou.copyNodesToClipboard(selection)

        context = get_node_context(selection[0])
        version = hou.applicationVersionString()

        src_file = '_'.join((context, 'copy.cpio'))
        src = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), src_file)
        dst = os.path.join(vault_dir, user, network_name + '.cpio')

        shutil.copy(src, dst)

        config_file = os.path.join(vault_dir, user, config_name)

        if not os.path.isfile(config_file):
            with open(config_file, 'x') as config_f:
                json.dump(dict(), config_f)

        with open(config_file, 'r') as config_f:
            try:
                data = json.load(config_f)
            except (Exception, io.UnsupportedOperation) as err:
                data = dict()
                print('Warning: Could not load config json at ', config_file)
                print(err)

        data.update(
            {
                network_name: {
                    'context': context,
                    'notes': network_description,
                    'version': version
                }
            }
        )

        with open(config_file, 'w') as config_f:
            json.dump(data, config_f)

        QtWidgets.QMessageBox.information(self,
            "Success", "Successfully saved network!"
        )
        self.close()


def launch():

    widget = NetSaveDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

    widget.show()
