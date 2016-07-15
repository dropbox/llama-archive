"""Configuation library for LLAMA.

This is mostly used by the Collector process to determine target hosts and
tag mappings.
"""

import collections
import logging
import yaml


class Error(Exception):
    """Top level error."""


Tag = collections.namedtuple('Tag', ['key', 'value'])


class Target(object):
    """Configuration for a single LLAMA target.

    On a decently sized deployment, we'd expect ~1000 or ~10,000 targets, so
    we'll use __slots__ to save memory at scale.
    """

    __slots__ = ['hostname', 'tags']

    def __init__(self, hostname, **tags):
        self.hostname = hostname
        self.tags = []
        for key, value in tags.iteritems():
            self.tags.append(Tag(key=key, value=value))

    def __repr__(self):
        return '<Target "%s" with %s tags at %s>' % (
            self.hostname, len(self.tags), hex(id(self)))


class CollectorConfig(object):

    __slots__ = ['_targets']

    def __init__(self):
        self._targets = []

    def load(self, filepath):
        with open(filepath, 'r') as fh:
            config = yaml.safe_load(fh)
        for hostname in config.keys():
            self._targets.append(Target(hostname, **config[hostname]))
        logging.info('Loaded configuration with %s targets', len(self._targets))

    def __repr__(self):
        return '<CollectorConfig with %s targets at %s>' % (
            len(self._targets), hex(id(self)))

    @property
    def targets(self):
        for target in self._targets:
            yield target.hostname, target.tags
