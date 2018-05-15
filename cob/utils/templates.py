from jinja2 import Environment, StrictUndefined
from pkg_resources import resource_string


def load_template(name):
    template_string = resource_string('cob', f'templates/{name}.j2').decode('utf-8')
    return Environment(undefined=StrictUndefined).from_string(template_string)
