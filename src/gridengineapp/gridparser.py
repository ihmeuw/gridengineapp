from argparse import ArgumentParser
from logging import getLogger

LOGGER = getLogger(__name__)


class ArgumentError(Exception):
    """An error for command-line arguments."""


class GridParser(ArgumentParser):
    def error(self, message):
        """Override the base class because it calls sys.exit.
        This library uses the parser as an internal tool,
        not just for user interaction. For instance, it's used
        in testing, where an exception is more appropriate.

        If the status is 0, that means nothing is wrong, and
        the user requested ``--help``, so, yes, exit.

        Otherwise, print a message to standard error
        and raise an exception.
        """
        LOGGER.error(message)
        raise ArgumentError(message)
