"""Unittests for udp lib"""

from llama.udp import UdpData, UdpStats, Sender, Ipv4UdpSocket
import pytest

class TestSender(object):

    def test_stats(self):
        mock_results = [
            UdpData(
                Ipv4UdpSocket.SIGNATURE, # Signature
                0x00, # ToS
                1496847778307.926, # Sent timestamp
                1496847778320.653, # Rcvd timestamp
                12.727022171020508, # RTT
                False, # Lost
            ),
            UdpData(
                Ipv4UdpSocket.SIGNATURE, # Signature
                0x00, # ToS
                0, # Sent timestamp
                0, # Rcvd timestamp
                0, # RTT
                True, # Lost
            ),
            UdpData(
                Ipv4UdpSocket.SIGNATURE, # Signature
                0x00, # ToS
                1496847925937.957, # Sent timestamp
                1496847925952.936, # Rcvd timestamp
                14.978885650634766, # RTT
                False, # Lost
            ),
        ]
        # TODO: This should be updated to reflect the commented/correct
        #       values once #27 has been resolved.
        mock_stats = UdpStats(
            3, # sent
            1, # lost
            33.33333333333333, # loss
            14.978885650634766, # rtt_max
            # 12.727022171020508, # rtt_min
            0, # rtt_min - This is due to #27
            # 13.852953910827637, # rtt_avg
            9.235302607218424, # rtt_avg - This is due to #27
        )
        sender = Sender('127.0.0.1', 60000, 3, tos=0x00, timeout=0.2)
        sender.results = mock_results
        stats = sender.stats
        assert stats == mock_stats
