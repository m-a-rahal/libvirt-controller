from libvirt_api.json_xml import *

# definitions
XML = 0
JSON = 1


# verify integrity
def verify_integrity(code: str, type_: int):
    """
    Checks if the transformation from json to xml (or the other way) keeps the content of the object the same,
    NOTE: this method only compares the internal representations, not the initial text with the final one
    :param code: a string with either xml or json content
    :param type_: 0 for XML or 1 for JSON
    :return: true, if the data is the same, false otherwise
    """
    if type_ == XML:
        x = dict1 = xml_to_dict(code)
        x = dict_to_json(x)
        x = dict2 = json_to_dict(x)
    elif type_ == JSON:
        x = dict1 = json_to_dict(code)
        x = dict_to_xml(x)
        x = dict2 = xml_to_dict(x)
    return dict1 == dict2


# NOT NEEDED ------------------------------------------------------------------

# json objects are set-like, their equality is not affected by their order
# so use this to unify the order before comparison
# source = https://stackoverflow.com/a/25851972
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
