=====
LLAMA
=====

|travis-ci-status| |pypi-llama|

.. figure:: ./docs/llama-logo.png
   :alt: llama-logo

**L.L.A.M.A.** is a deployable service which artificially produces traffic
for measuring network performance between endpoints.

LLAMA uses UDP socket level operations to support multiple QoS classes.
UDP datagrams are fast, efficient, and will hash across ECMP paths in
large networks to uncover faults and erring interfaces. LLAMA is written
in pure Python for maintainability.

Okay, but not yet - Alpha Status
--------------------------------
LLAMA will eventually have all those capabilities, but not yet. For
instance, there it does not currently provide QOS functionality,
but will send test traffic using ``hping3`` or a built-in UDP library
It’s currently being tested in *Alpha* at Dropbox through experimental
correlation.

Problem
-------

Measure the following between groups of endpoints across a network:

* round-trip latency
* packet loss

Solution
--------

1. A ``collector`` sends traffic and produces measurements
2. A ``reflector`` replies to the ``collector``
3. A ``scraper`` places measurements from ``collectors`` into a TSDB
   (timeseries database)

+-------------+------------+
| |collector| | |overview| |
+-------------+------------+

MVP Design Decisions
--------------------

In order to built a minimally viable product first, the following
decisions were made:

1. Python for maintainability (still uncovering how this will scale)
2. Initially TCP (hping3), then UDP (sockets)
3. InfluxDB for timeseries database
4. Grafana for UI, later custom web UI

ICMP vs. TCP vs. UDP
--------------------

-  **ICMP:** send echo-request; reflector sends back echo-reply (IP
   stack handles this natively)
-  **TCP:** send ``TCP SYN`` to ``tcp/0``; reflector sends back
   ``TCP RST+ACK``; source port increments (IP stack handles natively)
-  **UDP:** send ``UDP`` datagram to receiving port on reflector;
   reflector replies; source port increments (relies on Reflector agent)

Sending ICMP pings or sending TCP/UDP traffic all result in different
behaviors. ICMP is useful to test reachability but generally not useful
for testing multiple ECMP paths in a large or complex network fabric.

TCP can test ECMP paths, but in order to work without a reflector agent,
needs to trick the TCP/IP stack on the reflecting host by sending to
``tcp/0``. TCP starts breaking down at high transmission volumes because
the host fails to respond to some ``SYN`` packets with ``RST+ACK``.
However, the approach with TCP fits for an MVP model.

UDP can be supported with a reflector agent which knows how to respond
quickly to UDP datagrams. Crafting UDP datagrams means we maintain
control over the payload and things like TOS markings in the header.

+---------------------------------+--------+---------+-------+
|                                 | ICMP   | TCP     | UDP   |
+=================================+========+=========+=======+
| Easy implementation             | ✓      | ✓       |       |
+---------------------------------+--------+---------+-------+
| Hashes across LACP/ECMP paths   |        | ✓       | ✓     |
+---------------------------------+--------+---------+-------+
| Works without Reflector agent   | ✓      | ✓       |       |
+---------------------------------+--------+---------+-------+

Documentation
-------------
*TBD*

Contributing
------------
*TBD*

Acknowledgements / References
-----------------------------
* Inspired by: https://www.youtube.com/watch?v=N0lZrJVdI9A
  * with slides: https://www.nanog.org/sites/default/files/Lapukhov_Move_Fast_Unbreak.pdf
* Concepts borrowed from: https://github.com/facebook/UdpPinger/

.. |travis-ci-status| image:: https://travis-ci.org/dropbox/llama.svg?branch=master
   :target: https://travis-ci.org/dropbox/llama
.. |pypi-llama| image:: https://img.shields.io/pypi/v/llama.svg?style=flat
   :target: https://pypi.python.org/pypi/llama
.. |collector| image:: ./docs/collector-sm.png
   :target: ./docs/collector.png
.. |overview| image:: ./docs/overview-sm.png
   :target: ./docs/overview.png
