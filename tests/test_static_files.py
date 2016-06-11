from uuid import uuid4

import requests

import pytest


@pytest.mark.parametrize('same_root', [True, False])
def test_static_files(empty_project, same_root):
    if same_root:
        pytest.skip('not implemented')
    proj = empty_project
    names = ['static1', 'static2']
    if same_root:
        mount_points = ['/static' for name in names]
    else:
        mount_points = ['/{}'.format(name) for name in names]
    expected_values = [str(uuid4()) for _ in names]

    for name, mount_point, expected_value in zip(names, mount_points, expected_values):
        proj.generate_static_dir(name, mountpoint=mount_point)
        with proj.path.join(name).join('root').join('file').open('w') as f:
            f.write(expected_value)

    with proj.server_context() as url:
        for name, mount_point, expected_value in zip(names, mount_points, expected_values):
            assert requests.get(url.add_path(mount_point).add_path('file')).content.decode(
                'utf-8') == expected_value
