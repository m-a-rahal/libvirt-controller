# dependencies : xmltodict 0.13
from __future__ import print_function
from testing import test_all_files_in
import sys
import libvirt


def main():
    # testing XML JSON
    # test_all_files_in('examples')
    first_connection()

def first_connection():
    link = 'qemu:///system'
    conn = libvirt.open(link)
    if conn == None:
        print(f'Failed to open connection to {link}', file=sys.stderr)
        exit(1)
    print('Connection successful')
    conn.close()
    print('Connection closed.')
    exit(0)

if __name__ == '__main__':
    main()
