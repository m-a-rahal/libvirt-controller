import sys


class MissingAttributeError(Exception):
    pass


class UnrecognizedOption(Exception):
    pass


class Unimplemented(Exception):
    """use when a feature is not implemented yet, and you want ot remember implementing it"""
    pass


def print_stderr(msg):
    print(msg, file=sys.stderr)
