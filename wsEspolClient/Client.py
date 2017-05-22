'''
Client to consume Espol Web Services
'''
import os
from json import loads, dumps
from pysimplesoap.client import SoapClient, SimpleXMLElement
import xmltodict


class Client():
    '''
    Client class consume the wsEspol
    '''

    __service = None
    header = None
    namespaces = {
        'http://schemas.xmlsoap.org/soap/envelope/': None,
        'http://tempuri.org/': None,
        'http://www.w3.org/2001/XMLSchema': None
    }

    def __init__(self):
        self.__service = SoapClient(location='https://ws.espol.edu.ec/saac/wsandroid.asmx',
                                    namespace='http://tempuri.org/', action='http://tempuri.org/')
        self.header = SimpleXMLElement('<Header/>')
        security = self.header.add_child("GTSIAuthSoapHeader")
        security['xmlns'] = "http://tempuri.org/"
        security.marshall('usuario', os.environ['SPIDER_USER'])
        security.marshall('key', os.environ['SPIDER_KEY'])

    def __replace_special_chars(self, string):
        '''
        Replaces vowels with a string accent
        :param string: sting to remove acents
        :return: string without vocal acents
        '''
        return string.replace('\xf3', 'o').replace('\xe2', 'a').replace('\xed', 'i').replace(
            '\xe9', 'e').replace('\xfa', 'u').replace('\xc1', 'A').replace('\xc9', 'E').replace(
                '\xcd', 'I').replace('\xd3', 'O').replace('\xda', 'U').replace(
                    '\xf1', 'n').replace('\xd1', 'N')

    def __to_dict(self, order_dict):
        '''
        Convert OrderDict with nested OrderDict in regular dict
        :param order_dict: object type OrderDict
        :return: object type dict
        '''
        return loads(dumps(order_dict))

    def __bytes_to_dict(self, byte_object):
        '''
        Convert bytes response object to regular dict
        '''
        tmp = str(byte_object.decode('UTF-8', 'replace'))
        return self.__to_dict(xmltodict.parse(self.__replace_special_chars(tmp),
                                              process_namespaces=True,
                                              namespaces=self.namespaces))

    def __remove_unused_items(self, json):
        '''
        Return clean object or list of objects
        :param json: object list or dict
        :return: object without noise items
        '''
        if isinstance(json, list):
            result = []
            for item in json:
                try:
                    del item['@urn:schemas-microsoft-com:xml-diffgram-v1:id']
                    del item['@urn:schemas-microsoft-com:xml-msdata:rowOrder']
                    del item['@xmlns']
                except KeyError:
                    pass
                result.append(item)
            return result
        elif isinstance(json, dict):
            del json['@xmlns']
            del json['@urn:schemas-microsoft-com:xml-diffgram-v1:id']
            del json['@urn:schemas-microsoft-com:xml-msdata:rowOrder']
            return json
        else:
            return json

    def ws_consultar_persona_nombres(self, name, lastname):
        '''
        Consume wsConsultarPersonaPorNombres
        :param name: name of the student
        :param lastname: lastname of the student
        :return: object dict with the information or array with coincident people
        '''
        if name.isalpha() and lastname.isalpha():
            response = self.__service.wsConsultarPersonaPorNombres(nombre=name,
                                                                   apellido=lastname,
                                                                   headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsConsultarPersonaPorNombresResponse').get(
                    'wsConsultarPersonaPorNombresResult').get(
                        'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                            'NewDataSet').get('DATOSPERSONA')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('name and lastname invalid')

    def ws_consulta_calificaciones(self, year, term, student_code):
        '''
        Consume wsConsultaCalificaciones
        :param year: year to see grades
        :param term: academic term to see grades
        :param student_code: student id
        :return: array of dicts with the grades
        '''
        if student_code.isdigit() and year.isdigit() and term.isdigit():
            response = self.__service.wsConsultaCalificaciones(anio=str(year),
                                                               termino=str(term),
                                                               estudiante=student_code,
                                                               headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsConsultaCalificacionesResponse').get(
                    'wsConsultaCalificacionesResult').get(
                        'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                            'NewDataSet').get('CALIFICACIONES')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')
            