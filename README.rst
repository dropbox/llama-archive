#####
LLAMA
#####

.. image:: docs/llama-logo.png
   :alt: Loss & LAtency MAtrix
   :width: 200px

**LLAMA** is a deployable service which artificially produces
traffic for measuring network performance between endpoints.

LLAMA uses UDP socket level operations to support multiple QoS
classes. UDP datagrams are fast, efficient, and will hash
across ECMP paths in large networks to uncover faults and erring
interfaces. LLAMA is written in pure Python for maintainability.
