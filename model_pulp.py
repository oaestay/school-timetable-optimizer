from data import DIAS, PERIODOS, CURSOS, PROFESORES, ASIGNATURAS, \
    DEPARTAMENTO, DEPARTAMENTOS, CURSOS_DOBLES, PERIODOS_INICIO_MODULO, \
    REQUISITOS_ASIGNATURAS, REQUISITOS_REUNIONES, IMPARTE, \
    PROFESORES_JEFES, PROFESORES_NO_JEFES
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, \
    GLPK_CMD, GUROBI_CMD, PULP_CBC_CMD, COIN_CMD
import time

M = len(DIAS) * PERIODOS * 100

# Model
model = LpProblem("Asignacion de cursos", LpMinimize)

start_time = time.time()

"""
==============================================================================
                                Variables
==============================================================================
"""

X = LpVariable.dicts(
    "X",
    [
        (i, j, k, p, f)
        for i in CURSOS
        for j in PROFESORES
        for k in ASIGNATURAS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    cat="Binary",
)

alpha = LpVariable.dicts(
    "alpha",
    [
        (i, p, f)
        for i in CURSOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    cat="Binary",
)

beta = LpVariable.dicts(
    "beta",
    [
        (i, f)
        for i in CURSOS
        for f in DIAS
    ],
    lowBound=0,
    cat="Integer",
)

theta = LpVariable.dicts(
    "theta",
    [
        (i)
        for i in CURSOS
    ],
    lowBound=0,
    cat="Integer",
)

Y = LpVariable.dicts(
    "Y",
    [
        (j, d, p, f)
        for j in PROFESORES
        for d in DEPARTAMENTOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    cat="Binary",
)

Z = LpVariable.dicts(
    "Z",
    [
        (d, p, f)
        for d in DEPARTAMENTOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ],
    cat="Binary",
)

"""
==============================================================================
                             Restricciones
==============================================================================
"""

# Se agregan restricciones para fijar alpha
for i in CURSOS:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += lpSum([
                X[i, j, k, p, f]
                for j in PROFESORES
                for k in ASIGNATURAS
            ]) <= M * alpha[i, p, f]

for i in CURSOS:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += lpSum([
                X[i, j, k, p, f]
                for j in PROFESORES
                for k in ASIGNATURAS
            ]) >= alpha[i, p, f]

# Se agregan restricciones para fijar beta
for i in CURSOS:
    for f in DIAS:
        model += lpSum([
            p * (alpha[i, p, f] - alpha[i, p + 1, f])
            for p in range(1, PERIODOS)
        ]) + PERIODOS * alpha[i, PERIODOS, f] == beta[i, f]

# Se agregan restricciones para fijar theta
for i in CURSOS:
    for f in DIAS:
        model += beta[i, f] <= theta[i]

# Los profesores asisten a las reuniones de su departamento

for j in PROFESORES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += (
                Z[DEPARTAMENTO[j], p, f] == Y[j, DEPARTAMENTO[j], p, f]
            )

# Los profesores asisten a las reuniones de GPT
for j in PROFESORES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += Z["GPT", p, f] == Y[j, "GPT", p, f]

# Los profesores jefes asisten a las reuniones de JEFES
for j in PROFESORES_JEFES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += Z["JEFES", p, f] == Y[j, "JEFES", p, f]

# Los profesores no jefes no asisten a las reuniones de JEFES
for j in PROFESORES_NO_JEFES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += Y[j, "JEFES", p, f] == 0

# Los profesores no asisten a las reuniones que no son de su departamento
for j in PROFESORES:
    for d in [
        d
        for d in DEPARTAMENTOS
        if d != "GPT" and
        d != "JEFES" and
        d != DEPARTAMENTO[j]
    ]:
        for p in range(1, PERIODOS + 1):
            for f in DIAS:
                model += Y[j, d, p, f] == 0

# Un curso, sólo puede recibir una asignatura,
# de un sólo profesor en el mismo momento:
for i in CURSOS:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += lpSum([
                X[i, j, k, p, f]
                for j in PROFESORES
                for k in ASIGNATURAS
            ]) <= 1

# Un profesor, sólo puede impartir una asignatura,
# a un sólo curso en el mismo momento:
for j in PROFESORES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            model += lpSum([
                X[i, j, k, p, f]
                for i in CURSOS
                for k in ASIGNATURAS
            ]) <= 1

# Los profesores sólo hacen clases de su especialidad
for j in PROFESORES:
    for k in [
        k
        for k in [
            k
            for k in ASIGNATURAS
            if k != "JEFATURA"
        ]
        if k not in IMPARTE[j]
    ]:
        model += lpSum([
            X[i, j, k, p, f]
            for i in CURSOS
            for p in range(1, PERIODOS + 1)
            for f in DIAS
        ]) == 0

# Se deben dictar la cantidad de horas requeridas
# por cada curso de cada asignatura
for i in CURSOS:
    for k in ASIGNATURAS:
        model += lpSum([
            X[i, j, k, p, f]
            for j in PROFESORES
            for p in range(1, PERIODOS + 1)
            for f in DIAS
        ]) == REQUISITOS_ASIGNATURAS[i][k]

# Se deben dictar la cantidad de horas requeridas en reuniones de departamentos
for d in DEPARTAMENTOS:
    model += lpSum([
        Z[d, p, f]
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ]) == REQUISITOS_REUNIONES[d]

# Un profesor no puede dictar clases y asistir a una reunión
# al mismo tiempo
for j in PROFESORES:
    for p in range(1, PERIODOS + 1):
        for f in DIAS:
            lpSum([
                X[i, j, k, p, f]
                for i in CURSOS
                for k in ASIGNATURAS
            ]) + lpSum([
                Y[j, d, p, f]
                for d in DEPARTAMENTOS
            ]) <= 1

# Los cursos tienen clases desde el primer periodo
for i in CURSOS:
    for f in DIAS:
        model += alpha[i, 1, f] == 1

# Para cada curso, se deben dictar asignaturas desde la mañana,
# sin interrupciones
for i in CURSOS:
    for n in range(1, PERIODOS + 1):
        for m in range(1, n - 1):
            for f in DIAS:
                model += (
                    n - m + 1 - lpSum([
                            alpha[i, p, f]
                            for p in range(m, n + 1)
                        ]
                    ) <= M * (2 - alpha[i, m, f] - alpha[i, n, f])
                )

for i in CURSOS:
    for k in CURSOS_DOBLES:
        for p in PERIODOS_INICIO_MODULO:
            for f in DIAS:
                lpSum([
                    X[i, j, k, p, f]
                    for j in PROFESORES
                ]) == lpSum([
                    X[i, j, k, p + 1, f]
                    for j in PROFESORES
                ])

for i in CURSOS:
    for k in CURSOS_DOBLES:
        for f in DIAS:
            lpSum([
                X[i, j, k, 7, f]
                for j in PROFESORES
            ]) == 0

# Objective
model += lpSum([
        theta[i]
        for i in CURSOS
    ]) + lpSum([
        p * Z[d, p, f]
        for d in DEPARTAMENTOS
        for p in range(1, PERIODOS + 1)
        for f in DIAS
    ]) / M


def printSolution():
    if model.status == 1:
        print("Cost: {}".format(model.objective))

        print("Cost: {} (calculated)".format(
            sum([
                theta[i].varValue
                for i in CURSOS
            ]) + sum([
                p * Z[d, p, f].varValue
                for d in DEPARTAMENTOS
                for p in range(1, PERIODOS + 1)
                for f in DIAS
            ]) / M
        ))

        sol_X = {
            (i, j, k, p, f): X[i, j, k, p, f].varValue
            for i in CURSOS
            for j in PROFESORES
            for k in ASIGNATURAS
            for p in range(1, PERIODOS + 1)
            for f in DIAS
        }

        sol_Y = {
            (j, d, p, f): Y[j, d, p, f].varValue
            for j in PROFESORES
            for d in DEPARTAMENTOS
            for p in range(1, PERIODOS + 1)
            for f in DIAS
        }

        sol_theta = {
            (i): theta[i].varValue
            for i in CURSOS
        }

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

        str_ = "===================\nHORARIOS CURSOS\n===================\n\n"
        for i in CURSOS:
            str_ += i + ": \n"
            for f in range(len(DIAS)):
                str_ += str(HORARIOS_CURSOS[i][f]) + "\n"

        str_ += "===================\nHORARIOS PROFESORES\n===================\n\n"
        for j in PROFESORES:
            str_ += j + ": \n"
            for f in range(len(DIAS)):
                str_ += str(HORARIOS_PROFESORES[j][f]) + "\n"

        str_ += "===================\nCURSOS PROFESORES\n===================\n\n"
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

# model.solve(PULP_CBC_CMD(msg=0))
# model.solve(COIN_CMD(msg=0))
model.solve(GUROBI_CMD(msg=0))
# model.solve(GLPK_CMD(msg=0))

model.writeLP("Horario.lp")

printSolution()
