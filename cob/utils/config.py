import copy
import os
from pathlib import Path

import yaml


def get_etc_config_path(project_name):
    return Path('/etc/cob/conf.d') / project_name


def get_config_override_locations(project_name):
    return [
        get_etc_config_path(project_name),
        Path('~/.config/cob/projects').expanduser() / project_name,
    ]


def load_overrides(root, *, environ=None):

    if environ is None:
        environ = os.environ

    config_dirs = []
    project_name = root.get('name', None)
    if project_name is not None:
        config_dirs.extend(get_config_override_locations(project_name))
    config_dir_env = environ.get('COB_CONFIG_DIR')
    if config_dir_env:
        config_dirs.append(Path(config_dir_env))

    for config_dir in config_dirs:
        if not isinstance(config_dir, Path):
            config_dir = Path(config_dir)

        if config_dir.is_dir():
            for yaml_file in sorted(config_dir.iterdir(), key=lambda p: p.stem):
                if yaml_file.stem.startswith(('_', '.')) or yaml_file.suffix != '.yml':
                    continue
                with yaml_file.open() as f:
                    root = merge_config(root, yaml.load(f))
    return root


def merge_config(parent, *children, in_place=False):
    if in_place:
        returned = parent
    else:
        returned = copy.deepcopy(parent)
    for child in children:
        for key, value in child.items():
            if isinstance(value, dict):
                if key not in returned:
                    returned[key] = value.copy()
                else:
                    if not isinstance(returned[key], dict):
                        raise ValueError(f'Cannot merge dictionaries: value of {key!r} is not a dictionary')
                    merge_config(returned[key], value, in_place=True)
            else:
                returned[key] = copy.deepcopy(value)
    return returned
