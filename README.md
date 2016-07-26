# LLAMA

![llama-logo](./docs/llama-logo.png)

**LLAMA** is a deployable service which artificially produces
traffic for measuring network performance between endpoints.

LLAMA uses UDP socket level operations to support multiple QoS
classes. UDP datagrams are fast, efficient, and will hash
across ECMP paths in large networks to uncover faults and erring
interfaces. LLAMA is written in pure Python for maintainability.

## Okay, but not yet

LLAMA will eventually have all those capabilities, but not yet.
For instance, there it does not currently provide UDP or QOS
functionality, but will send test traffic using `hping3`
It's currently being tested in *Alpha* at Dropbox through
experimental correlation. See the TODO list below for more plans.

# Problem
Measure the following between groups of endpoints across a network:
* round-trip latency
* packet loss

# Solution

1. A `collector` sends traffic and produces measurements
2. A `reflector` replies to the `collector`
3. A `scraper` places measurements from `collectors` into a TSDB (timeseries database)

| <img src="./docs/collector.png" height="300px">  | <img src="./docs/overview.png" height="300px"> |
| ---- | ---- |

## MVP Design Decisions
1. Python for maintainability (still uncovering how this will scale)
2. Initially TCP (hping3), then UDP (sockets)
3. InfluxDB for timeseries database
4. Grafana for UI, later custom web UI

## ICMP vs. TCP vs. UDP

* **ICMP:** send echo-request ; reflector sends back echo-reply (IP stack handles this natively)
* **TCP:** send `TCP SYN` to `tcp/0` ; reflector sends back `TCP RST+ACK` ; source port increments (IP stack handles natively)
* **UDP:** ......


|      | ICMP | TCP | UDP |
| --- | --- | --- | --- |
| Easy implementation | &#10004; | &#10004; |  |
| Hashes across LACP/ECMP paths | | &#10004; | &#10004; |
| Works without Reflector agent | &#10004; | &#10004; |  |


# TODO
- [x] Implement TCP library (using `hping3` in a shell) 
- [x] Implement UDP library (using sockets)
- [ ] Write bin runscripts for Sender/Reflector CLI utilities
- [ ] Hook UDP library into Collector process
- [ ] Add support for QOS
- [ ] Add monitoring timeseries for Collectors
- [ ] Write matrix-like UI for InfluxDB timeseries
