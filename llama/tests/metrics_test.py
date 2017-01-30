"""Unittests for metrics lib."""

from llama import metrics
import pytest
import time


@pytest.fixture
def two_things():
    class Thing(object):
        dp1 = metrics.Datapoint('dp1')
        dp2 = metrics.Datapoint('dp2')
    return Thing(), Thing()


class TestDatapoint(object):
    """Let's test the Datapoint descriptor."""

    def test_setget_single(self, two_things, monkeypatch):
        obj1, obj2 = two_things
        monkeypatch.setattr(time, 'time', lambda: 100)
        obj1.dp1 = 1241
        assert obj1.dp1 == ('dp1', 1241, 100)

    def test_setget_multidatapoint(self, two_things, monkeypatch):
        obj1, obj2 = two_things
        monkeypatch.setattr(time, 'time', lambda: 999)
        obj1.dp1 = 1241
        obj1.dp2 = 0.1111
        assert obj1.dp1 == ('dp1', 1241, 999)
        assert obj1.dp2 == ('dp2', 0.1111, 999)

    def test_setget_multiclass(self, two_things, monkeypatch):
        obj1, obj2 = two_things
        monkeypatch.setattr(time, 'time', lambda: 12345)
        obj1.dp1 = 1241
        obj1.dp2 = 0.1111
        obj2.dp1 = 3000
        obj2.dp2 = 1234567890123456
        assert obj1.dp2 == ('dp2', 0.1111, 12345)
        assert obj2.dp1 == ('dp1', 3000, 12345)
        assert obj2.dp2 == ('dp2', 1234567890123456, 12345)
        # another round
        obj1.dp1 = 0
        obj1.dp2 = 10.1111
        assert obj1.dp1 == ('dp1', 0, 12345)
        assert obj1.dp2 == ('dp2', 10.1111, 12345)


@pytest.fixture
def m1():
    m = metrics.Metrics(src='host2',
                        metro='iad', facility='iad2', cluster='iad2a')
    return m


class TestMetrics(object):

    def test_constructor(self, m1):
        assert m1

    def test_tags(self, m1):
        assert m1.tags == {
            'src': 'host2',
            'metro': 'iad',
            'facility': 'iad2',
            'cluster': 'iad2a'
        }

    def test_data(self, m1):
        assert len(m1.data) == 2

    def test_as_dict(self, m1, monkeypatch):
        monkeypatch.setattr(time, 'time', lambda: 100)
        m1.rtt = 1
        m1.loss = 2
        assert m1.as_dict['tags'] == {
            'src': 'host2',
            'metro': 'iad',
            'facility': 'iad2',
            'cluster': 'iad2a'
        }
        assert ('rtt', 1, 100) in m1.as_dict['data']
        assert ('loss', 2, 100) in m1.as_dict['data']

    def test_as_influx(self, monkeypatch):
        monkeypatch.setattr(time, 'time', lambda: 100)
        m1 = metrics.Metrics(src='a', dst='b')
        m1.rtt = 70
        m1.loss = 1.2
        point1 = {
            'measurement': 'rtt',
            'tags': {
                'src': 'a',
                'dst': 'b',
            },
            'time': 100000000000,
            'fields': {
                'value': 70
            }
        }
        point2 = {
            'measurement': 'loss',
            'tags': {
                'src': 'a',
                'dst': 'b',
            },
            'time': 100000000000,
            'fields': {
                'value': 1.2
            }
        }
        assert type(m1.as_influx) is list
        assert point1 in m1.as_influx
        assert point2 in m1.as_influx
