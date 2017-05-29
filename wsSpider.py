'''
wsSpider get grades from student input
:argv 1: name
:argv 2: lastname
:argv 3: year
:argv 4: term

$python3 wsSpider <name> <lastname> <year> <term>

Example: $ python3 wsSpider.py John Doe 2017 1
         $ python3 wsSpider.py Oscar 'De la Olla' 2014 2
'''
import sys
from tabulate import tabulate

from wsEspolClient import Client


def remove_unused_chars(string):
    return string.replace('&nbsp;', '')


def processing_grades(grades):
    if isinstance(grades, dict):
        # if 1 course
        result = [grades.get('MATERIA'), grades.get('NOTA1'), grades.get('NOTA2'),
                  grades.get('NOTA3'), grades.get('PROMEDIO'),
                  remove_unused_chars(grades.get('ESTADO')),
                  grades.get('VEZ')]
        grades_table.append(result)
        print(tabulate(grades_table, headers=table_header,
                       tablefmt="fancy_grid"))
        print(line_break)
        print(separator)
    elif isinstance(grades, list):
        # if group of courses
        for grade in grades:
            course = [grade.get('MATERIA'), grade.get('NOTA1'), grade.get('NOTA2'),
                      grade.get('NOTA3'), grade.get('PROMEDIO'),
                      remove_unused_chars(grade.get('ESTADO')),
                      grade.get('VEZ')]
            grades_table.append(course)
        print(tabulate(grades_table, headers=table_header,
                       tablefmt="fancy_grid"))
        print(line_break)
        print(separator)
    else:
        print("Oops, No courses available")


def print_info_student(name, lastname, student_code):
    print(separator)
    print(line_break)
    print("INFORMACION DE ESTUDIANTE")
    print("NOMBRE: {} {}".format(name, lastname))
    print("CODIGO: {}".format(student_code))
    print(line_break)

if __name__ == '__main__':
    client = Client()

    separator = '===' * 50
    line_break = '\n'
    table_header = ['MATERIA', 'PARCIAL', 'FINAL',
                    'MEJORAMIENTO', 'PROMEDIO', 'ESTADO', 'VEZ']

    name = sys.argv[1]
    lastname = sys.argv[2]
    year = sys.argv[3]
    term = sys.argv[4]

    grades_table = []

    try:
        student = client.ws_consultar_persona_nombres(name, lastname)
        if isinstance(student, dict):
            # if ws return 1 person
            print_info_student(student.get('NOMBRES'), student.get(
                'APELLIDOS'), student.get('CODESTUDIANTE'))
            try:
                grades = client.ws_consulta_calificaciones(
                    year, term, student.get('CODESTUDIANTE'))
                processing_grades(grades)
            except Exception as e:
                print("Something went wrong looking the grades :(")
        elif isinstance(student, list):
            # if ws return some people
            print(line_break)
            for index, element in enumerate(student):
                print("{} - {} {} {}".format(index + 1, element.get('NOMBRES'),
                                            element.get('APELLIDOS'), element.get('CODESTUDIANTE')))
            print(line_break)
            op = input("Ingrese el numero de la persona a consultar: ")
            print(line_break)
            tmp_student = student[int(op) - 1]
            print_info_student(tmp_student.get('NOMBRES'), tmp_student.get(
                'APELLIDOS'), tmp_student.get('CODESTUDIANTE'))
            grades = client.ws_consulta_calificaciones(
                year, term, tmp_student.get('CODESTUDIANTE'))
            processing_grades(grades)
        else:
            print('Oops, There are no people with that name')
    except Exception:
        print("Something went wrong searching this student :(")
