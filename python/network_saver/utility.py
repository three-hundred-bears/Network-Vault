"""Common I/O functions and file read operations."""

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


def remap_node_categories(category_name: str) -> str:
    """Remap node type categories to naming convention used by CPIO files.
    
    Copying a node (or nodes) in Houdini creates a temporary CPIO file in
    $HOUDINI_TEMP_DIR, prefixed with the category of the network it was 
    copied from. This func remaps the name of the categories given by
    hou.NodeTypeCategory.name() to the convention used for these CPIO files.

    Args:
        category_name str: Node category to be remapped.
    Returns:
        str: Remapped node category.
    """

    conformed_cat: str = CATEGORY_MAP.get(category_name)
    if not conformed_cat:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to ' 
            'account for {}'.format(category_name)
            )
    return conformed_cat


def get_data_dir() -> str:
    """Fetch directory containing module data.
    
    Returns:
        str: Path-like object representing data directory of project.
    """

    cur_dir: Path = Path(__file__)
    return os.path.join(cur_dir.parents[2], 'data')


def get_vault_dir() -> str:
    """Fetch vault directory from text file containing it.

    Returns:
        str: First line in vault_dir.txt, ideally pointing to root vault 
             vault directory.
    """

    vault_file: str = os.path.join(
        get_data_dir(),
        'vault_dir.txt'
    )
    with open(vault_file, 'r') as f:
        vault_path: Path = Path(f.readline().strip())
    if vault_path.is_absolute():
        return str(vault_path)
    cur_dir: Path = Path(__file__)
    project_dir: str = cur_dir.parents[2]
    return os.path.join(project_dir, str(vault_path))


def get_user_dir(user: str=None, vault_dir: str=None) -> str:
    """Fetch user directory from vault location.
    
    Args:
        user string: User to fetch dir for
        vault_dir string: Path-like object representing current vualt location
    """

    vault_dir: str = vault_dir or get_vault_dir()
    user: str = user or getuser()
    return os.path.join(vault_dir, user)


def get_vault_file(user=None, vault_dir=None) -> str:
    """Fetch vault json file for given user.

    Args:
        user string: User determining which vault file to fetch.
    """

    user_dir: str = get_user_dir(user=user, vault_dir=vault_dir)
    vault_name: str = "networks.json"
    return os.path.join(user_dir, vault_name)


def get_node_context(node: hou.Node) -> str:
    """Get network category of given node.
    
    Args:
        node hou.Node: Node to fetch category for.
    Returns:
        str: Remapped category of given node.
    """

    return remap_node_categories(node.type().category().name())


def get_network_context(node: hou.Node) -> str:
    """Get child network category of given node.

    Args:
        node hou.Node: Node to fetch child category for.
    Returns: Remapped category of internal network of given node.
    """

    category: hou.NodeTypeCategory = node.type().childTypeCategory()
    if not category:
        return get_node_context(node)
    return remap_node_categories(category.name())


def _make(config_file: str) -> None:
    """Create vault json for given user.
    
    Args:
        config_file string: Path-like object representing file to make.
        user string: User to create json file under.
    """

    user_dir: str = os.path.dirname(config_file)
    if not os.path.isdir(user_dir):
        os.makedirs(user_dir, mode=0o644)
    with open(config_file, 'x') as config_f:
        json.dump(dict(), config_f)


def _notify(config_file: str) -> None:
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


def read_network_vault(filepath: str, mode: str) -> dict:
    """Read contents of vault json to dict.
    
    Args:
        filepath string: Path-like object representing vault json to read.
        mode string: Determines how to react in the event that the file does
                     not exist.
        user string: User to read vault json from.
    Returns:
        dict: Dict representation of contents of given filepath.
    """

    if not os.path.splitext(filepath)[1] == ".json":
        raise ValueError(
            "Given filepath {} is not a valid json".format(filepath)
            )

    func_map: dict = {'r': _notify, 'w': _make}
    func: function = func_map.get(mode)
    if not func:
        raise ValueError("Invalid filemode {}".format(mode))
    if not os.path.isfile(filepath):
        func(filepath)
        return dict()
    try:
        with open(filepath, 'r') as config_f:
            data: dict = json.load(config_f)
    except (Exception, io.UnsupportedOperation) as err:
        data: dict = dict()
        print('Warning: Could not load config json at ', filepath)
        print(err)
    return data


def read_user_data(user: str=None, vault_dir: str=None) -> dict:
    """Read network vault data for given user.
    
    Args:
        user str: User to retrieve data for.
        vault_dir str: Path-like object to vault directory.
    Returns:
        dict: Dict representation of network data for given user.
    """

    user: str = user or getuser()
    vault_dir: str = vault_dir or get_vault_dir()
    vault_file: str = get_vault_file(user=user, vault_dir=vault_dir)
    return read_network_vault(vault_file, 'r')


def delete_network_data(
        network_name: str, user: str=None, vault_dir: str=None
    ) -> None:
    """Delete given network's entry from vault json.
    
    Args:
        network_name str: Network to remove.
        user str: User whose vault to remove network from.
        vault_dir str: Path-like object representing vault location.
    """

    user: str = user or getuser()
    vault_dir: str = vault_dir or get_vault_dir()

    vault_file: str = get_vault_file(
        user=user, vault_dir=vault_dir
    )
    data: dict = read_network_vault(vault_file, 'r')

    # update network data
    try:
        data.pop(network_name)
    except KeyError:
        # assume it's already gone somehow, which we want anyway
        pass
    with open(vault_file, 'w') as vault_f:
        json.dump(data, vault_f)


def remove_cpio_file(
        network_name: str, user: str=None, vault_dir: str=None
    ) -> None:
    """Remove given network's CPIO file from vault location.
    
    Args:
        network_name str: Network to remove.
        user str: User whose vault to remove network from.
        vault_dir str: Path-like object representing vault location.
    """

    user: str = user or getuser()
    vault_dir: str = vault_dir or get_vault_dir()

    full_path: str = os.path.join(
        vault_dir, user, network_name + ".cpio"
    )
    if not os.path.isfile(full_path):
        print("Unable to remove ", full_path, ": Does not exist!")
        return
    os.remove(full_path)
