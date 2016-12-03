=====
LLAMA
=====

|travis-ci-status| |pypi-llama|

.. figure:: ./docs/_static/llama-logo.png
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
