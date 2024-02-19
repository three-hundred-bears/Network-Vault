"""Contains a GUI allowing a user to load their saved networks into Houdini."""

import os
from getpass import getuser
import shutil

import hou

from PySide2 import QtWidgets, QtCore, QtGui

import network_saver.utility


class NetLoadDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NetLoadDialog, self).__init__(parent)

        # TODO: add support for browsing networks of other users

        self.setWindowTitle('Load Selected Network')

        vbox = QtWidgets.QVBoxLayout()

        self.table_model = QtGui.QStandardItemModel()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)

        self.table_model.setHorizontalHeaderLabels(
            ['Name', 'Houdini Version', 'Context', 'Description']
        )

        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setMaximumHeight(25)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_view.setWordWrap(True)

        for index, width in [(0, 150), (1, 150), (2, 60), (3, 350)]:
            self.table_view.setColumnWidth(index, width)

        self.table_view.setShowGrid(False)
        self.table_view.setWordWrap(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.load_button = QtWidgets.QPushButton('Ok', self)

        vbox.addWidget(self.table_view)
        vbox.addWidget(self.load_button)

        self.setLayout(vbox)

        self.load_button.clicked.connect(self.load_network)

        self.refresh_networks()

    def sizeHint(self):

        return QtCore.QSize(700, 250)

    def _get_current_selection(self):

        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            hou.ui.displayMessage(
                "No network selected!",
                severity=hou.severityType.Error
            )
            raise RuntimeError("No network selected")

        return indexes

    def _get_network_data(self):

        indexes = self._get_current_selection()
        name = indexes[0].data(QtCore.Qt.UserRole)
        context = indexes[2].data(QtCore.Qt.UserRole)

        return name, context

    def _validate_network_editor(self, current_network, expected_context):

        if not current_network.isEditable():
            hou.ui.displayMessage(
                "Cannot load into a locked editor!",
                severity=hou.severityType.Error
            )
            raise RuntimeError("Current network editor is locked")

        network_context = network_saver.utility.get_network_context(
            current_network
        )

        if not network_context == expected_context:
            hou.ui.displayMessage(
                "Current context does not match selected network!\n"
                "Navigate to the desired location in the network editor.",
                severity=hou.severityType.Error
            )
            raise RuntimeError(
                "Network editor category does not match network category"
            )

    def _paste_selected_network(self, name, context, network_pane):

        vault_dir = network_saver.utility.get_vault_dir()
        user = getuser()
        dst_file = '_'.join((context, 'copy.cpio'))
        dst = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), dst_file)
        src = os.path.join(vault_dir, user, name + '.cpio')
        shutil.copy(src, dst)

        hou.pasteNodesFromClipboard(network_pane.pwd())

    def _wrap_selection_in_netbox(self, name, cur_network):

        netbox = cur_network.createNetworkBox()
        netbox.setName(name)
        netbox.setComment(name)
        netbox.setColor(hou.selectedNodes()[0].color())
        for node in hou.selectedNodes():
            netbox.addNode(node)
        netbox.fitAroundContents()

    def load_network(self):

        try:
            name, context = self._get_network_data()
            network_pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            cur_network = network_pane.pwd()
            self._validate_network_editor(cur_network, context)
        except RuntimeError:
            return

        self._paste_selected_network(name, context, network_pane)

        self._wrap_selection_in_netbox(name, cur_network)

        hou.ui.displayMessage(
            "Successfully loaded network!"
        )
        self.close()

    def _append_network_row(self, network_name, network_data):

        name_item = QtGui.QStandardItem(network_name)
        name_item.setData(network_name, QtCore.Qt.UserRole)
        version_item = QtGui.QStandardItem(network_data['version'])
        context_item = QtGui.QStandardItem(network_data['context'])
        context_item.setData(network_data['context'], QtCore.Qt.UserRole)
        notes_item = QtGui.QStandardItem(network_data['notes'])

        row = [name_item, version_item, context_item, notes_item]

        self.table_model.appendRow(row)

    def refresh_networks(self):

        self.table_model.setRowCount(0)

        vault_file = network_saver.utility.get_vault_file()
        try:
            data = network_saver.utility.read_network_vault(vault_file, 'r')
        except RuntimeError:
            self.close()

        if not data:
            hou.ui.displayMessage(
                "No networks available to load!\n"
                "Please first save a network using the network saver tool.",
                severity=hou.severityType.Error
            )
            self.close()  # TODO: does this work if we haven't called show() yet?

        for name, meta in data.items():
            self._append_network_row(name, meta)

        self.table_view.resizeRowsToContents()


def launch():

    widget = NetLoadDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()
