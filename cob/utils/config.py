import copy
import os

import yaml


def load_overrides(root, *, environ=None):
    if environ is None:
        environ = os.environ
    config_dir = environ.get('COB_CONFIG_DIR')
    if config_dir is not None and os.path.isdir(config_dir):
        for yaml_file in sorted(os.listdir(config_dir)):
            with open(os.path.join(config_dir, yaml_file)) as f:
                root = merge_config(root, yaml.load(f))
    return root

def merge_config(parent, *children):
    returned = copy.deepcopy(parent)
    for child in children:
        for key, value in child.items():
            if isinstance(value, dict):
                if key not in returned:
                    returned[key] = value.copy()
                else:
                    if not isinstance(returned[key], dict):
                        raise ValueError('Cannot merge dictionaries: value of {!r} is not a dictionary'.format(key))
                    returned[key].update(value)
            else:
                returned[key] = copy.deepcopy(value)
    return returned
