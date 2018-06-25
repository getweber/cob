import pytest

from cob.utils.config import merge_config, load_overrides


def test_merge_config():
    assert merge_config({'a': 'b'}, {'c': 'd'}) == {'a': 'b', 'c': 'd'}


def test_merge_config_recursive():
    a = {'a': 'b', 'c': {'x': 'y', 'd': {'z': 1}}}
    b = {'a2': 'b2', 'c': {'x2': 'y2', 'd': {'z2': 4}}}
    result = merge_config(a, b)
    assert result == {
        'a': 'b',
        'a2': 'b2',
        'c': {'x': 'y', 'x2': 'y2', 'd': {'z': 1, 'z2': 4}},
    }
    assert result is not a
    assert result['c'] is not a['c']


def test_merge_config_incompatible():
    a = {'a': 'b', 'c': 2}
    b = {'a2': 'b2', 'c': {'c': 'd2'}}
    with pytest.raises(ValueError) as caught:
        merge_config(a, b)

    assert 'cannot merge dictionaries' in str(caught.value).lower()


def test_config_overrides(tmpdir, request):
    root_config = {'a': 2}

    for i in range(3):
        with tmpdir.join(f'{i:03}.yml').open('w') as f:
            f.write(f'a: {i+1000}')

    cfg = load_overrides(root_config, environ={'COB_CONFIG_DIR': str(tmpdir)})
    assert cfg is not root_config

    assert cfg['a'] == 1002
