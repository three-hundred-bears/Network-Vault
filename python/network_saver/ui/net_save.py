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
    """GUI allowing user to save selected networks to be loaded later."""
    def __init__(
            self, parent: QtWidgets.QWidget=None, 
            user: str=None, root: str=None
        ) -> None:
        """Initializes NetSave GUI.

        Args:
            user str: User to initialize GUI under.
            root str: Path-like object representing vault location.
        """
        super(NetSaveDialog, self).__init__(parent)

        self.setWindowTitle('Save Selected Network')

        self.vault_dir: str = root or network_saver.utility.get_vault_dir()
        self.user: str = user or getuser()

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()

        # network naming
        self.title_edit: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit(self)
        self.title_edit.setFixedHeight(30)

        # network description
        notes_label: QtWidgets.QLabel = QtWidgets.QLabel("Notes:")
        self.notes: QtWidgets.QPlainTextEdit = QtWidgets.QPlainTextEdit(self)
        self.notes.setFixedHeight(64)

        self.save_button: QtWidgets.QPushButton = QtWidgets.QPushButton('Ok', self)

        form.addRow("Network Name: ", self.title_edit)
        form.addRow(notes_label)
        form.addRow(self.notes)
        form.addRow(self.save_button)
        self.setLayout(form)

        self.save_button.clicked.connect(self.save_network)

    def sizeHint(self) -> QtCore.QSize:
        """GUI dimensions."""

        return QtCore.QSize(400, 100)

    def get_selected_nodes(self) -> tuple[hou.OpNode]:
        """Fetch currently selected nodes.
        
        Returns:
            tuple: Collection of currently selected nodes.
        """

        selection: tuple[hou.OpNode] = hou.selectedNodes()
        if not selection:
            if hou.isUIAvailable():
                hou.ui.displayMessage(
                    "No nodes selected!", severity=hou.severityType.Warning
                )
            raise RuntimeError("No nodes selected")
        return selection

    def validate_network_name(self, network_name: str, data: dict[str, str]) -> None:
        """Validate given network name against given network data.

        Ensure given network name conforms to convention that won't conflict
        with Houdini's restriction on node names.

        Args:
            network_name str: Name of network to be validated.
            data dict: Map of currently saved networks to their relevant data.
        """

        if not re.match(r'^[a-zA-Z0-9_ ]+$', network_name):
            if hou.isUIAvailable():
                hou.ui.displayMessage(
                    "Please make ensure network name is alphanumeric!\n"
                    "(only numbers, letters, spaces, or underscores)",
                    severity=hou.severityType.Warning
                )
            raise RuntimeError("Invalid network name")
        if network_name in data.keys(): 
            if hou.isUIAvailable() and hou.ui.displayConfirmation(
                "Network with this name already exists!\n"
                "Would you like to replace it?"
            ):
                return
            raise RuntimeError("Operation aborted")

    def get_network_name(self, data: dict[str, str]) -> str:
        """Fetch and validate given network name from GUI.
        
        Args:
            data dict: Map of currently saved networks to their relevant data.
        Returns:
            str: Name of network to be saved.
        """

        network_name: str = self.title_edit.toPlainText().replace(" ", "_")
        self.validate_network_name(network_name, data)

        return network_name
    
    def _move_network_file(self, vault_dir: str, context: str, network_name: str) -> None:
        """Copy currently stored CPIO file to vault directory.
        
        Args:
            vault_dir string: Path-like object representing "vault" directory.
            context string: Category of current network file.
            network_name string: Given name of network being copied.
        """

        src_file: str = '_'.join((context, 'copy.cpio'))
        src: str = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), src_file)
        dst: str = os.path.join(vault_dir, self.user, network_name + '.cpio')
        shutil.copy(src, dst)

    def get_network_data(self, selection: tuple[hou.Node]) -> dict[str, str]:
        """Compile relevant data on current network.
        
        Args:
            selection tuple: Collection of hou.Node objects representing
                             currently selected network.
        Returns:
            dict: Relevant data of network to be saved.
        """

        notes: str = self.notes.toPlainText()
        context: str = network_saver.utility.get_node_context(selection[0])
        version: str = hou.applicationVersionString()
        return {'context': context, 'notes': notes, "version": version}

    def _write_network_data(
            self, config_file: str, data: dict[str, dict[str, str]], 
            network_name: str, network_data: dict[str, str]
        ) -> None:
        """Update network json with data associated with current network.

        Args:
            config_file string: Path-like object representing config file to 
                                save to.
            data dict: Map of previously saved networks to their relevant data.
            network_name string: Name of network currently being saved.
            network_data dict: Map of name of network to its relevant data.
        """

        data.update({network_name: network_data})
        with open(config_file, 'w') as config_f:
            json.dump(data, config_f)

    def save_network(self) -> None:
        """Save network currently selected in GUI to json located on disk."""

        try:
            selection: tuple[hou.Node] = self.get_selected_nodes()
        except RuntimeError:
            return

        vault_file: str = network_saver.utility.get_vault_file(user=self.user)
        data: dict[str, dict[str, str]] = network_saver.utility.read_network_vault(vault_file, 'w')

        try:
            network_name: str = self.get_network_name(data)
        except RuntimeError:
            return

        network_data: dict[str, str] = self.get_network_data(selection)

        hou.copyNodesToClipboard(selection)  # <-- creates CPIO file
        vault_dir: str = network_saver.utility.get_vault_dir()
        self._move_network_file(
            vault_dir, network_data['context'], network_name
        )

        self._write_network_data(vault_file, data, network_name, network_data)

        if hou.isUIAvailable():
            hou.ui.displayMessage(
                "Successfully saved network!"
            )
        self.close()

def launch() -> None:
    """Launch GUI, parenting to Houdini main window."""

    try:
        widget: NetSaveDialog = NetSaveDialog()
    except RuntimeError as err:
        print("Failed to open NetSave dialog:\n{}".format(err))
        return
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()
