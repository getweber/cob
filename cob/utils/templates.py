from jinja2 import Template
from pkg_resources import resource_string


def load_template(name):
    template_string = resource_string('cob', 'templates/{}.j2'.format(name)).decode('utf-8')
    return Template(template_string)
