"""LLAMA TSDB Scraper

This binary scrapes the LLAMA collectors for latency statistics and shovels
them into a timeseries database.

Usage:
    tsdb [options] <collectors>...

Options:
    --loglevel=(debug|info|warn|error|critical)
                          # Logging level to print to stderr [default: info]
    --logfile=PATH        # Log to a file
    --interval=NUM        # Collector poll interval, seconds [default: 30]
    --influx_server=HOST  # InfluxDB server [default: localhost]
    --influx_port=PORT    # InfluxDB port   [default: 8086]
    --influx_db=NAME      # InfluxDB database name [default: llama]
    --port=PORT           # Connection port on collectors  [default: 5000]
"""

from apscheduler.schedulers.blocking import BlockingScheduler
import docopt
import httplib
import influxdb
import json
import logging
import socket

import app


class Error(Exception):
    """Top-level error."""


def http_get(server, port, uri, **headers):
    """Generic HTTP GET request.

    Args:
        uri: string containing the URI to query
        headers: HTTP headers to inject into request

    Returns:
        a tuple, (status_code, data_as_string)
    """
    # TODO(): Move this to requests library.
    httpconn = httplib.HTTPConnection(server, port)
    try:
        httpconn.request('GET', uri, "", headers)
    except socket.error as exc:
        raise Error('Could not connect to %s:%s (%s)' % (server, port, exc))
    response = httpconn.getresponse()
    return response.status, response.read()


class CollectorClient(object):
    """A client for moving data from Collector to TSDB."""

    def __init__(self, server, port):
        """Constructor.

        Args:
            server:  (str) collector server hostname or IP
            port:  (int) collector TCP port
        """
        self.server = server
        self.port = port

    def get_latency(self):
        """Gets /influxdata stats from collector.

        Returns:
            list of dictionary data (latency JSON)

        Raises:
            Error: if status code from collector is not 200
        """
        status, data = http_get(self.server, self.port, '/influxdata')
        # TODO(): this would be obviated by the requests library.
        if status < 200 or status > 299:
            logging.error('Error received getting latency from collector: '
                          '%s:%s, code=%s' % (self.server, self.port, status))
        return json.loads(data)

    def push_tsdb(self, server, port, database, points):
        """Push latest datapoints to influxDB server.

        Args:
            server: (str) influxDB server hostname or IP
            port: (int) influxDB server TCP port
            database: (str) name of LLAMA database
            points: (list) dicts containing InfluxDB formatted datapoints
        """
        client = influxdb.InfluxDBClient(
            server, port, database=database)
        client.write_points(points)

    def run(self, server, port, database):
        """Get and push stats to TSDB."""
        try:
            points = self.get_latency()
        except Error as exc:
            logging.error(exc)
            return
        logging.info('Pulled %s datapoints from collector: %s',
                     len(points), self.server)
        self.push_tsdb(server, port, database, points)
        logging.info('Pushed %s datapoints to TSDB: %s', len(points), server)


def main(args):
    # process args
    loglevel = args['--loglevel']
    logfile = args['--logfile']
    interval = int(args['--interval'])
    influx_server = args['--influx_server']
    influx_port = int(args['--influx_port'])
    influx_db = args['--influx_db']
    collector_port = args['--port']
    collectors = args['<collectors>']

    # setup logging
    app.log_to_stderr(loglevel)
    if logfile:
        app.log_to_file(logfile, loglevel)
    logging.info('Arguments:\n%s', args)

    # get to work
    logging.info('Using Collector list: %s', collectors)
    scheduler = BlockingScheduler()
    for collector in collectors:
        client = CollectorClient(collector, collector_port)
        scheduler.add_job(
            client.run, 'interval', seconds=interval, args=[
                influx_server, influx_port, influx_db])
    scheduler.start()


if __name__ == '__main__':
    app.run(main, docopt.docopt(__doc__))
