"""Ping.py

Ping implements different methods of measuring latency between endpoints. Major
methods available are:
    * hping3 (sub-shell/process)
"""

import logging
import re
import shlex
import subprocess


RE_LOSS = re.compile(
    r'(?P<loss>[0-9]+)\% packet loss')
RE_STATS = re.compile(
    r'= (?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+) ms')


class Error(Exception):
    """Top level error."""


class CommandError(Error):
    """Problems running commands."""


def runcmd(command):
    """Runs a command in sub-shell.

    Args:
        command:  string containing the command

    Returns:
        a tuple containing (stdout, stderr)

    Raises:
        CommandError, if return code of command is anything but 0
    """
    cmd = shlex.split(command)
    runner = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while runner.poll() is None:
        logging.debug(runner.stdout.readline().strip())
    return runner.returncode, runner.stdout.read(), runner.stderr.read()


def hping3(target, count=128):
    """Sends TCP SYN traffic to a target host.

    Note: Using hping3 requires not only hping3 be installed on the host
    system, but access as `root` (or sudo equivalent).

    Args:
        target:  hostname or IP address of target
        count:  number of datagrams to send

    Returns:
        a tuple containing (loss, RTT average)
    """
    cmd = 'sudo hping3 --interval u10000 --count %s --syn %s' % (
        count, target)
    code, out, err = runcmd(cmd)
    for line in err.split('\n'):
        logging.debug(line)
    match_loss = RE_LOSS.search(err)
    match_stats = RE_STATS.search(err)
    if match_loss and match_stats:
        return match_loss.group('loss'), match_stats.group('avg'), target
    else:
        return None, None
