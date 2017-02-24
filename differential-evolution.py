#! /usr/bin/python3

from random import random, randint
from math import sqrt, exp, cos
from multiprocessing import Pool
from numpy import arange
import csv

def target_function(params):

    #Ackley
    result = -20 * exp(-0.2 * sqrt(0.5 * (params[0] ** 2 + params[1] ** 2))) - \
             exp(0.5 * (cos(6.2 * params[0]) + cos(6.2 * params[1]))) + 2.71 + 20

    # Beale
    # result = (1.5 - params[0] + params[0] * params[1]) ** 2 + (2.25 - params[0] \
    #          + params[0] * (params[1] ** 2)) ** 2 + \
    #          (2.625 - params[0] + params[0] * (params[1] ** 3)) ** 2

    # Bukin02    [-15, 5] [-3, 3]
    # result = 100 * (params[1] - 0.01 * params[0] ** 2 +1) + 0.01(params[0] + 10) ** 2

    # AMGM [0,10]
    # result = 0.5 * ((params[0] + params[1]) - sqrt(params[0] * params[1])) ** 2

    # Sodp [-1, 1]
    # result =  abs(params[0] * 2) + abs(params[1] * 3)

    # Treecani [-5, 5]
    # result = params[0] ** 4 +   4 * params[0] ** 3 + 4 * params[0] ** 2 + params[1] ** 2

    # Trigonometric2 [-500, 500]
    # result = (1 + 8 * (sin(7 * (params[0] - 0.9) ** 2)) ** 2 + 6 * (sin(14 * (params[0] \
    #          - 0.9) ** 2)) ** 2 + (params[0] - 0.9) ** 2) + (1 + 8 * (sin(7 * (params[1] \
    #          - 0.9) ** 2)) ** 2 + 6 * (sin(14 * (params[1] - 0.9) ** 2)) ** 2 + \
    #          (params[1] - 0.9) ** 2)


    # Cosine Mixture  [-1, 1]
    # result = -0.1 * (cos(5 * pi * params[0]) + cos(5 * pi * params[1])) - (params[0] \
    #          ** 2 + params[1] ** 2)

    # Rosenbrock
    # result = 0
    # for i in range(len(params) - 1):
    #     result += 100 * (params[i + 1] - params[i] ** 2) ** 2 + (params[i] - 1) ** 2

    return result

def differential_evolution(cr, f, np, dim, it, b_lo=-1, b_up=1):

    agents = [[(random() * (b_up - b_lo)) for x in range(dim)] for a in range(np)]

    for i in range(it):
        for x in range(np):

            a, b, c = randint(0, np - 1), randint(0, np - 1), randint(0, np - 1)
            while a == b or b == c or c == a or a == x or b == x or c == x:
                a, b, c = randint(0, np - 1), randint(0, np - 1), randint(0, np - 1)

            R = randint(0, dim)
            y = [None] * dim

            for i in range(dim):
                ri = random()
                if ri < cr or i == R:
                    y[i] = agents[a][i] + f * (agents[b][i] - agents[c][i])
                else:
                    y[i] = agents[x][i]

            if target_function(y) < target_function(agents[x]):
                agents[x] = y

    best = agents[0]
    best_fitness = target_function(agents[0])

    for a in agents:
        if target_function(a) < best_fitness:
            best = a
            best_fitness = target_function(a)

    return best


def run(params):

    cr_range, f_range, increment_step, repetitions, generation_size, \
    dimensions, iterations, b_lower, b_upper = params

    fitness = []

    cr_vals = [round(x, 6) for x in arange(cr_range[0], cr_range[1], increment_step).tolist()]
    f_vals = [round(x, 6) for x in arange(f_range[0], f_range[1], increment_step).tolist()]


    for cr in cr_vals:
        for f in f_vals:

            average_fitness = 0
            average_position = [0] * dimensions

            for r in range(repetitions):
                position = differential_evolution(cr, f, \
                           generation_size, dimensions, iterations, \
                           b_lower, b_upper)
                average_fitness += target_function(position)
                average_position = [sum(x) for x in zip(average_position, position)]

            average_fitness /= repetitions
            average_position = [x / repetitions for x in average_position]
            fitness.append([cr, f, average_fitness, average_position])

    return fitness


def init():

    cpu_cores = 4
    cr_range = [0, 1]
    f_range = [0, 2]
    increment_step = 0.05
    repetitions = 10
    generation_size = 10
    dimensions = 2
    iterations = 50
    b_lower = -5
    b_upper = 5

    worker_tasks = []
    for core in range(cpu_cores):
        worker_tasks.append([
            [
                (core / cpu_cores) * (cr_range[1] - cr_range[0]),
                ((core + 1) / cpu_cores) * (cr_range[1] - cr_range[0]),
            ],
            [
                (core / cpu_cores) * (f_range[1] - f_range[0]),
                ((core + 1) / cpu_cores) * (f_range[1] - f_range[0]),
            ],
            increment_step,
            repetitions,
            generation_size,
            dimensions,
            iterations,
            b_lower,
            b_upper
        ])

    workers = Pool(cpu_cores)
    worker_results = workers.map(run, worker_tasks)

    results = []
    for core in worker_results:
        for result in core:
            results.append(result)

    best_position = results[0]
    for r in results:
        if r[2] < best_position[2]:
            best_position = r

    print(best_position)

    with open('results.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar=';', quoting=csv.QUOTE_MINIMAL)
        for line in range(len(results)):
            writer.writerow(results[line][:3])

if __name__ == '__main__':
    init()
