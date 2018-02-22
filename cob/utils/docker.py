import os
import shutil

from mitba import cached_function
import subprocess


@cached_function
def _check_if_sudo_needed():
    proc = subprocess.Popen('docker ps', shell=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
    err = proc.communicate()[1].decode('utf-8')
    if proc.returncode == 0:
        return False
    assert 'permission denied' in err.lower(), "'docker ps' failed on {}".format(err)
    return True


def get_full_commmand(cmd, should_sudo=None):
    if should_sudo is None:
        should_sudo = _check_if_sudo_needed()
    if should_sudo:
        cmd[:0] = ['sudo', '-p', 'Please enter your password to run docker: ']

    if not os.path.isabs(cmd[0]):
        cmd[0] = shutil.which(cmd[0])
    return cmd
