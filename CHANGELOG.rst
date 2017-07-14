#########
Changelog
#########

Version History
===============

.. _v0.1.0:
0.1.0 (2017-07-14)
------------------
* Adds timeout parameter through the complete flow for the collector.
* Sender results are actually handled as they complete now.
* Sender exceptions are collected and provided via logging. However, better handling of non-lost probes requires a greater refactor to truly solve.

.. _v0.0.1a10:
0.0.1a10 (2017-06-07)
------------------
* Removed rounding calculation that was excessively removing precision

.. _v0.0.1a9:
0.0.1a9 (2017-05-31)
------------------
* Reflector will now discard malformed datagrams instead of still reflecting them
* Removed a debug statement in a high-frequency loop that was hampering perf
* Collector can now be told which port to use as the destination with UDP

.. _v0.0.1a8:
0.0.1a8 (2017-02-02)
------------------
* Converted ``llama_collector`` to require IP addresses for reflector targets
* Removed all DNS lookups from ``llama_collector`` process

.. _v0.0.1a7:
0.0.1a7 (2016-12-06)
------------------
* Created ``CHANGELOG.rst``, retroactively
* Converted ``README.md`` to ``README.rst``
* Created documentation, `llama.readthedocs.io <http://llama.readthedocs.io/>`_

.. _v0.0.1a6:
0.0.1a6 (2016-12-01)
------------------
* Minor housekeeping
* Moved ``runcmd()`` function into ``util.py`` library, added unittest

.. _v0.0.1a5:
0.0.1a5 (2016-11-23)
------------------
* Hooked UDP socket library into ``llama_collector``
* Added ``llama_sender`` command-line test utility

.. _v0.0.1a4:
0.0.1a4 (2016-11-14) and previous versions
------------------
* Initial Alpha versions 0.0.1a1 through 0.0.1a4 with basic functionality
  using TCP SYN probes generated from ``hping3`` command-line utility
