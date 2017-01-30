"""LLAMA Collector module

The Collector is intended to be run on a single host and collect packet loss
and latency to a collection of far-end hosts.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from concurrent import futures
import flask
import humanfriendly
import json
import logging
import os
import time

from llama import config
from llama import metrics
from llama import ping
from version import __version__


class Error(Exception):
    """Top level error."""


class Collection(object):
    """An abstraction for measuring latency to a group of targets."""

    def __init__(self, config, use_udp=False):
        """Constructor.

        Args:
            config: (config.CollectorConfig) of targets
            udp: (bool) Use UDP datagrams for probes (requires Reflectors)
        """
        self.method = ping.hping3
        if use_udp:
            self.method = ping.send_udp
        self.metrics = {}
        self.config = config
        for dst_ip, tags in self.config.targets:
            logging.info('Creating metrics for %s: %s', dst_ip, tags)
            self.metrics.setdefault(
                dst_ip, metrics.Metrics(**dict(tags)))

    def collect(self, count):
        """Collects latency against a set of hosts.

        Args:
            count: number of datagrams to send each host
        """
        jobs = []
        with futures.ThreadPoolExecutor(max_workers=50) as executor:
            for host in self.metrics.keys():
                logging.info('Assigning target host: %s', host)
                jobs.append(executor.submit(self.method, host, count))
        for job in futures.as_completed(jobs):
            loss, rtt, host = job.result()
            self.metrics[host].loss = loss
            self.metrics[host].rtt = rtt
            logging.info('Summary {:16}:{:>3}% loss, {:>4} ms rtt'.format(
                host, loss, rtt))

    @property
    def stats(self):
        return [x.as_dict for x in self.metrics.values()]

    @property
    def stats_influx(self):
        points = []
        for metric in self.metrics.values():
            points.extend(metric.as_influx)
        return points


class HttpServer(flask.Flask):
    """Our HTTP/API server."""

    EXECUTORS = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }

    def __init__(self, name, ip, port, *args, **kwargs):
        """Constructor.

        Args:
            name:  (str) name of Flask service
            ip:  (str) IP address to bind HTTP server
            port:  (int) TCP port for HTTP server to listen
        """
        super(HttpServer, self).__init__(name, *args, **kwargs)
        # Fixup the root path for Flask so it can find templates/*
        root_path = os.path.abspath(os.path.dirname(__file__))
        logging.debug('Setting root_path for Flask: %s', root_path)
        self.root_path = root_path
        self.targets = config.CollectorConfig()
        self.ip = ip
        self.port = port
        self.start_time = time.time()
        self.setup_time = 0
        self.scheduler = BackgroundScheduler(
            daemon=True, executors=self.EXECUTORS)
        self.collection = None
        self.add_url_rule('/', 'index', self.index_handler)
        self.add_url_rule('/status', 'status', self.status_handler)
        self.add_url_rule('/latency', 'latency', self.latency_handler)
        self.add_url_rule('/influxdata', 'influxdata', self.influxdata_handler)
        self.add_url_rule('/quitquit', 'quitquit', self.shutdown_handler)
        logging.info('Starting Llama Collector, version %s', __version__)

    def configure(self, filepath):
        """Configure the Collector from file.

        Args:
            filepath: (str) where the configuration is located
        """
        self.targets.load(filepath)

    def status_handler(self):
        return flask.Response('ok', mimetype='text/plain')

    def index_handler(self):
        return flask.render_template(
            'index.html',
            targets=self.targets.targets,
            interval=self.interval,
            start_time=self.start_time,
            setup_time=self.setup_time,
            uptime=humanfriendly.format_timespan(
                time.time() - self.start_time))

    def latency_handler(self):
        data = json.dumps(self.collection.stats, indent=4)
        return flask.Response(data, mimetype='application/json')

    def influxdata_handler(self):
        data = json.dumps(self.collection.stats_influx, indent=4)
        return flask.Response(data, mimetype='application/json')

    def shutdown_handler(self):
        """Shuts down the running web server and other things."""
        logging.warn('/quitquit request, attempting to shutdown server...')
        self.scheduler.shutdown(wait=False)
        fn = flask.request.environ.get('werkzeug.server.shutdown')
        if not fn:
            raise Error('Werkzeug (Flask) server NOT running.')
        fn()
        return '<pre>Quitting...</pre>'

    def run(self, interval, count, use_udp=False, *args, **kwargs):
        """Start all the polling and run the HttpServer.

        Args:
            interval:  seconds between each poll
            count:  count of datagram to send each responder per interval
        """
        self.interval = interval
        self.scheduler.start()
        self.collection = Collection(self.targets, use_udp)
        self.scheduler.add_job(self.collection.collect, 'interval',
                               seconds=interval, args=[count])
        super(HttpServer, self).run(
            host=self.ip, port=self.port, threaded=True, *args, **kwargs)
        self.setup_time = round(time.time() - self.start_time, 0)
