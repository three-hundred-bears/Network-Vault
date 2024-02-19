
import io
import json
import os
from pathlib import Path

import hou


def _remap_node_categories(category_name):

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
    conformed_cat = map.get(category_name)
    if not conformed_cat:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to ' 
            'account for {}'.format(category_name)
            )
    return conformed_cat


def get_data_dir():  
    cur_dir = Path(__file__)
    return os.path.join(cur_dir.parents[2], 'data')


def get_vault_dir():
    vault_file = os.path.join(
        get_data_dir(),
        'vault_dir.txt'
    )
    with open(vault_file, 'r') as f:
        return f.readline().strip()


def get_node_context(node):
    return _remap_node_categories(node.type().category().name())


def get_network_context(node):
    category = node.type().childTypeCategory()
    if not category:
        return get_node_context(node)
    return _remap_node_categories(category.name())

def _make(config_file):
    with open(config_file, 'x') as config_f:
        json.dump(dict(), config_f)


def _notify(config_file):
    hou.ui.displayMessage(
        "No networks available to load!\n"
        "Please first save a network using the network saver tool."
    )
    raise RuntimeError(
        "Network vault file {} does not exist".format(config_file)
    )

def read_network_vault(filepath, mode):
    func_map = {'r': _notify, 'w': _make}
    func = func_map.get(mode)
    if not func:
        raise ValueError("Invalid filemode {}".format(mode))
    if not os.path.isfile(filepath):
        func(filepath)
    try:
        data = json.load(config_f)
    except (Exception, io.UnsupportedOperation) as err:
        data = dict()
        print('Warning: Could not load config json at ', config_file)
        print(err)
    return data
