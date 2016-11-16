from io import StringIO

import pytest

from cob.utils.parsing import parse_front_matter

@pytest.mark.parametrize('line', [
    "# cob: x=value1 y=value2",
    "#cob:   x=value1    y=value2",
])
def test_front_matter_parser_oneline(line):
    assert _parse(line) == {'x': 'value1', 'y': 'value2'}

@pytest.mark.parametrize('line', [
    '# cob: x',
    '#',
])
def test_front_matter_parser_oneline_wrong(line):
    assert _parse(line) is None

def test_front_matter_yaml():
    yaml = _parse(
"""# cob-yaml:
# type: x
# value: y
# ---
""")
    assert yaml == {'type': 'x', 'value': 'y'}


def _parse(s):
    f = StringIO(s)
    return parse_front_matter(f)
