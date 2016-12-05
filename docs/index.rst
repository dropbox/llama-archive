##################################
LLAMA - Loss & LAtency MAtrix
##################################

|travis-ci-status| |rtd-llama| |pypi-llama|

.. figure:: https://raw.githubusercontent.com/dropbox/llama/master/docs/_static/llama-logo.png
   :alt: llama-logo

**L.L.A.M.A.** is a deployable service which artificially produces traffic
for measuring network performance between endpoints.

LLAMA uses UDP socket level operations to support multiple QoS classes.
UDP datagrams are fast, efficient, and will hash across ECMP paths in
large networks to uncover faults and erring interfaces. LLAMA is written
in pure Python for maintainability.


**Contents**:

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |travis-ci-status| image:: https://travis-ci.org/dropbox/llama.svg?branch=master
   :target: https://travis-ci.org/dropbox/llama
.. |pypi-llama| image:: https://img.shields.io/pypi/v/llama.svg?style=flat
   :target: https://pypi.python.org/pypi/llama
.. |rtd-llama| image:: https://readthedocs.org/projects/llama/badge/?version=latest
   :target: http://llama.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
