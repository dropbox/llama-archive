"""UDP Packet Library for LLAMA

This library provides several functions:
    * Custom IPv4 UDP sockets
    * Sender class
    * Reflector class

The custom socket class provides the capability to carry timestamps, TOS
markings, and other data encoding. Specialty methods send and receive these
pieces of data. Usually, setting IP_TOS in the IP header is simple, but in
Python reading TOS bits becomes difficult unless using raw sockets. We'd like
to avoid raw sockets so our application doesn't need to run as `root`. To
solve this we encode TOS bits into the payload of the datagrams.

The Sender class sends large quantities of UDP probes in batches.

The Reflector class runs a simple loop: receive, decode TOS, set timestamp,
encode TOS, send back.

TOS is encoded as 8-bits (1-byte, 2-hex digits). See
https://www.tucny.com/Home/dscp-tos for a reference.
"""

import collections
import concurrent.futures
import logging
import socket
import struct
import time

from llama import util


# Data payload structure for probes
# Encoding timestamps in packet data reduces the amount of tracking we have to
# do in code. TOS bits can be set on outbound UDP packets, but are difficult
# to read back with getsockopt() -- placing in payload helps this as well.
# We include a 'signature' to help reject non-LLAMA related datagrams.
UdpData = collections.namedtuple(
    'UdpData', ['signature',    # Unique LLAMA signature
                'tos',          # TOS bits, expressed as 1 byte in hex
                'sent',         # Time datagram was placed on wire in ms
                'rcvd',         # Time datagram was returned to sender in ms
                'rtt',          # Total round-trip time in ms
                'lost'])        # Boolean, was our packet returned to sender?


# UDP statistics returned at the end of each probe cycle.
UdpStats = collections.namedtuple(
    'UdpStats', ['sent',        # How many datagrams were sent
                 'lost',        # How many datagrams were not returned
                 'loss',        # Loss, expressed as a percentage
                 'rtt_max',     # Maximum round trip time
                 'rtt_min',     # Minimum round trip time
                 'rtt_avg'])    # Average (mean) round trip time


class Ipv4UdpSocket(socket.socket):
    """Custom IPv4 UDP socket which tracks TOS and timestamps.

    Note: We inherit from the socket.socket() class for ease of use, but due
          to restrictions in C bindings, we cannot override builtin methods
          like sendto() and recvfrom(). For those methods, we make special
          methods below:  tos_sendto() and tos_recvfrom().
    """

    SIGNATURE = '__llama__'     # Identify LLAMA packets from other UDP
    FORMAT = '<10sBddd?'        # Used to pack/unpack struct data

    def __init__(self, tos=0x00, timeout=util.DEFAULT_TIMEOUT):
        """Constructor.

        Args:
            tos:  (hex) TOS bits expressed as 2-bytes
            timeout: (float) Number of seconds to block/wait socket operation
        """
        super(Ipv4UdpSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM,
                                            socket.IPPROTO_UDP)
        self._tos = tos & 0xff  # [6-bits TOS] [2-bits ECN]
        self.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, self._tos)
        self.settimeout(timeout)
        self.processed = 0

    def tos_sendto(self, ip, port):
        """Mimic the behavior of socket.sendto() with special behavior.

        Note: Data is excluded from arguments since we encode our own.

        Args:
            ip: (str) destination IP address
            port: (int) destination UDP port

        Returns:
            (int) the number of bytes sent on the socket
        """
        return self.sendto(struct.pack(self.FORMAT, self.SIGNATURE, self._tos,
                                       time.time() * 1000, 0, 0, False),
                           (ip, port))

    def tos_recvfrom(self, bufsize=512):
        """Mimic the behavior of socket.recvfrom() with special behavior.

        Args:
            bufsize: (int) number of bytes to read from socket
                     It's not advisable to change this.

        Returns:
            (UdpData) namedtuple containing timestamps
        """
        try:
            data, addr = self.recvfrom(bufsize)
            rcvd = time.time() * 1000
            results = UdpData._make(struct.unpack(self.FORMAT, data))
            rtt = rcvd - results.sent
            return results._replace(rcvd=rcvd, rtt=rtt, lost=False)
        except socket.timeout:
            logging.debug('Timed out after {}s waiting to receive'.format(
                self.gettimeout()))
            return UdpData(self.SIGNATURE, self._tos, 0, 0, 0, True)

    def tos_reflect(self, bufsize=512):
        """Intended to be the sole operation on a LLAMA reflector.

        Args:
            bufsize: (int) number of bytes to read from socket
                     It's not advisable to change this.
        """
        data, addr = self.recvfrom(bufsize)
        try:
            udpdata = UdpData._make(struct.unpack(self.FORMAT, data))
        except struct.error:
            logging.warn('Received malformed datagram of %s bytes. '
                         'Discarding.', len(data))
            # Don't reflect invalid data
            return
        self.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, udpdata.tos)
        self.sendto(data, addr)
        self.processed += 1
        if self.processed % 512 == 0:
            logging.info('Processed packets: %s', self.processed)


