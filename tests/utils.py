import os
from contextlib import contextmanager

import jinja2
import logbook


_logger = logbook.Logger(__name__)


@contextmanager
def chdir_context(path):
    path = str(path)
    oldpath = os.path.abspath('.')
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpath)


def write_template(fileobj, name, args):
    with open(os.path.join(os.path.dirname(__file__), '_templates', name)) as f:
        template = jinja2.Template(f.read())
    fileobj.write(template.render(**args))
