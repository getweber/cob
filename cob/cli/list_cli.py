import click
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
        for rule in sorted(app.url_map.iter_rules(), key=lambda rule: rule.endpoint):
            options = {}
            for arg in rule.arguments:
                options[arg] = f"[{arg}]"

            methods = ','.join(rule.methods)
            url = flask.url_for(rule.endpoint, **options)
            click.echo(f"{rule.endpoint:50s} {methods:20s} ", nl=False)
            click.echo(click.style(urllib.parse.unquote(url), fg='green'))