class Sender(object):
    """UDP Sender class capable of sending/receiving UDP probes."""

    def __init__(self, target, port, count, tos=0x00,
                 timeout=util.DEFAULT_TIMEOUT):
        """Constructor.

        Args:
            target: (str) IP address or hostname of destination
            port: (int) UDP port of destination
            count: (int) number of UDP datagram probes to send
            tos: (hex) TOS bits
            timeout: (float) in seconds
        """
        self.target = target
        self.port = port
        sockets = []
        for x in range(0, count):
            sock = Ipv4UdpSocket(tos=tos, timeout=timeout)
            sock.bind(('', 0))
            sockets.append(sock)
        self.batches = util.array_split(sockets, 50)

    def send_and_recv(self, batch):
        """Send and receive a single datagram and store results.

        Args:
            batch: (list of socket objects) for sending/receiving
        """
        for sock in batch:
            sock.tos_sendto(self.target, self.port)
            self.results.append(sock.tos_recvfrom())

    def run(self):
        """Run the sender."""
        self.results = []
        exception_jobs = []
        jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            for batch in self.batches:
                jobs.append(executor.submit(self.send_and_recv, batch))
            for job in concurrent.futures.as_completed(jobs):
                # Results should be getting collected as part of the job
                # So just handle logging any exceptions.
                if job.exception():
                    exception_jobs.append(job)
        for result in self.results:
            logging.debug(result)
        if len(exception_jobs) > 0:
            logging.critical("Encountered {} exceptions while running Sender. "
                             "Logging one such exception as an "
                             "example.".format(len(exception_jobs)))
            try:
                exception_jobs[0].result()
            except Exception as e:
                logging.exception(e)

    @property
    def stats(self):
        """Returns a namedtuple containing UDP loss/latency results."""
        sent = len(self.results)
        if sent is 0:
            logging.critical('Sender has zero results, likely as a '
                             'result of exceptions during probing')
            # TODO: Better handling for this requires a greater refactor
            return UdpStats(0, 0, 0.0, 0.0, 0.0, 0.0)
        lost = sum(x.lost for x in self.results)
        loss = (float(lost) / float(sent)) * 100
        # TODO: This includes 0 values for instances of loss
        #       Handling this requires more work around null
        #       values along the various components and DB
        rtt_values = [x.rtt for x in self.results]
        rtt_min = min(rtt_values)
        rtt_max = max(rtt_values)
        rtt_avg = util.mean(rtt_values)
        return UdpStats(sent, lost, loss, rtt_max, rtt_min, rtt_avg)


class Reflector(object):
    """Simple Reflector class."""

    def __init__(self, port):
        self.sock = Ipv4UdpSocket()
        self.sock.bind(('', port))
        sockname = self.sock.getsockname()
        logging.info('LLAMA reflector listening on %s udp/%s',
                     sockname[0], sockname[1])
        self.sock.setblocking(1)

    def run(self):
        while True:
            self.sock.tos_reflect()
