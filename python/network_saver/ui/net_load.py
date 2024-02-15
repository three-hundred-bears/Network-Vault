"""Contains a GUI allowing a user to load their saved networks into Houdini."""

import os
from getpass import getuser
import json
import shutil

import hou

from PySide2 import QtWidgets, QtCore, QtGui

from network_saver.utility import get_vault_dir


class NetLoadDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NetLoadDialog, self).__init__(parent)

        self.setWindowTitle('Load Selected Network')

        vbox = QtWidgets.QVBoxLayout()

        self.table_model = QtGui.QStandardItemModel()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)

        self.table_model.setHorizontalHeaderLabels(
            ['Name', 'Houdini Version', 'Context', 'Description']
        )
        # self.table_view.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
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

    def load_network(self):
        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            QtWidgets.QMessageBox.critical(self,
                "Error Loading Network", "No network selected!"
            )
            return

        vault_dir = get_vault_dir()  # TODO: store this as property?
        user = getuser()

        name = indexes[0].data(QtCore.Qt.UserRole)
        context = indexes[2].data(QtCore.Qt.UserRole)
        print('got ', name, ' of context ', context)

        dst_file = '_'.join((context, 'copy.cpio'))
        dst = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), dst_file)
        src = os.path.join(vault_dir, user, name + '.cpio')

        # TODO: validate network pane to ensure it matches context of loaded network

        shutil.copy(src, dst)

        network_pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

        # TODO: put a netbox around the resulting nodes?
        hou.pasteNodesFromClipboard(network_pane.pwd())

        QtWidgets.QMessageBox.information(self,
            "Success", "Successfully loaded network!"
        )
        self.close()

    def refresh_networks(self):
        self.table_model.setRowCount(0)

        vault_dir = get_vault_dir()
        user = getuser()
        config_name = "networks.json"

        config_file = os.path.join(vault_dir, user, config_name)
        with open(config_file, 'r') as config_f:
            try:
                data = json.load(config_f)
            except Exception as err:  # TODO: cast a smaller yet, maybe
                data = dict()
                print('Warning: Could not load config json at ', config_file)
                print(err)

        for name, meta in data.items():
            name_item = QtGui.QStandardItem(name)
            name_item.setData(name, QtCore.Qt.UserRole)
            version_item = QtGui.QStandardItem(meta['version'])
            context_item = QtGui.QStandardItem(meta['context'])
            context_item.setData(meta['context'], QtCore.Qt.UserRole)
            notes_item = QtGui.QStandardItem(meta['notes'])

            row = [name_item, version_item, context_item, notes_item]

            self.table_model.appendRow(row)

            self.table_view.resizeRowsToContents()


def launch():
    
    widget = NetLoadDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()

