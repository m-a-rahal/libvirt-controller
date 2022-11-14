from __future__ import print_function

from datetime import datetime

from libvirt_api import JsonXmlDict, xml_to_dict


def load_xml_example(src_file='tests/examples/xmldoc_example.xml', **kwargs: object) -> str:
    with open(src_file, 'r') as f:
        doc = f.read()
    dic = JsonXmlDict(xml_to_dict(doc))
    domain = dic['domain']
    for k, v in kwargs.items():
        domain[k] = v
    return dic.xml


def load_xml_examples():
    # TODO: add more examples to tests createXML/defineXML
    vm_name = f'vm_{datetime.now()}'
    example1 = load_xml_example(src_file='../tests/examples/xmldoc_example.xml', name=vm_name)
    return [example1]
