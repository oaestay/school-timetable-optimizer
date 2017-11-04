from data import DIAS, PERIODOS, CURSOS, PROFESORES, ASIGNATURAS, \
    DEPARTAMENTO, DEPARTAMENTOS, CURSOS_DOBLES, PERIODOS_INICIO_MODULO, \
    REQUISITOS_ASIGNATURAS, REQUISITOS_REUNIONES, IMPARTE, \
    PROFESORES_JEFES, PROFESORES_NO_JEFES
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

# Se agregan restricciones para fijar alpha
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

# Se agregan restricciones para fijar beta
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

# Se agregan restricciones para fijar theta
model.addConstrs(
    (
        beta[i, f] <= theta[i]
        for i in CURSOS
        for f in DIAS
    )
)

# Los profesores asisten a las reuniones de su departamento
model.addConstrs(
    (
        Z[DEPARTAMENTO[j], p, f] == Y[j, DEPARTAMENTO[j], p, f]
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los profesores asisten a las reuniones de GPT
model.addConstrs(
    (
        Z["GPT", p, f] == Y[j, "GPT", p, f]
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los profesores jefes asisten a las reuniones de JEFES
model.addConstrs(
    (
        Z["JEFES", p, f] == Y[j, "JEFES", p, f]
        for j in PROFESORES_JEFES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los profesores no jefes no asisten a las reuniones de JEFES
model.addConstrs(
    (
        Y[j, "JEFES", p, f] == 0
        for j in PROFESORES_NO_JEFES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los profesores no asisten a las reuniones que no son de su departamento
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

# Un curso, sólo puede recibir una asignatura,
# de un sólo profesor en el mismo momento:
model.addConstrs(
    (
        X.sum(i, "*", "*", p, f) <= 1
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Un profesor, sólo puede impartir una asignatura,
# a un sólo curso en el mismo momento:
model.addConstrs(
    (
        X.sum("*", j, "*", p, f) <= 1
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los profesores sólo hacen clases de su especialidad
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


# Se deben dictar la cantidad de horas requeridas por cada curso de cada asignatura
model.addConstrs(
    (
        X.sum(i, "*", k, "*", "*") == REQUISITOS_ASIGNATURAS[i][k]
        for i in CURSOS
        for k in ASIGNATURAS
    )
)

# Se deben dictar la cantidad de horas requeridas en reuniones de departamentos
model.addConstrs(
    (
        Z.sum(d, "*", "*") == REQUISITOS_REUNIONES[d]
        for d in DEPARTAMENTOS
    )
)

# Un profesor no puede dictar clases y asistir a una reunión
# al mismo tiempo
model.addConstrs(
    (
        X.sum("*", j, "*", p, f) + Y.sum(j, "*", p, f) <= 1
        for j in PROFESORES
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    )
)

# Los cursos tienen clases desde el primer periodo
model.addConstrs(
    (
        alpha[i, 1, f] == 1
        for i in CURSOS
        for f in DIAS
    )
)

# Para cada curso, se deben dictar asignaturas desde la mañana,
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

model.addConstrs(
    (
        X.sum(i, "*", k, p, f) == X.sum(i, "*", k, p + 1, f)
        for i in CURSOS
        for k in CURSOS_DOBLES
        for p in PERIODOS_INICIO_MODULO
        for f in DIAS
    )
)

model.addConstrs(
    (
        X.sum(i, "*", k, 7, f) == 0
        for i in CURSOS
        for k in CURSOS_DOBLES
        for f in DIAS
    )
)

# Objective
obj = theta.sum() + quicksum(
    p * Z[d, p, f]
    for d in DEPARTAMENTOS
    for p in range(1, PERIODOS + 1)
    for f in DIAS
) / M


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
