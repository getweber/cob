def test_docker_image_name(project_factory):
    project_factory.config.update({'docker': {'image_name': 'bla'}})
    assert project_factory.build().get_docker_image_name() == 'bla'
