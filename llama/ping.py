"""Ping.py

Ping implements different methods of measuring latency between endpoints. Major
methods available are:
    * hping3 (sub-shell/process)
"""

import collections
import logging
import re
import shlex
import subprocess
from llama import udp


RE_LOSS = re.compile(
    r'(?P<loss>[0-9]+)\% packet loss')
RE_STATS = re.compile(
    r'= (?P<min>[0-9.]+)/(?P<avg>[0-9.]+)/(?P<max>[0-9.]+) ms')


ProbeResults = collections.namedtuple(
    'ProbeResults', ['loss', 'avg', 'target'])


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
        a tuple containing (loss %, RTT average, target host)
    """
    cmd = 'sudo hping3 --interval u10000 --count %s --syn %s' % (
        count, target)
    code, out, err = runcmd(cmd)
    for line in err.split('\n'):
        logging.debug(line)
    match_loss = RE_LOSS.search(err)
    match_stats = RE_STATS.search(err)
    if match_loss and match_stats:
        results = ProbeResults(match_loss.group('loss'),
                               match_stats.group('avg'),
                               target)
    else:
        results = ProbeResults(None, None, target)
    return results


def send_udp(target, count=500, port=60000, tos=0x00, timeout=0.2):
    """Sends UDP datagrams crafted for LLAMA reflectors to target host.

    Note: Using this method does NOT require `root` priveleges.

    Args:
        target: hostname or IP addres of target
        count: number of datagrams to send

    Returns:
        a tuple containing (loss %, RTT average, target host)
    """
    sender = udp.Sender(target, port, count, tos, timeout)
    sender.run()
    return ProbeResults(sender.stats.loss, sender.stats.rtt_avg, target)
