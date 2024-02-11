"""Contains a GUI allowing a user to save their Houdini network to disk."""

import os
from getpass import getuser
import json
import shutil

from PySide2 import QtCore, QtWidgets
import hou


def get_data_dir():
    current_dir = os.path.realpath(__file__)
    return os.path.join(
        os.path.dirname(os.path.dirname(current_dir)),
        'data'
    )


def get_vault_dir():
    vault_file = os.path.join(
        get_data_dir(),
        'vault_dir.txt'
    )
    with open(vault_file, 'r') as f:
        return f.readline().strip()


def conform_network_context(context):
    map = {
        'Shop': 'SHOP',
        'CopNet': 'IMG',
        'Cop2': 'COP2',
        'ChopNet': 'CHOPNET',
        'Chop': 'CHOP',
        'Object': 'OBJ',
        'Driver': 'ROP', 
        'Sop': 'SOP',
        'Vop': 'VOP',
        'Lop': 'LOP',
        'TopNet': 'TOPNET',
        'Top': 'TOP',
        'Dop': 'DOP'
    }
    conformed_context = map.get(context)
    if not conformed_context:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to account for {}'.format(context)
            )
    return conformed_context


def get_network_context(network):

    node_category = network[0].type().category().name()
    return node_category
    


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

        hou.copyNodesToClipboard(selection)

        context = conform_network_context(get_network_context(selection))
        version = hou.applicationVersionString()

        vault_dir = get_vault_dir()
        user = getuser()
        config_name = "networks.json"

        # TODO: validate network name so no weird characters fuck up the filesystem
        network_name = self.title_edit.toPlainText()  # TODO: check if network with name already exists, notify user
        network_description = self.notes.toPlainText()

        src_file = '_'.join((context, 'copy.cpio'))
        src = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), src_file)
        dst = os.path.join(vault_dir, user, network_name + '.cpio')

        shutil.copy(src, dst)

        config_file = os.path.join(vault_dir, user, config_name)

        with open(config_file, 'w') as config_f:
            try:
                data = json.load(config_f)
            except:  # TODO: cast a smaller net, maybe
                data = dict()

            data.update(
                {
                    network_name: {
                        'context': context,
                        'notes': network_description,
                        'version': version
                    }
                }
            )
            json.dump(data, config_f)
        print('save successful')


def launch():

    widget = NetSaveDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

    widget.show()
