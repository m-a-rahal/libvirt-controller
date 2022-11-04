import json
import xmltodict

# JSON, XML to intermediate encoding (dictionary)
xml_to_dict = xmltodict.parse
json_to_dict = json.loads
dict_to_json = json.dumps
dict_to_xml = xmltodict.unparse


# JSON to XML directly (and vise versa)
def xml_to_json(xml_code):
    return json.dumps(xmltodict.parse(xml_code))


def json_to_xml(json_code):
    return xmltodict.unparse(json.loads(json_code))
