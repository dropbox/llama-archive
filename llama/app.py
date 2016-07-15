"""Application Setup & Run

This module intends to provide standard logging, command-line flags/options.
The intended execution looks like:

    import app

    def main(args):
        pass

    if __name__ == '__main__':
        app.run(main)

Default behavior is:
    o Setup logging to INFO facility with standard format
    o Find the main() function which must take a single argument
    o Pass command-line arguments from sys.argv to main()

Behavior can be augmented by passing keyword arguments to app.run().  Constants
and helper functions should exist within this module to assist.

EXAMPLE USAGE:

    if __name__ == '__main__':
        # Always call run() first, then modify or add logging after.
        app.run(main)

        # Change logging to stderr. All three statements below do the same
        # thing.
        app.log_to_stderr(app.DEBUG)
        app.log_to_stderr('debug')
        app.log_to_stderr('DEBUG')

        # Log to a file in append mode.
        app.log_to_file('/tmp/myapp.log')

        # Log to the file and clobber exising log file.
        app.log_to_file('/tmp/myapp.log', filemode=app.CLOBBER)

    # Use an argument parser, like 'docopt' or 'gflags', to pass
    # arguments through app.run.  This ensures flags/options are loaded
    # prior to any other code running.
    if __name__ == '__main__':
        app.run(main, docopt.docopt(__doc__))

        # or with gflags
        app.run(main, FLAGS(sys.argv))

NOTE: Protection exists against running app.run() more than once per runtime
environment.
"""

import logging
import os
import sys


# Logging facilities
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL

# File modes.
CLOBBER = 'w'
APPEND = 'a'

# Formatting.
_LOG_FORMATTER = logging.Formatter(
    '%(levelname)s %(asctime)s [%(module)s]: %(message)s')

# Logging handlers.
_STDERR_HANDLER = None
_FILE_HANDLER = None

# Colors.
LOG_COLORS = {
    'DEBUG': '\033[94m',
    'INFO': '\033[32m',
    'WARN': '\033[33m',
    'WARNING': '\033[33m',
    'ERROR': '\033[91m',
    'CRITICAL': '\033[91m',
    'END': '\033[0m'}


class Error(Exception):
    """Top-level error."""
    pass


class AppError(Error):
    """Errors associated with running the application."""
    pass


def run_once(function):
    """Decorator which prevents functions from being run more than once."""
    def wrapper(*args, **kwargs):
        if wrapper.has_run:
            raise AppError(
                'Cannot call %s.%s() more than once per runtime!' % (
                    __name__, function.__name__))
        else:
            wrapper.has_run = True
            return function(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


@run_once
def run(main, args=None, root_level=DEBUG, formatter=_LOG_FORMATTER):
    """Run the application.

    Args:
        main:  the main() function from __main__ module
        args:  list or object containing args to pass to main()
               default behavior is to not send any args to main()
               popular values here are `sys.argv` or `docopt.docopt(__doc__)`
        root_level:  logging level for the root logger; limiting this will
                     limit ALL subsequent logging.
        formatter:  logging.Formatter object for stderr and file logging

    Raises:
        AppError: if function is called more than once
    """
    # Set the root logger to handle everything.
    logger = logging.getLogger('')
    logger.setLevel(root_level)
    # Setup stderr logging.
    log_to_stderr(level=CRITICAL, formatter=formatter)
    logging.debug('App started. Calling main()')
    # Call main().
    if args:
        main(args)
    else:
        main()


def userlog(level, message, *args):
    """Log a message to STDOUT for user-facing applications.

    This also results in logging to whatever level is specified.

    Args:
        level:  a logging level, i.e. logging.info or logging.error
        message:  string of message to log
        args:  arguments to pass into message
    """
    lvlname = level.func_name.upper()
    try:
        color = LOG_COLORS[lvlname]
        end = LOG_COLORS['END']
    except KeyError:
        color = ''
        end = ''
    level(message, *args)
    output = '%s%s:%s %s\n' % (color, lvlname, end, message)
    sys.stderr.write(output % args)


def get_loglevel(level):
    """Return a logging level (integer).

    Args:
        level: can be a level or a string name of a level, such as:
               logging.INFO, app.INFO or 'info'
    Returns:
        a logging.<lvl> (which is really an integer)
    """
    if type(level) is str:
        level = logging.getLevelName(level.upper())
    if type(level) is int:
        return level
    else:
        raise AppError('Level "%s" is not a valid logging level' % level)


def log_to_stderr(level, formatter=_LOG_FORMATTER,
                  handler=logging.StreamHandler):
    """Setup logging or set logging level to STDERR.

    Args:
        level:  a logging level, like logging.INFO
        formatter: a logging.Formatter object
        handler:  logging.StreamHandler (this argument is for testing)
    """
    global _STDERR_HANDLER
    _level = get_loglevel(level)
    if type(_STDERR_HANDLER) is handler:
        _STDERR_HANDLER.setLevel(_level)
    else:
        _STDERR_HANDLER = handler(stream=sys.stderr)
        _STDERR_HANDLER.setLevel(_level)
        _STDERR_HANDLER.setFormatter(formatter)
        logging.getLogger('').addHandler(_STDERR_HANDLER)
    logging.debug('Setting logging at level=%s',
                 logging.getLevelName(_level))


def log_to_file(filename, level=INFO, formatter=_LOG_FORMATTER,
                filemode=APPEND, handler=logging.FileHandler):
    """Setup logging or set logging level to file.

    Args:
        filename:  string of path/file to write logs
        level:  a logging level, like logging.INFO
        formatter:  a logging.Formatter object
        filemode:  a mode of writing, like app.APPEND or app.CLOBBER
        handler:  logging.FileHandler (this argument is for testing)
    """
    global _FILE_HANDLER
    _level = get_loglevel(level)
    if type(_FILE_HANDLER) is handler:
        _FILE_HANDLER.setLevel(_level)
    else:
        _FILE_HANDLER = handler(filename=filename, mode=filemode)
        _FILE_HANDLER.setLevel(_level)
        _FILE_HANDLER.setFormatter(formatter)
        logging.getLogger('').addHandler(_FILE_HANDLER)
    logging.info('Logging to file %s [mode=\'%s\', level=%s]',
                 os.path.abspath(filename), filemode,
                 logging.getLevelName(_level))
