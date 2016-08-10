import pytest

def test_static_files(empty_project):
    proj = empty_project

    for i in range(2):
        proj.generate_models('models{}'.format(i)).append_template('model', {'name': 'Obj{}'.format(i)})
        proj.generate_blueprint('bp{}'.format(i)).append_template('list_model'.format(i), {'model': 'Obj{}'.format(i)})
