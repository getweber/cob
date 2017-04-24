import click
import colorful
import flask
import urllib

from ..app import build_app
from ..bootstrapping import ensure_project_bootstrapped


@click.group()
def list():
    pass

@list.command(name='routes')
@click.option('--server-name', default='app')
def list_routes(server_name):
    ensure_project_bootstrapped()
    app = build_app()

    app.config['SERVER_NAME'] = server_name

    with app.app_context():
        output = []

        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = flask.url_for(rule.endpoint, **options)
            line = colorful.gray("{:50s} {:20s} ".format(rule.endpoint, methods))
            line += colorful.green(urllib.parse.unquote(url))
            output.append(line)

    for line in sorted(output, key=lambda s: s.orig_string):
        print(line)
