import unittest
from pycsp.parallel import *
from pycsp.parallel.channel import ChannelEndRead, ChannelEndWrite


@process
def request_listener(channel_in: ChannelEndRead):
    request = channel_in()
    Spawn()

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()