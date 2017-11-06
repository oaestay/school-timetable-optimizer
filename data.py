import csv

CURSOS = [
    "1A",
    "1B",
    "1C",
    "1D",
    "1E",
    "2A",
    "2B",
    "2C",
    "2D",
    "2E",
    "3A",
    "3B",
    "3C",
    "3D",
    "3E",
    "4A",
    "4B",
    "4C",
    "4D",
    "4E",
]

PRIMEROS = [
    "1A",
    "1B",
    "1C",
    "1D",
    "1E",
]

SEGUNDOS = [
    "2A",
    "2B",
    "2C",
    "2D",
    "2E",
]

TERCEROS = [
    "3A",
    "3B",
    "3C",
    "3D",
    "3E",
]

CUARTOS = [
    "4A",
    "4B",
    "4C",
    "4D",
    "4E",
]

PROFESORES = [
    "BELTRAND CRUZ CRISTIAN ALEJANDRO",
    "MARDONES VASQUEZ MARTA GEORGINA",
    "DONOSO ADARO MANUEL HERNAN",
    "ENCALADA PINO PAMELA VICTORIA",
    "VASQUEZ MIRANDA TAMARA DANIELA",
    "VASQUEZ VERGARA STEFANY ANDREA",
    "CRUZ MUÑOZ BARBARA PATRICIA",
    "ALEGRIA ESPINOZA MARIA ISABEL",
    "CATALDO NUÑEZ FABIOLA ANDREA",
    "CONA LINCOQUEO MARIANELA MERCEDES",
    "CORNEJO TRONCOSO LAURA CECILIA",
    "ERICES ZUÑIGA KELLY WENDOLLYN",
    "FAJARDO PEREIRA FRANCO CRISTHOFER",
    "IZQUIERDO MUÑOZ MARCIA LORENA",
    "LABRAÑA MARTINEZ CLAUDIA VALESKA",
    "MAULEN QUIROZ RUTH DANIELA",
    "PARADA ROJAS PAULA ANDREA",
    "PAVEZ TAPIA DAVID IGNACIO",
    "PRIETO URRA NERY DIOMARA",
    "RAMIREZ CACERES BARBARA PATRICIA",
    "RIVERA BARRAZA DANIELA PAZ",
    "RIVERA MONTOYA JOSE ANTONIO",
    "SANDOVAL SANDOVAL MARIA ISABEL",
    "SOTO FERRADA MARCELA ANDREA",
    "VALDES GILI ANTONIA",
    "VALDIVIA HUERTA PAOLA MARGARITA",
    "BARROS VIDAL VICTOR IGNACIO",
    "BERRIOS RAMIREZ PAULO ANDRES",
    "DIAZ HILLMER PAOLA ANDREA",
    "FAUNDEZ ESPINA DAYANNA PAOLA",
    "GATICA GUZMAN JAVIERA CAMILA",
    "LARA GARCIA BALDOMERO DANTE",
    "LEON LAGOS ROMINA LAGOS",
    "MIRANDA VERA NELSON GUILLERMO",
    "PEHUEN JORQUERA MARIA ANDREA",
    "SEPULVEDA RETAMAL RODRIGO ANTONIO",
    "TOLOZA LOBOS CRISTIAN ARIEL",
    "WEISS FUENTES NATHALIE DE JESUS EL",
    "URRA PARRA CRISTIAN GABRIEL",
    "GONZALEZ MANRIQUEZ ROCIO ALEJANDRA",
    "CIFUENTES NATALIA"
]

ASIGNATURAS = [
    "INNOVACION COCINA INTERNACIONAL",
    "ELAB BEBIDAS ALCOHOLICAS",
    "ARTES VISUALES",
    "LENGUAJE",
    "RECEPECIÓN Y ALMACENAMIENTO",
    "INGLES",
    "BIOLOGIA",
    "EXPRESION MUSICAL P",
    "PREP MONTAJE BUFFET",
    "EXPRESION LITERARIA",
    "INNOVACION PASTERERIA Y",
    "SIST OPERATIVOS REDES",
    "PLANIF DE LA PRODUCCIÓN",
    "ACTIVIDADES EDUCATIVAS",
    "INST MANT BAS TERM INFORM",
    "EMPRENDIMIENTO",
    "RECREACION Y BIENESTAR DE",
    "QUIMICA",
    "ELABORACION DE MENU",
    "OPER Y FUND TELECO",
    "ED. FISICA",
    "MANT CIRC ELECTRONICOS",
    "COMUNIC INALAMBRICAS",
    "FISICA",
    "RELIGION",
    "COCINA CHILENA",
    "HIGIENE",
    "ELAB PROD REPOSTERIA",
    "HISTORIA",
    "ELAB BAJA COMPLEJIDAD",
    "SERVICIO COMEDOR",
    "ELAB PASTAS Y MASAS",
    "INST REDES TELEF CONVE",
    "ED. TECNOLOGICA",
    "MATEMATICAS",
    "ELAB PROD PASTELERIA",
    "SALUD EN PARVULO",
    "INST CONFIG REDES",
    "RELACION C/FAMILIA",
    "MATERIAL DIDACTICO",
    "MANT REDES ACCES BANDA",
    "HIGIENE Y SEGURIDAD",
    "TIC´S",
    "DISEÑO Y PROGRAMACION",
    "ALIMENTACION PARVULO",
    "INST SERV BASICO TELCO",
    "ACONDICIMIENTO FISICO",
]

