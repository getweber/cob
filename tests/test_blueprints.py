import requests


def test_blueprints(empty_project):
    proj = empty_project
    names = ['bp1', 'bp2']
    expected_values = ['this is {}'.format(name) for name in names]

    for name, expected_value in zip(names, expected_values):
        proj.generate_blueprint(name).append_template(
            'echo_route', {'value': expected_value, 'path': 'test'})

    with proj.server_context() as url:
        for name, expected_value in zip(names, expected_values):
            assert requests.get(url.add_path(name).add_path('test')).content.decode(
                'utf-8') == 'this is {}'.format(name)
