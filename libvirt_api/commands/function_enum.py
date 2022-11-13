from __future__ import annotations


class FunctionEnum:
    counter = 0

    def __eq__(self, other: FunctionEnum):
        return self.value == other.value

    def __lt__(self, other: FunctionEnum):
        return self.value < other.value

    def __init__(self, f):
        self.f = f
        self.value = FunctionEnum.counter
        FunctionEnum.counter += 1

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)
