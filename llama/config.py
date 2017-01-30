"""Configuation library for LLAMA.

This is mostly used by the Collector process to determine target hosts and
tag mappings.
"""

import collections
import ipaddress
import logging
import yaml


class Error(Exception):
    """Top level error."""


Tag = collections.namedtuple('Tag', ['key', 'value'])


def validate_ip(addr):
    """Pass-through function for validating an IPv4 address.

    Args:
        ip: (str) IP address

    Returns:
        unicode string with same address

    Raises:
        Error: if IPv4 address is not valid
    """
    try:
        return ipaddress.IPv4Address(unicode(addr)).compressed
    except ipaddress.AddressValueError as exc:
        raise Error('Invalid IPv4 address "%s"; %s' % (addr, exc))


class Target(object):
    """Configuration for a single LLAMA target.

    On a decently sized deployment, we'd expect ~1000 or ~10,000 targets, so
    we'll use __slots__ to save memory at scale.
    """

    __slots__ = ['dst_ip', 'tags']

    def __init__(self, dst, **tags):
        self.dst_ip = validate_ip(dst)
        self.tags = []
        for key, value in tags.iteritems():
            self.tags.append(Tag(key=key, value=value))

    def __repr__(self):
        return '<Target "%s" with %s tags at %s>' % (
            self.ip, len(self.tags), hex(id(self)))


class CollectorConfig(object):

    __slots__ = ['_targets']

    def __init__(self):
        self._targets = []

    def load(self, filepath):
        with open(filepath, 'r') as fh:
            config = yaml.safe_load(fh)
        for dst in config.keys():
            self._targets.append(Target(dst, **config[dst]))
        logging.info('Loaded configuration with %s targets',
                     len(self._targets))

    def __repr__(self):
        return '<CollectorConfig with %s targets at %s>' % (
            len(self._targets), hex(id(self)))

    @property
    def targets(self):
        for target in self._targets:
            yield target.dst_ip, target.tags
