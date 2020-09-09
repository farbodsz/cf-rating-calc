"""Contains helper functions used across other modules."""

from sys import stderr

def log(msg):
    """Logs messages to stderr."""
    stderr.write(msg + "\n")
    stderr.flush()

