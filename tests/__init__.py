from __future__ import print_function

import threading
import time
from datetime import datetime

from libvirt import virConnect, virDomain

from libvirt_api import JsonXmlDict, xml_to_dict, LibvirtManager
from tests.utils import run_as_thread, Future


def load_xml_example(src_file='../tests/examples/xmldoc_example.xml', **kwargs: object) -> str:
    """make sure to call this function with correct src_file path"""
    with open(src_file, 'r') as f:
        doc = f.read()
    dic = JsonXmlDict(xml_to_dict(doc))
    domain = dic['domain']
    for k, v in kwargs.items():
        domain[k] = v
    return dic.xml


def load_xml_examples(src_file: str = None):
    # TODO: add more examples to tests createXML/defineXML
    vm_name = f'vm_{datetime.now()}'
    if src_file is None:
        example1 = load_xml_example(name=vm_name)
    else:
        example1 = load_xml_example(src_file=src_file, name=vm_name)
    return [example1]


def create_test_domain(connection: virConnect, name: str = None, verbose=False):
    if name is None:
        name = f'test_domain_{datetime.now()}'
    desc = load_xml_example(name=name)
    if verbose:
        start_time = time.time()
        print(f'creating domain name={name}')
    domain = connection.createXML(desc)
    if verbose:
        if domain is not None:
            print(f'domain name={name} created successfully in {time.time() - start_time:0.2f} seconds')
        else:
            print(f'failed to created domain name={name}')
    return domain


def create_n_domains(n: int) -> list[virDomain]:
    """create n domains using threads"""
    threads: list[threading.Thread] = []

    @run_as_thread(thread_list=threads)
    def create_domain_as_attribute(future_: Future):
        with LibvirtManager() as connection:
            future_.return_value = create_test_domain(connection, verbose=True)

    futures = []
    for _ in range(n):
        future = Future()
        futures.append(future)
        create_domain_as_attribute(future)

    for t in threads:
        t.join()

    return [f.return_value for f in futures]


class TempDomain:
    def __init__(self, connection: virConnect):
        self.domain: virDomain | None = None
        self.connection = connection

    def __enter__(self):
        domain = create_test_domain(self.connection, verbose=True)
        self.domain = domain
        return domain

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.domain.destroy()
