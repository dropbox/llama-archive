"""Unittests for metrics lib."""

from llama import ping
from llama import util
import pytest


def fake_runcmd(cmd):
    stderr = '''
    --- shelby hping statistic ---
    5 packets transmitted, 5 packets received, 0% packet loss
    round-trip min/avg/max = 0.1/0.1/0.2 ms
    '''
    stdout = '''
    HPING shelby (eth0 108.160.167.85): S set, 40 headers + 0 data bytes
    len=46 ip=1.1.7.5 ttl=61 DF id=4696 sport=0 flags=RA seq=0 win=0 rtt=0.1 ms
    len=46 ip=1.1.7.5 ttl=61 DF id=4699 sport=0 flags=RA seq=1 win=0 rtt=0.1 ms
    len=46 ip=1.1.7.5 ttl=61 DF id=4701 sport=0 flags=RA seq=2 win=0 rtt=0.1 ms
    len=46 ip=1.1.7.5 ttl=61 DF id=4702 sport=0 flags=RA seq=3 win=0 rtt=0.1 ms
    len=46 ip=1.1.7.5 ttl=61 DF id=4704 sport=0 flags=RA seq=4 win=0 rtt=0.1 ms
    '''
    return 0, stdout, stderr


class TestHping3(object):

    def silence_pyflakes(self):
        """PyFlakes complains because we don't explicitly use the module."""
        dir(pytest)

    def test_good(self, monkeypatch):
        monkeypatch.setattr(util, 'runcmd', fake_runcmd)
        assert ping.hping3('somehost', count=5) == ('0', '0.1', 'somehost')
