import libvirt
import sys
from manager.request_handler import RequestHandler


class Manager:
    def __init__(self):
        self._running = True

    def __int__(self):
        self.connections = []

    def new_connection(self, name) :
        conn = libvirt.open(name)
        if conn is None:
            print(f'Failed to open connection to {name}', file=sys.stderr)
            return None
        print('Connection successful')
        self.connections.append(conn)
        return conn

    def close_all_connection(self):
        for conn in self.connections:
            conn.close()

    def isRunning(self):
        return self._running


if __name__ == '__main__':
    manager = Manager()
    connection = Manager.new_connection('qemu:///system')
    while manager.isRunning():
        xmldesc = RequestHandler.get_request()
        connection.createXML(xmldesc)
    

