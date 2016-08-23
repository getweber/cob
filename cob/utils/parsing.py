import re

import yaml


def parse_front_matter(fileobj):
    line = fileobj.readline().strip()

    match = re.match(r'^\s*#\s*cob:\s*(.*)$', line)
    if match:
        return _parse_oneline_dict(match.group(1))

    if re.match(r'^#\s?cob-yaml:\s*$', line):
        s = ""
        for line in fileobj:
            if not line.startswith('#'):
                return None

            line = line[1:]
            if line and line[0].isspace():
                line = line[1:]
            if line.strip() == '---':
                break
            s += line
        return yaml.load(s)

    return None

def _parse_oneline_dict(line):
    returned = {}
    for element in line.split():
        try:
            key, value = element.split('=')
        except ValueError:
            return None
        returned[key] = value
    return returned
