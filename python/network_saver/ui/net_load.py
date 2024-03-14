"""Contains a GUI allowing a user to load their saved networks into Houdini."""

import os
from getpass import getuser
import shutil

import hou

from PySide2 import QtWidgets, QtCore, QtGui

import network_saver.utility


class NetLoadDialog(QtWidgets.QWidget):
    """GUI allowing user to load saved networks into Houdini."""
    def __init__(self, parent=None, user=None, root=None):
        """Initializes NetLoad GUI.

        Args:
            user str: User to initialize GUI under.
            root str: Path-like object representing vault location.
        """
        super(NetLoadDialog, self).__init__(parent)

        self.setWindowTitle('Load Selected Network')

        self.vault_dir = root or network_saver.utility.get_vault_dir()
        self.user = user or getuser()

        vbox = QtWidgets.QVBoxLayout()

        # user selection
        hbox = QtWidgets.QHBoxLayout()
        user_label = QtWidgets.QLabel(self)
        user_label.setText('User:')
        self.user_combobox = QtWidgets.QComboBox(self)
        hbox.addWidget(user_label)
        hbox.addWidget(self.user_combobox)
        hbox.addStretch()

        # network removal
        self.remove_button = QtWidgets.QPushButton('Remove Network', self)
        hbox.addWidget(self.remove_button)

        # setup table model 
        self.table_model = QtGui.QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(
            ['Name', 'Houdini Version', 'Context', 'Description']
        )

        # setup table view
        self.table_view = QtWidgets.QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setMaximumHeight(25)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setHorizontalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.table_view.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.table_view.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.table_view.setWordWrap(True)
        for index, width in [(0, 150), (1, 150), (2, 60), (3, 350)]:
            self.table_view.setColumnWidth(index, width)
        self.table_view.setShowGrid(False)
        self.table_view.setWordWrap(True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )
        self.table_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        self.load_button = QtWidgets.QPushButton('Load Network', self)

        # layout
        vbox.addLayout(hbox)
        vbox.addWidget(self.table_view)
        vbox.addWidget(self.load_button)
        self.setLayout(vbox)

        # preflight 
        self.refresh_networks()
        self._populate_users()
        self._set_current_user()

        # connections
        self.load_button.clicked.connect(self.load_network)
        self.remove_button.clicked.connect(self.remove_network)
        self.user_combobox.currentIndexChanged.connect(
            self._handle_user_change
        )

    def sizeHint(self):
        """GUI dimensions."""

        return QtCore.QSize(700, 250)

    def _handle_user_change(self):
        """Update relevant fields based on current user selection."""

        self.user = self.user_combobox.currentText()
        self.refresh_networks()

    def _set_current_user(self):
        """Set user property to current user. Meant to run once during init."""

        index = self.user_combobox.findText(self.user)
        if index == -1:
            return
        self.user_combobox.setCurrentIndex(index)

    def _validate_user_dir(self, folder):
        """Filter func to ensure user directory both exists and contains 
           network json.

        Args:
            folder: String representing file/folder present in vault dir.
        Returns:
            bool: Value representing validation status.
        """

        full_path = os.path.join(self.vault_dir, folder)
        if not os.path.isdir(full_path):
            return False
        children = os.listdir(full_path)
        if "networks.json" not in children:
            return False
        return True

    def _populate_users(self):
        """Populate user combobox based on contents of vault dir."""

        user_dirs = filter(self._validate_user_dir, os.listdir(self.vault_dir))
        self.user_combobox.addItems(user_dirs)

    def get_current_selection(self):
        """Get currently selected network as row of indexes.

        Returns:
            tuple: Collection of selected row indexes.
        """

        indexes = self.table_view.selectionModel().selectedIndexes()
        if not indexes:
            if hou.isUIAvailable():
                hou.ui.displayMessage(
                    "No network selected!",
                    severity=hou.severityType.Error
                )
            raise RuntimeError("No network selected")

        return indexes

    def get_network_data(self):
        """Fetch data associated with selected network.

        Returns:
            str: Name of selected network.
            str: Category of selected network.
        """

        indexes = self.get_current_selection()
        name = indexes[0].data(QtCore.Qt.UserRole)
        context = indexes[2].data(QtCore.Qt.UserRole)

        return name, context

    def _validate_root_network(self, current_network, expected_context):
        """Ensure current network editor is same category as selected network.

        Args:
            current_network hou.paneTab: Current network editor.
            expected_context string: Representation of current network
                                     category.
        """

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

    def _paste_selected_network(self, name, context, cur_network):
        """Load selected network from clipboard.

        Args:
            name string: name of selected network
            context string: Representation of current network category.
            network_pane hou.paneTabType.NetworkEditor: Current network editor.
        """

        dst_file = '_'.join((context, 'copy.cpio'))
        dst = os.path.join(os.getenv('HOUDINI_TEMP_DIR'), dst_file)
        src = os.path.join(self.vault_dir, self.user, name + '.cpio')
        shutil.copy(src, dst)

        hou.pasteNodesFromClipboard(cur_network)

    def _wrap_selection_in_netbox(self, name, cur_network):
        """Create netbox around recently created network.

        Args:
            name string: Name of netbox.
            cur_network hou.Node: Current network location.
        """

        netbox = cur_network.createNetworkBox()
        netbox.setName(name)
        netbox.setComment(name)
        netbox.setColor(hou.selectedNodes()[0].color())
        for node in hou.selectedNodes():
            netbox.addNode(node)
        netbox.fitAroundContents()
    
    @staticmethod
    def _get_cur_network():
        """Get root node of current active network editor pane

        Returns:
            hou.Node: Root node of current network editor.
        """
        network_pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        return network_pane.pwd()

    def load_network(self, root_network=None):
        """Import selected network into active network editor pane."""

        if not root_network and not hou.isUIAvailable():
            raise RuntimeError(
                "Must explicitly pass a root network in" 
                "non-GUI sessions of Houdini"
            )

        try:
            name, context = self.get_network_data()
            cur_network = root_network or self._get_cur_network()
            self._validate_root_network(cur_network, context)
        except RuntimeError:
            # assume we failed network validation
            return

        self._paste_selected_network(name, context, cur_network)

        self._wrap_selection_in_netbox(name, cur_network)

        if hou.isUIAvailable():
            hou.ui.displayMessage(
                "Successfully loaded network!"
            )
        self.close()

    def remove_network(self):
        """Remove network from GUI and associated json file."""

        try:
            name, _context = self.get_network_data()
        except RuntimeError:
            # assume no network was selected
            return

        if hou.isUIAvailable() and not hou.ui.displayConfirmation(
            "Are you sure you want to remove this network?", 
            severity=hou.severityType.Warning
        ):
            return

        # remove network from json
        network_saver.utility.delete_network_data(
            name, user=self.user, vault_dir=self.vault_dir
        )

        # remove cpio file
        network_saver.utility.remove_cpio_file(
            name, user=self.user, vault_dir=self.vault_dir
        )

        try:
            self.refresh_networks()
        except RuntimeError:
            self.close()

    def _construct_network_row(self, network_name, network_data):
        """Create row representation of given network data.
        
        Args:
            network_name str: Name of network being added.
            network_data dict: Map of relevant network data, including Houdini
                               version, category, and description.
        Returns:
            list: List of QStandardItems representing network row in GUI.
        """

        name_item = QtGui.QStandardItem(network_name)
        name_item.setData(network_name, QtCore.Qt.UserRole)
        version_item = QtGui.QStandardItem(network_data['version'])
        context_item = QtGui.QStandardItem(network_data['context'])
        context_item.setData(network_data['context'], QtCore.Qt.UserRole)
        notes_item = QtGui.QStandardItem(network_data['notes'])

        row = [name_item, version_item, context_item, notes_item]
        for item in row:
            item.setEditable(False)
        
        return row

    def _append_network_row(self, network_name, network_data):
        """Add network as row to GUI, with relevant data stored in associated
           columns.

        Args:
            network_name string: Name of network being added.
            network_data dict: Map of relevant network data, including Houdini
                               version, category, and description.
        """

        row = self._construct_network_row(network_name, network_data)

        self.table_model.appendRow(row)

    def refresh_networks(self):
        """Refresh networks displayed by GUI."""

        self.table_model.setRowCount(0)

        data = network_saver.utility.read_user_data(
            user=self.user, vault_dir=self.vault_dir
        )

        if not data:
            if hou.isUIAvailable():
                hou.ui.displayMessage(
                    "No networks available to load!\n"
                    "Please first save a network using the network saver tool.",
                    severity=hou.severityType.Error
                )
            raise RuntimeError("Network vault empty")

        for name, meta in data.items():
            self._append_network_row(name, meta)

        self.table_view.resizeRowsToContents()


def launch():
    """Launch GUI, parenting to Houdini main window."""

    try:
        widget = NetLoadDialog()
    except RuntimeError as err:
        print("Failed to open NetLoad dialog:\n{}".format(err))
        return
    widget.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    widget.show()
