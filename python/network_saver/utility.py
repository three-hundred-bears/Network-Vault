
import os
from pathlib import Path


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
