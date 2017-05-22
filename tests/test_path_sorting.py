import pytest

import itertools

from cob.utils.url import sort_paths_specific_to_generic


@pytest.mark.parametrize('paths', list(itertools.permutations(
    ['/api/bla', '/apibla', '/a/pi/bla', '/a'])))
def test_sort_paths(paths):
    assert sort_paths_specific_to_generic(paths) == [
        '/apibla',
        '/api/bla',
        '/a/pi/bla',
        '/a',
        ]

@pytest.mark.parametrize('paths', list(itertools.permutations(
    ['/api', '/api//blap/', '/api/blap/foo'])))
def test_sort_paths_normalization(paths):
    assert sort_paths_specific_to_generic(paths) == [
        '/api/blap/foo',
        '/api//blap/',
        '/api',
        ]
