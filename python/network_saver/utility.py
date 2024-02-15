
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