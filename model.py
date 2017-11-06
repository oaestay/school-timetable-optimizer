from data import DIAS, PERIODOS, CURSOS, PRIMEROS, SEGUNDOS, TERCEROS, \
    CUARTOS, PROFESORES, ASIGNATURAS, DEPARTAMENTO, DEPARTAMENTOS, \
    ASIGNATURAS_DOBLES, PERIODOS_INICIO_MODULO, REQUISITOS_ASIGNATURAS, \
    REQUISITOS_REUNIONES, IMPARTE, PROFESORES_JEFES, PROFESORES_NO_JEFES, \
    ASIGNATURAS_RESTRINGIDAS, HORAS_MAX
from gurobipy import Model, quicksum, GRB
import time

M = len(DIAS) * PERIODOS * 100

# Model
model = Model("Asignacion de CURSOS")

start_time = time.time()

"""
==============================================================================
                                Variables
==============================================================================
"""

X = model.addVars(
    [
        (i, j, k, p, f)
        for i in CURSOS
        for j in PROFESORES
        for k in ASIGNATURAS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    vtype=GRB.BINARY
)

P = model.addVars(
    [
        (i, p, f)
        for i in CURSOS
        for p in range(1, PERIODOS)
        for f in DIAS
    ],
    vtype=GRB.BINARY
)

alpha = model.addVars(
    [
        (i, p, f)
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    vtype=GRB.BINARY,
)

beta = model.addVars(
    [
        (i, f)
        for i in CURSOS
        for f in DIAS
    ],
    vtype=GRB.INTEGER,
)

theta = model.addVars(
    [
        (i)
        for i in CURSOS
    ],
    vtype=GRB.INTEGER,
)

Y = model.addVars(
    [
        (j, d, p, f)
        for j in PROFESORES
        for d in DEPARTAMENTOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    vtype=GRB.BINARY,
)

Z = model.addVars(
    [
        (d, p, f)
        for d in DEPARTAMENTOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    vtype=GRB.BINARY,
)

model.setParam("Threads", 4)

# Update model to integrate new variables
model.update()

"""
==============================================================================
                             Restricciones
==============================================================================
"""

# (R1) Se agregan restricciones para fijar alpha
model.addConstrs(
    (
        X.sum(i, "*", "*", p, f)
        <= M * alpha[i, p, f]
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

model.addConstrs(
    (
        X.sum(i, "*", "*", p, f)
        >= alpha[i, p, f]
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R2) Se agregan restricciones para fijar beta
model.addConstrs(
    (
        quicksum(
            p * (alpha[i, p, f] - alpha[i, p + 1, f])
            for p in range(1, PERIODOS)
        ) + PERIODOS * alpha[i, PERIODOS, f] == beta[i, f]
        for i in CURSOS
        for f in DIAS
    )
)

# (R3) Se agregan restricciones para fijar theta
model.addConstrs(
    (
        beta[i, f] <= theta[i]
        for i in CURSOS
        for f in DIAS
    )
)

# (R4) Los profesores asisten a las reuniones de su departamento
model.addConstrs(
    (
        Z[DEPARTAMENTO[j], p, f] == Y[j, DEPARTAMENTO[j], p, f]
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R5) Los profesores asisten a las reuniones de GPT
model.addConstrs(
    (
        Z["GPT", p, f] == Y[j, "GPT", p, f]
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R6) Los profesores jefes asisten a las reuniones de JEFES
model.addConstrs(
    (
        Z["JEFES", p, f] == Y[j, "JEFES", p, f]
        for j in PROFESORES_JEFES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R7) Los profesores no jefes no asisten a las reuniones de JEFES
model.addConstrs(
    (
        Y[j, "JEFES", p, f] == 0
        for j in PROFESORES_NO_JEFES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R8) Los profesores no asisten a las reuniones que no son de su departamento
model.addConstrs(
    (
        Y[j, d, p, f] == 0
        for j in PROFESORES
        for d in [
            d
            for d in DEPARTAMENTOS
            if d != "GPT" and
            d != "JEFES" and
            d != DEPARTAMENTO[j]
        ]
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R9) Un curso, solo puede recibir una asignatura,
# de un solo profesor en el mismo momento:
model.addConstrs(
    (
        X.sum(i, "*", "*", p, f) <= 1
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R10) Un profesor, solo puede impartir una asignatura,
# a un solo curso en el mismo momento:
model.addConstrs(
    (
        X.sum("*", j, "*", p, f) <= 1
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R11) Los profesores solo hacen clases de su especialidad
model.addConstrs(
    (
        X.sum("*", j, k, "*", "*") == 0
        for j in PROFESORES
        for k in [
            k
            for k in [
                k
                for k in ASIGNATURAS
                if k != "JEFATURA"
            ]
            if k not in IMPARTE[j]
        ]
    )
)


# (R12) Se deben dictar la cantidad de horas requeridas por
# cada curso de cada asignatura
model.addConstrs(
    (
        X.sum(i, "*", k, "*", "*") == REQUISITOS_ASIGNATURAS[i][k]
        for i in CURSOS
        for k in ASIGNATURAS
    )
)

# (R13) Se deben dictar la cantidad de horas requeridas
# en reuniones de departamentos
model.addConstrs(
    (
        Z.sum(d, "*", "*") == REQUISITOS_REUNIONES[d]
        for d in DEPARTAMENTOS
    )
)

# (R14) Un profesor no puede dictar clases y asistir a una reunión
# al mismo tiempo
model.addConstrs(
    (
        X.sum("*", j, "*", p, f) + Y.sum(j, "*", p, f) <= 1
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# (R15) Los cursos tienen clases desde el primer periodo
model.addConstrs(
    (
        alpha[i, 1, f] == 1
        for i in CURSOS
        for f in DIAS
    )
)

# (R16) Para cada curso, se deben dictar asignaturas desde la manana,
# sin interrupciones
model.addConstrs(
    (
        n - m + 1 - quicksum(
            alpha[i, p, f]
            for p in range(m, n + 1)
        ) <= M * (2 - alpha[i, m, f] - alpha[i, n, f])
        for i in CURSOS
        for n in range(1, PERIODOS + 1)
        for m in range(1, n - 1)
        for f in DIAS
    )
)

# (R17) Hay cursos que deben realizarse sin recreo entremedio,
# dos modulos seguidos, en las primeras 6 horas:
model.addConstrs(
    (
        X.sum(i, "*", k, p, f) == X.sum(i, "*", k, p + 1, f)
        for i in CURSOS
        for k in ASIGNATURAS_DOBLES
        for p in PERIODOS_INICIO_MODULO
        for f in DIAS
        if REQUISITOS_ASIGNATURAS[i][k] % 2 == 0
    )
)

# (RX) Biologia fisica y quimica se realizan dentro de las primeras 6 horas:
model.addConstrs(
    (
        X.sum(i, "*", k, p, f) == 0
        for i in CURSOS
        for k in [
            "BIOLOGIA",
            "FISICA",
            "QUIMICA"
        ]
        for p in range(7, PERIODOS)
        for f in DIAS
    )
)
# (RX) Jefatura se realiza al septimo y octavo modulo:
model.addConstrs(
        X.sum(i, "*", "JEFATURA", 7, f) == 0
        for i in CURSOS
        for f in DIAS
)

model.addConstrs(
        X.sum(i, "*", "JEFATURA", 8, f) == 0
        for i in CURSOS
        for f in DIAS
)


# (R18) Hay asignaturas que no se pueden realizar en el septimo
# u octavo modulo:
model.addConstrs(
        X.sum("*", "*", k, p, "*") == 0
        for k in ASIGNATURAS_RESTRINGIDAS
        for p in range(7, 9)
)

# (R19) Para los terceros y cuartos, lenguajes y matematicas se
# deben dictar hasta el sexto modulo:
model.addConstrs(
    (
        X.sum(i, "*", k, p, "*") == 0
        for i in TERCEROS + CUARTOS
        for k in ["MATEMATICAS", "LENGUAJE"]
        for p in range(7, PERIODOS + 1)
    )
)

# (R20) No se realizan clases en el onceavo modulo
model.addConstrs(
    (
        X.sum(i, j, k, 11, f) == 0
        for i in CURSOS
        for j in PROFESORES
        for k in ASIGNATURAS
        for f in DIAS
    )
)

# (R21) Se realizan la cantidad de horas maximas en cada asignatura
model.addConstrs(
    (
        X.sum(i, "*", k, "*", f) <= HORAS_MAX[k]
        for i in CURSOS
        for k in ASIGNATURAS
        for f in DIAS
    )
)

# (R22) Se cuentan los cambios de asignaturas
model.addConstrs(
    (
        X.sum(i, "*", k_1, p + 1, f) - X.sum(i, "*", k_0, p, f) <= P[i, p, f]
        for i in CURSOS
        for k_0 in ASIGNATURAS
        for k_1 in ASIGNATURAS
        for p in range(1, PERIODOS)
        for f in DIAS
        if k_0 != k_1
    )
)

# Objective
obj = P.sum() + theta.sum() / len(CURSOS) + quicksum(
    p * Z[d, p, f]
    for d in DEPARTAMENTOS
    for p in range(1, PERIODOS + 1)
    for f in DIAS
) / (M + (PERIODOS + 1))


model.setObjective(obj, GRB.MINIMIZE)


def printSolution():
    if model.status == GRB.Status.OPTIMAL:
        print('\nCost: %g' % model.objVal)

        sol_X = model.getAttr('X', X)
        sol_Y = model.getAttr('X', Y)
        sol_theta = model.getAttr('X', theta)

        HORARIOS_CURSOS = {
            i: [["" for _ in range(PERIODOS)] for t in range(len(DIAS))]
            for i in CURSOS
        }

        CURSOS_PROFESORES = {
            i: [["" for _ in range(PERIODOS)] for t in range(len(DIAS))]
            for i in CURSOS
        }

        HORARIOS_PROFESORES = {
            j: [["" for _ in range(PERIODOS)] for t in range(len(DIAS))]
            for j in PROFESORES
        }

        for i in CURSOS:
            for p in range(1, PERIODOS + 1):
                for f in range(len(DIAS)):
                    for j in PROFESORES:
                        for k in ASIGNATURAS:
                            if sol_X[i, j, k, p, DIAS[f]] > 0:
                                HORARIOS_CURSOS[i][f][p - 1] = k
                                CURSOS_PROFESORES[i][f][p - 1] = j

        for j in PROFESORES:
            for p in range(1, PERIODOS + 1):
                for f in range(len(DIAS)):
                    for i in CURSOS:
                        for k in ASIGNATURAS:
                            if sol_X[i, j, k, p, DIAS[f]] > 0:
                                HORARIOS_PROFESORES[j][f][p - 1] = k

                    for d in DEPARTAMENTOS:
                        if sol_Y[j, d, p, DIAS[f]] > 0:
                            HORARIOS_PROFESORES[j][f][p - 1] = "REUNION " + d

        str_ = "===================\nHORARIOS CURSOS\n====================\n\n"
        for i in CURSOS:
            str_ += i + ": \n"
            for f in range(len(DIAS)):
                str_ += str(HORARIOS_CURSOS[i][f]) + "\n"

        str_ += "===================\nHORARIOS PROFESORES\n===============\n\n"
        for j in PROFESORES:
            str_ += j + ": \n"
            for f in range(len(DIAS)):
                str_ += str(HORARIOS_PROFESORES[j][f]) + "\n"

        str_ += "===================\nCURSOS PROFESORES\n=================\n\n"
        for i in CURSOS:
            str_ += i + ": \n"
            for f in range(len(DIAS)):
                str_ += str(CURSOS_PROFESORES[i][f]) + "\n"

        str_ = str_.encode('ascii', 'ignore').decode('ascii')

        with open("./result.txt", "w+") as f:
            f.write(str_)

        print(str_)

    else:
        print('No solution')


# Solve

model.optimize()
model.write("model.lp")
printSolution()
