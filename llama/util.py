"""Utility library for LLAMA.

This provides utility functions used across the project.
"""


def array_split(iterable, n):
    """Split a list into chunks of ``n`` length."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


def mean(iterable):
    """Returns the average of the list of items."""
    return sum(iterable) / len(iterable)
