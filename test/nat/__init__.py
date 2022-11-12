from pycsp.parallel import *

@process
def send_requests():
    """
    the role of this is to simulate requests being sent to the controller,
    many instances of this class will run
    """