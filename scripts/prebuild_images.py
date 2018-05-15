import click
from halo import Halo
import logbook
import pathlib
import subprocess
import os
import sys
import tempfile
import yaml


_logger = logbook.Logger(__name__)

_ROOT = pathlib.Path(__file__).parent.parent / '_test_projects'



@click.command()
def main():
    from cob.cli.docker_cli import _build_cob_sdist

    tmpdir = pathlib.Path(tempfile.mkdtemp())
    sdist_file = tmpdir / 'cob_sdist.tar.gz'
    logbook.StderrHandler(level=logbook.DEBUG).push_application()

    _build_cob_sdist(sdist_file)
    os.environ['COB_SDIST_FILENAME'] = str(sdist_file)

    projects = []
    processes = []
    logs = []

    project_names = set()

    for project_dir in _ROOT.iterdir():
        proj_yaml = project_dir / '.cob-project.yml'
        if proj_yaml.exists():
            with proj_yaml.open() as f:
                name = yaml.load(f.read()).get('name')
                if name is None:
                    sys.exit(f'Project {project_dir.stem} does not have a name configured')
                if name in project_names:
                    sys.exit(f'Project name {name} is already in use (found in {project_dir})')
                project_names.add(name)

            projects.append(proj_yaml)


    for proj_yaml in projects:
        project_dir = proj_yaml.parent
        log = tmpdir / project_dir.stem
        logs.append(log)
        with log.open('w') as logfile:
            _logger.info('Building {}...', project_dir)
            processes.append(
                subprocess.Popen(f'{sys.executable} -m cob.cli.main docker build', cwd=project_dir, stderr=subprocess.STDOUT, stdout=logfile, shell=True)
            )
    success = True

    with Halo('Waiting for projects to build'):
        for p, log in zip(processes, logs):
            project = log.stem
            result = p.wait()
            if result != 0:
                success = False
                click.echo(click.style(f'Build failed for {project}. More details below', fg='red'))
                with log.open() as f:
                    for line in f:
                        click.echo(click.style(line, fg='yellow'))
                click.echo(click.style('^' * 80, fg='red'))

    if not success:
        raise click.ClickException('Some build processes failed')


if __name__ == '__main__':
    main()
