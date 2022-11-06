import libvirt

from json_xml import xml_to_json
from json_xml.random import random_json_request


class RequestHandler:

    @staticmethod
    def get_request():
        """
        receives and returns requests from NAT
        :return: a json string request
        """
        return ()

    @staticmethod
    def send_response(response: str):
        """
        send
        :param response: json (transformed) response from libvirt
        :return: return true, if sucess, else 0
        """
        xml_to_json(response)
        # send the response, & if success
        return True

    @staticmethod
    def on_request(request: str):
        """
        when request is received, what to do?
        :param request: json string request
        :return:
        """
        conn = libvirt.open()
        conn.createXML(request)
