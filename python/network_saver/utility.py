
from getpass import getuser
import io
import json
import os
from pathlib import Path

import hou

CATEGORY_MAP = {
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


def remap_node_categories(category_name):
    """Remap node type categories to naming convention used by CPIO files.
    
    Copying a node (or nodes) in Houdini creates a temporary CPIO file in
    $HOUDINI_TEMP_DIR, prefixed with the category of the network it was 
    copied from. This func remaps the name of the categories given by
    hou.NodeTypeCategory.name() to the convention used for these CPIO files.
    """

    conformed_cat = CATEGORY_MAP.get(category_name)
    if not conformed_cat:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to ' 
            'account for {}'.format(category_name)
            )
    return conformed_cat


def get_data_dir():
    """Fetch directory containing module data."""

    cur_dir = Path(__file__)
    return os.path.join(cur_dir.parents[2], 'data')


def get_vault_dir():
    """Fetch vault directory from text file containing it."""

    vault_file = os.path.join(
        get_data_dir(),
        'vault_dir.txt'
    )
    with open(vault_file, 'r') as f:
        return f.readline().strip()


def get_user_dir(user=None, vault_dir=None):

    vault_dir = vault_dir or get_vault_dir()
    user = user or getuser()
    return os.path.join(vault_dir, user)


def get_vault_file(user=None, vault_dir=None):
    """Fetch vault json file for given user.

    Args:
        user string: User determining which vault file to fetch.
    """

    user_dir = get_user_dir(user=user, vault_dir=vault_dir)
    vault_name = "networks.json"
    return os.path.join(user_dir, vault_name)


def get_node_context(node):
    """Get network category of given node.
    
    Args:
        node hou.Node: Node to fetch category for.
    """

    return remap_node_categories(node.type().category().name())


def get_network_context(node):
    """Get child network category of given node.
    
    Args:
        node hou.Node: Node to fetch child category for.
    """

    category = node.type().childTypeCategory()
    if not category:
        return get_node_context(node)
    return remap_node_categories(category.name())


def _make(config_file):
    """Create vault json for given user.
    
    Args:
        config_file string: Path-like object representing file to make.
        user string: User to create json file under.
    """

    user_dir = os.path.dirname(config_file)
    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)  # TODO: change mode so only user has perms
    with open(config_file, 'x') as config_f:
        json.dump(dict(), config_f)


def _notify(config_file):
    """Notify user that no vault json currently exists.
    
    Args:
        config_file string: Path-like object representing vault json that
                            should exist but doesn't.
    """

    if hou.isUIAvailable():
        hou.ui.displayMessage(
            "No networks available to load!\n"
            "Please first save a network using the network saver tool."
        )
    raise RuntimeError(
        "Network vault file {} does not exist".format(config_file)
    )


def read_network_vault(filepath, mode):
    """Read contents of vault json to dict.
    
    Args:
        filepath string: Path-like object representing vault json to read.
        mode string: Determines how to react in the event that the file does
                     not exist.
        user string: User to read vault json from.
    """

    if not os.path.splitext(filepath)[1] == ".json":
        raise ValueError(
            "Given filepath {} is not a valid json".format(filepath)
            )

    func_map = {'r': _notify, 'w': _make}
    func = func_map.get(mode)
    if not func:
        raise ValueError("Invalid filemode {}".format(mode))
    if not os.path.isfile(filepath):
        func(filepath)
        return dict()
    try:
        with open(filepath, 'r') as config_f:
            data = json.load(config_f)
    except (Exception, io.UnsupportedOperation) as err:
        data = dict()
        print('Warning: Could not load config json at ', filepath)
        print(err)
    return data
