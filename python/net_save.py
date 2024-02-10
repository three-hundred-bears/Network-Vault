"""Contains a GUI allowing a user to save their Houdini network to disk."""

from PySide2 import QtCore, QtWidgets
import hou


class NetSaveDialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(NetSaveDialog, self).__init__(parent)

        self.setWindowTitle('Save Network')

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
        print('network saved')


def launch():

    widget = NetSaveDialog()
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

    widget.show()
