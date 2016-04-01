import requests

from .utils import server_context


def test_no_index_page(empty_project):
    with server_context(empty_project) as url:
        assert requests.get(url).status_code == requests.codes.not_found
