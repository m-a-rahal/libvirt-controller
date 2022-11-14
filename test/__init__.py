from __future__ import print_function

from datetime import datetime

from libvirt_api import JsonXmlDict, xml_to_dict


def load_xml_example(**kwargs: object) -> str:
    with open('libvirt_api/json_xml/examples/xmldoc_example.xml', 'r') as f:
        doc = f.read()
    dic = JsonXmlDict(xml_to_dict(doc))
    domain = dic['domain']
    for k, v in kwargs.items():
        domain[k] = v
    return dic.xml


def load_xml_examples():
    # TODO: add more examples to test createXML/defineXML
    vm_name = f'vm_{datetime.now()}'
    example1 = load_xml_example(name=vm_name)
    return [example1]
