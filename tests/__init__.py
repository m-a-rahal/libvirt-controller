from __future__ import print_function
from datetime import datetime

from libvirt import virConnect

from libvirt_api import JsonXmlDict, xml_to_dict


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


def create_test_domain(connection: virConnect, name: str = None):
    if name is None:
        name = f'test_domain_{datetime.now()}'
    desc = load_xml_example(name=name)
    domain = connection.createXML(desc)
    return domain