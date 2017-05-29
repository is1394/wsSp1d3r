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
                                                               termino=str(
                                                                   term),
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

    def ws_consulta_codigo_estudiante(self, username):
        '''
        Consume wsConsultaCodigoEstudiante
        :param user: username of the student
        :return: json with the student code
        '''
        if username.isalpha():
            response = self.__service.wsConsultaCodigoEstudiante(
                user=username, headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get(
                'Body').get('wsConsultaCodigoEstudianteResponse').get(
                    'wsConsultaCodigoEstudianteResult').get(
                        'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                            'NewDataSet').get('MATRICULA')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError(
                'username is a string without numbers or special chars')

    def ws_consulta_periodo_actual(self):
        '''
        Consume wsConsultaPeriodoActual
        :return: json with actual academic term
        '''
        response = self.__service.wsConsultaPeriodoActual(headers=self.header)
        json_response = self.__bytes_to_dict(response.as_xml())
        json_response = json_response.get('Envelope').get('Body').get(
            'wsConsultaPeriodoActualResponse').get('wsConsultaPeriodoActualResult').get(
                'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                    'NewDataSet').get('PERIODO')
        return self.__remove_unused_items(json_response)

    def ws_estudiantes_registrados(self, course_code, parallel):
        '''
        Consume wsEstudiantesRegistrados
        :param course_code: code course e.g. 'ICM0001'
        :param parallel: the number of the course to find e.g. 1
        :return: array with the students {code, name}
        the name is _x0031_ <- wtf?
        '''
        if course_code.isalnum() and parallel.isdigit():
            response = self.__service.wsEstudiantesRegistrados(codigoMateria=course_code, 
                paralelo=int(parallel), headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsEstudiantesRegistradosResponse').get('wsEstudiantesRegistradosResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('ESTUDIANTESREGISTRADOS')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('invalid inputs')

    def ws_horario_clases(self, course_code, parallel):
        '''
        Consume wsHorarioClases
        :param course_code: code course e.g. 'ICM0001'
        :param parallel: the number of the course to find e.g. 1
        :return: list with hours or dict with 1 hour
        '''
        if course_code.isalnum() and parallel.isdigit():
            response = self.__service.wsHorarioClases(codigoMateria=course_code,
                paralelo=int(parallel), headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsHorarioClasesResponse').get('wsHorarioClasesResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('HORARIOCLASES')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('invalid inputs')

    def ws_horario_examenes(self, course_code, parallel):
        '''
        Consume wsHorarioExamenes
        :param course_code: code course e.g. 'ICM0001'
        :param parallel: the number of the course to find e.g. 1
        :return: list with tests date
        '''
        if course_code.isalnum() and parallel.isdigit():
            response = self.__service.wsHorarioExamenes(codigoMateria=course_code,
                paralelo=int(parallel), headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsHorarioExamenesResponse').get('wsHorarioExamenesResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('_x0020__x0020_')
            # '_x0020__x0020_' <- wtf? 
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('invalid inputs')

    def ws_materias_registradas(self, student_code):
        '''
        Consume wsMateriasRegistradas
        :param student_code: student id
        '''
        if student_code.isdigit():
            response  = self.__service.wsMateriasRegistradas(codigoestudiante=student_code,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsMateriasRegistradasResponse').get('wsMateriasRegistradasResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('MATERIASREGISTRADAS')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')

    def ws_info_estudiante_general(self, student_code):
        '''
        Consume wsInfoEstudianteGeneral
        :param student_code: student id
        '''
        if student_code.isdigit():
            response = self.__service.wsInfoEstudianteGeneral(codestudiante=student_code,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoEstudianteGeneralResponse').get('wsInfoEstudianteGeneralResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('ESTUDIANTE')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')
    
    def ws_info_estudiante(self, student_code):
        '''
        consume wsInfoEstudiante
        :param student_code: student id
        '''
        if student_code.isdigit():
            response = self.__service.wsInfoEstudiante(codigoEstudiante=student_code,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoEstudianteResponse').get('wsInfoEstudianteResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('INFOESTUDIANTE')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')
    
    def ws_info_estudiante_carrera(self, student_code):
        '''
        Consume wsInfoEstudianteCarrera
        :param student_code: student id
        '''
        if student_code.isdigit():
            response = self.__service.wsInfoEstudianteCarrera(codigoEstudiante=student_code,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoEstudianteCarreraResponse').get('wsInfoEstudianteCarreraResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('ESTUDIANTECARRERA')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')
    
    def ws_info_personal_estudiante(self, student_code, dni):
        '''
        Consume wsInfoPersonalEstudiante
        :param student_code: student id
        :param dni: dni code
        '''
        if student_code.isdigit() and dni.isdigit():
            response = self.__service.wsInfoPersonalEstudiante(matricula=student_code,
                identificacion=dni, headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoPersonalEstudianteResponse').get('wsInfoPersonalEstudianteResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('INFOPERSONALESTUDIANTE')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code or dni invalid')
    
    def ws_info_usuario(self, user):
        '''
        Consume wsInfoUsuario
        :param user: username in the academic system
        '''
        if user.isalpha():
            response = self.__service.wsInfoUsuario(usuario=user,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoUsuarioResponse').get('wsInfoUsuarioResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('INFORMACIONUSUARIO')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('username incorrect')
    
    def ws_info_paralelo(self, course_code, parallel):
        '''
        Consume wsInfoparalelo
        :param course_code: code course e.g. 'ICM0001'
        :param parallel: the number of the course to find e.g. 1
        '''
        if course_code.isalnum() and parallel.isdigit():
            response = self.__service.wsInfoparalelo(codigoMateria=course_code,
                paralelo=int(parallel), headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsInfoparaleloResponse').get('wsInfoparaleloResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('INFORMACIONMATERIA')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('invalid inputs')
    
    def ws_materias_disponibles(self, student_code):
        '''
        Consume wsMateriasDisponibles
        :param student_code: student id 
        '''
        if student_code.isdigit():
            response = self.__service.wsMateriasDisponibles(codigoestudiante=student_code,
                headers=self.header)
            json_response = self.__bytes_to_dict(response.as_xml())
            json_response = json_response.get('Envelope').get('Body').get(
                'wsMateriasDisponiblesResponse').get('wsMateriasDisponiblesResult').get(
                    'urn:schemas-microsoft-com:xml-diffgram-v1:diffgram').get(
                        'NewDataSet').get('MATERIASDISPONIBLES')
            return self.__remove_unused_items(json_response)
        else:
            raise AttributeError('student code must be a string of numbers')
