"""Utility library for LLAMA.

This provides utility functions used across the project.
"""

import collections
import logging
import shlex
import subprocess


# Default port for targets
# Primarily used for UDP, as dst for the collector, and
# the listening port on the reflector
DEFAULT_DST_PORT = 60000
# Default timeout for probes
# Determines how long to wait until counting it as a loss
DEFAULT_TIMEOUT = 0.2

CommandResults = collections.namedtuple(
    'CommandResults', ['returncode', 'stdout', 'stderr'])


def array_split(iterable, n):
    """Split a list into chunks of ``n`` length."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


def mean(iterable):
    """Returns the average of the list of items."""
    return sum(iterable) / len(iterable)


def runcmd(command):
    """Runs a command in sub-shell.

    Args:
        command:  string containing the command

    Returns:
        a namedtuple containing (returncode, stdout, stderr)
    """
    stdout = ''
    cmd = shlex.split(command)
    runner = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        out = runner.stdout.readline()
        if out == '' and runner.poll() is not None:
            break
        if out:
            logging.debug(out.strip())
            stdout += out
    return CommandResults(runner.returncode, stdout, runner.stderr.read())
