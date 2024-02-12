"""Contains a GUI allowing a user to load their saved networks into Houdini."""

import os
from getpass import getuser
import json
import shutil

import hou

from PySide2 import QtWidgets, QtCore, QtGui

class NetLoadDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NetLoadDialog, self).__init__(parent)

        self.setWindowTitle('Load Selected Network')

        vbox = QtWidgets.QVBoxLayout()

        self.table_model = QtGui.QStandardItemModel()
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)

        self.table_model.setHorizontalHeaderLabels(
            ['Name', 'Houdini Version', 'Description']
        )
        self.table_view.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.table_view.horizontalHeader().setMaximumHeight(25)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_view.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.table_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_view.setWordWrap(True)

        for index, width in [(0, 150), (1, 150), (2, 350)]:
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
        return QtCore.QSize(600, 250)

    def load_network(self):
        print('loaded network')
        self.table_view.resizeRowsToContents()
    
    def refresh_networks(self):
        print('what')
        self.table_model.setRowCount(0)
        test_row_A = [
            QtGui.QStandardItem('bacon'),
            QtGui.QStandardItem('eggs'),
            QtGui.QStandardItem('ham')
        ]
        test_row_B = [
            QtGui.QStandardItem('mario'),
            QtGui.QStandardItem('luigi'),
            QtGui.QStandardItem('yoshi')
        ]
        self.table_model.appendRow(test_row_A)
        self.table_model.appendRow(test_row_B)

        self.table_view.resizeRowsToContents()


def launch():
    
    widget = NetLoadDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()

