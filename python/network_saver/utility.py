
import os
from pathlib import Path

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

def conform_network_context(node_type):
    if node_type.isManager():
        context = node_type.childTypeCategory().name()
    else:
        context = node_type.category().name()
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
    conformed_context = map.get(context)
    if not conformed_context:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to account for {}'.format(context)
            )
    return conformed_context


def get_node_context(node):
    return conform_network_context(node.type())


def get_network_context(network):
    return get_node_context(network[0])


def get_child_context(node):
    # TODO: you already know
    category = node.type().childTypeCategory()
    if not category:
        return get_node_context(node)
    context = category.name()
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
    conformed_context = map.get(context)
    if not conformed_context:
        raise RuntimeError(
            'Unsupported context?!\n'
            'Please send me a message telling me to account for {}'.format(context)
            )
    return conformed_context

    


