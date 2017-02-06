"""LAMA - Variables module

This library supplies a consistent variable naming representation for LAMA
timeseries data.
"""

import collections
import json
import time
import weakref


class Error(Exception):
    """Top-level error."""


class DatapointError(Error):
    """Problems with Datapoint descriptors."""


DatapointResults = collections.namedtuple(
    'DatapointResults', ['name', 'value', 'timestamp'])


class Datapoint(object):
    """Descriptor for a single datapoint."""

    def __init__(self, name):
        self.name = name
        self._value = weakref.WeakKeyDictionary()
        self._time = weakref.WeakKeyDictionary()

    def __set__(self, instance, value):
        self._value[instance] = value
        self._time[instance] = int(round(time.time()))

    def __get__(self, instance, cls):
        try:
            results = DatapointResults(
                self.name, self._value[instance], self._time[instance])
        except KeyError:
            results = DatapointResults(self.name, None, None)
        return results

    def __delete__(self, instance):
        raise DatapointError('Cannot delete datapoint: %s' % instance)


class Metrics(object):
    """A collection of metrics and common operations."""

    rtt = Datapoint('rtt')
    loss = Datapoint('loss')

    def __init__(self, **tags):
        """Constructor

        Args:
            tags: (dict) key=value pairs of tags to assign the metric.
        """
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    @property
    def data(self):
        data = []
        for attr, thing in Metrics.__dict__.iteritems():
            if isinstance(thing, Datapoint):
                data.append(tuple(self.__getattribute__(attr)))
        return data

    @property
    def as_dict(self):
        return {'tags': self.tags, 'data': self.data}

    @property
    def as_json(self):
        return json.dumps(self.as_dict, indent=4)

    @property
    def as_influx(self):
        """Returns datapoints formatted for ingestion into InfluxDB.

        The returned data is a list of dicts (each dict is one datapoint).
        """
        points = []
        for name, value, timestamp in self.data:
            point = {}
            point.setdefault('measurement', name)
            point.setdefault('tags', self.tags)
            try:
                point.setdefault('fields', {'value': float(value)})
            except TypeError:
                point.setdefault('fields', {'value': None})
            try:
                point.setdefault('time', timestamp * 1000000000)
            except TypeError:
                point.setdefault('time', None)
            points.append(point)
        return points
