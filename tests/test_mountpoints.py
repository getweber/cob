# pylint: disable=redefined-outer-name
import pytest

from cob.utils.url import Mountpoint

def test_mountpoint_normalize():
    assert Mountpoint('/a/b/c').path == '/a/b/c/'
    assert Mountpoint('/').path == '/'
    assert Mountpoint('').path == '/'

def test_mountpoint_join():
    assert Mountpoint('/a/b/c/').join('/').path == '/a/b/c/'
    assert Mountpoint('/a/b/c/').join('d').path == '/a/b/c/d/'
    assert Mountpoint('/a/b/c').join('/d/').path == '/a/b/c/d/'

def test_without_trailing_slash():
    assert Mountpoint('/a/b/c/').without_trailing_slash() == '/a/b/c'
    assert Mountpoint('/').without_trailing_slash() == ''

def test_str(mountpoint):
    assert str(mountpoint) == mountpoint.path

def test_hash(mountpoint):
    assert hash(mountpoint) == hash(mountpoint.path)

def test_equality(mountpoint):
    assert mountpoint == mountpoint
    assert mountpoint == Mountpoint(mountpoint.path)
    assert mountpoint == mountpoint.path
    assert not (mountpoint == Mountpoint('/bla'))
    assert not (mountpoint == '/bla')

def test_inequality(mountpoint):
    assert not (mountpoint != mountpoint)
    assert not (mountpoint != Mountpoint(mountpoint.path))
    assert not (mountpoint != mountpoint.path)
    assert mountpoint != Mountpoint('/bla')
    assert mountpoint != '/bla'



@pytest.fixture(params=['/a/b/c', '/', '/a/c/'])
def mountpoint(request):
    return Mountpoint(request.param)
