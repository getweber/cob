import copy

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
