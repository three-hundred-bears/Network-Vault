"""Contains a GUI allowing a user to save their Houdini network to disk."""

import os
from getpass import getuser
import json
import re
import shutil

from PySide2 import QtCore, QtWidgets
import hou

import network_saver.utility


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
    
    def _get_selected_nodes(self):

        selection = hou.selectedNodes()
        if not selection:
            hou.ui.displayMessage(
                "No nodes selected!", severity=hou.severityType.Warning
                )
            raise RuntimeError("No nodes selected")
        return selection
    
    def _get_network_name(self, data):

        network_name = self.title_edit.toPlainText()
        if not re.match(r'^[a-zA-Z0-9_ ]+$', network_name):
            hou.ui.displayMessage(
                "Please make ensure network name is alphanumeric!\n"
                "(only numbers, letters, spaces, or underscores)",
                severity=hou.severityType.Warning
            )
            raise RuntimeError("Invalid network name")
        if network_name in data.keys() and not hou.ui.displayConfirmation(
            "Network with this name already exists!\n"
            "Would you like to replace it?"
        ):
            raise RuntimeError("Operation aborted")

        return network_name
    
    def _move_network_file(self, vault_dir, context, user, network_name):

        src_file = '_'.join((context, 'copy.cpio'))
        src = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), src_file)
        dst = os.path.join(vault_dir, user, network_name + '.cpio')
        shutil.copy(src, dst)


    def _get_network_data(self, selection):

        notes = self.notes.toPlainText()
        context = network_saver.utility.get_node_context(selection[0])
        version = hou.applicationVersionString()
        return {'context': context, 'notes': notes, "version": version}


    def _write_network_data(
            self, config_file, data, network_name, network_data):

        data.update({network_name: network_data})
        with open(config_file, 'w') as config_f:
            json.dump(data, config_f)


    def save_network(self):

        try:
            selection = self._get_selected_nodes()
        except RuntimeError:
            return

        vault_file = network_saver.utility.get_vault_file()
        data = network_saver.utility.read_network_vault(vault_file, 'w')

        try:
            network_name = self._get_network_name(data)
        except RuntimeError:
            return

        network_data = self._get_network_data(selection)

        hou.copyNodesToClipboard(selection)  # <-- creates CPIO file
        vault_dir = network_saver.utility.get_vault_dir()
        user = getuser()
        self._move_network_file(
            vault_dir, network_data['context'], user, network_name
        )

        self._write_network_data(vault_file, data, network_name, network_data)

        hou.ui.displayMessage(
            "Successfully saved network!"
        )
        self.close()


def launch():

    try:
        widget = NetSaveDialog()
    except RuntimeError as err:
        print("Failed to open NetSave dialog:\n{}".format(err))
        return
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()
