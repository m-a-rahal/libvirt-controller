import sys


def print_stderr(msg, raise_exception=True):
    print(msg, file=sys.stderr)
    if raise_exception:
        raise Exception(msg)
