from typing import List, Union
import libvirt
import sys
from manager.request_handler import RequestHandler


class Manager:
    def __init__(self):
        self._running = True

    def __int__(self):
        self.connections: List[libvirt.virConnect] = []

    def new_connection(self, uri) -> Union[libvirt.virConnect, None]:
        """
        Establishes connection and returns None if there's nothing to return
        :param uri: connection 
        :return:
        """
        conn = libvirt.open(uri)
        if conn is None:
            print(f'Failed to open connection to {uri}', file=sys.stderr)
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
    

