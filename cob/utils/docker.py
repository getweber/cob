from mitba import cached_function
from ..exceptions import MissingDependency
import os
import shutil
import subprocess


__all__ = ['docker_cmd', 'docker_compose_cmd']


class Docker:

    def __init__(self, command_name='docker'):
        self._cmdname = command_name
        self._cmd_full_path = None

    def get_command_name(self):
        return self._cmdname

    @cached_function
    def is_sudo_needed(self):
        proc = subprocess.Popen(
            'docker ps', shell=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        err = proc.communicate()[1].decode('utf-8')
        if proc.returncode == 0:
            return False
        assert 'permission denied' in err.lower(), f"'docker ps' failed on {err}"
        return True

    def get_full_command_name(self):
        if self._cmd_full_path is None:
            cmd = self._cmdname
            if not os.path.isabs(cmd):
                cmd = shutil.which(cmd)
                if cmd is None:
                    raise MissingDependency(f'{self._cmdname} could not be found')
                self._cmd_full_path = cmd
        return self._cmd_full_path

    def args(self, args):
        return DockerCommand(self, args)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)

        def returned(args):
            return self.args([attr]).args(args)

        returned.__name__ = attr
        return returned


class DockerCommand:

    def __init__(self, docker, args):
        self._docker = docker
        self._force_sudo = False
        self._args = list(args)

    def args(self, args):
        self._args.extend(args)
        return self

    def force_sudo(self, force=True):
        self._force_sudo = force
        return self

    def to_split_command(self):
        returned = []
        if self._force_sudo or self._docker.is_sudo_needed():
            returned.extend(
                ['sudo', '-p', 'Please enter your password to run docker: '])
        returned.append(self._docker.get_full_command_name())
        returned.extend(self._args)
        return returned

    def execv(self):
        cmd = self.to_split_command()
        os.execv(cmd[0], cmd)

    def popen(self, *args, **kwargs):
        return subprocess.Popen(self.to_split_command(), *args, **kwargs)

    def check_output(self, *args, **kwargs):
        return subprocess.check_output(self.to_split_command(), *args, **kwargs)

    def run(self, use_exec=False):
        if use_exec:
            self.execv()
        else:
            returned = self.popen()
            if returned.wait() != 0:
                raise subprocess.CalledProcessError(
                    returned.returncode, self.to_split_command())
            return returned

    def __repr__(self):
        return f"[docker] {' '.join(self._args)}"


docker_cmd = Docker()
docker_compose_cmd = Docker('docker-compose')
