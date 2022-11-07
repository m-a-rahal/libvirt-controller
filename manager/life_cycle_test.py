import libvirt
import traceback

from manager import Manager, example_request

if __name__ == '__main__':
    manager = Manager()
    conn = manager.new_connection(Manager.DEFAULT_URI)
    try:
        if conn is None:
            exit(1)

        # create & run a VM (guest domain)
        domain = conn.createXML(example_request())

        # pause domain
        domain.save()
        # save domain

        # restore domain

        # destroy domain
        domain.destroy()

    except:
        print(traceback.format_exc())
    finally:
        # VERY IMPORTANT, close connection at the end
        print(f'closing connection {conn}')
        conn.close()