DEPARTAMENTOS = [
    "PARVULO",
    "LENGUAJE",
    "MATEMATICAS",
    "HISTORIA",
    "GASTRONOMIA",
    "INGLES",
    "DEPORTE Y EDUCACION FISICA",
    "CIENCIAS",
    "RELIGION",
    "TELECOMUNICACIONES",
    "TECNOLOGÍA",
    "GPT",
    "JEFES"
]

PERIODOS = 11

DIAS = [
    "LUNES",
    "MARTES",
    "MIERCOLES",
    "JUEVES",
    "VIERNES",
]

REQUISITOS_ASIGNATURAS = {}
with open('./data/cursos.csv') as file:
    cursos = csv.DictReader(file)
    for curso in cursos:
        _curso = dict(curso)
        courses = {
            k: int(v)
            for k, v in curso.items()
            if k != 'CURSOS'
        }
        REQUISITOS_ASIGNATURAS[_curso['CURSOS']] = courses

for i in CURSOS:
    REQUISITOS_ASIGNATURAS[i]["JEFATURA"] = 2

REQUISITOS_REUNIONES = {
    "PARVULO": 1,
    "LENGUAJE": 1,
    "MATEMATICAS": 1,
    "HISTORIA": 1,
    "GASTRONOMIA": 1,
    "INGLES": 1,
    "DEPORTE Y EDUCACION FISICA": 1,
    "CIENCIAS": 1,
    "RELIGION": 1,
    "TELECOMUNICACIONES": 1,
    "TECNOLOGÍA": 1,
    "GPT": 2,
    "JEFES": 1
}

IMPARTE = {}

with open('./data/profesores.csv') as file:
    profesores = csv.DictReader(file)
    for profe in profesores:
        _profe = dict(profe)
        courses = [
            k
            for k, v in profe.items()
            if k != 'PROFESOR' and int(v) > 0
        ]
        IMPARTE[_profe['PROFESOR']] = courses

JEFATURA = {}
with open('./data/profesores-jefes.csv') as file:
    jefaturas = csv.DictReader(file)
    for profe in jefaturas:
        _profe = dict(profe)
        JEFATURA[_profe['PROFESOR']] = _profe['CURSOS'] \
            if _profe['CURSOS'] else None

DEPARTAMENTO = {}
with open('./data/profesores-departamentos.csv') as file:
    jefaturas = csv.DictReader(file)
    for profe in jefaturas:
        _profe = dict(profe)
        DEPARTAMENTO[_profe['PROFESORES']] = _profe['DEPARTAMENTO'] \
            if _profe['DEPARTAMENTO'] else None

# Filtros

PROFESORES_JEFES = [
    j
    for j in PROFESORES
    if JEFATURA[j] is not None
]

PROFESORES_NO_JEFES = [
    j
    for j in PROFESORES
    if JEFATURA[j] is None
]

PERIODOS_INICIO_MODULO = [
    1,
    3,
    5,
]

# ASIGNATURAS_DOBLES = [
#     "BIOLOGIA",
#     "FISICA",
#     "QUIMICA"
# ]

ASIGNATURAS_RESTRINGIDAS = [
    "FISICA",
    "QUIMICA",
    "BIOLOGIA",
    "INGLES",
    "ED. FISICA",
]

HORAS_MAX = {}
with open('./data/horas_max.csv') as file:
    horas_max = csv.DictReader(file)
    for asignaturas in horas_max:
        _asignatura = dict(asignaturas)
        HORAS_MAX[_asignatura['CURSOS']] = int(_asignatura['HORAS_MAX']) \
            if _asignatura['HORAS_MAX'] else 0


ASIGNATURAS_DOBLES = [
    "ARTES VISUALES",
    "LENGUAJE",
    "INGLES",
    "BIOLOGIA",
    "EXPRESION MUSICAL P",
    "EXPRESION LITERARIA",
    "SIST OPERATIVOS REDES",
    "EMPRENDIMIENTO",
    "QUIMICA",
    "ED. FISICA",
    "FISICA",
    "RELIGION",
    "HISTORIA",
    "ED. TECNOLOGICA",
    "MATEMATICAS",
    "TIC´S",
    "ACONDICIMIENTO FISICO",
]
