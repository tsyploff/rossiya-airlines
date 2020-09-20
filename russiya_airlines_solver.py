import numpy as np 
import pandas as pd 
from time import time
from russiya_airlines_import import read_ideal_values, read_delta
from russiya_airlines_interface import solver_setting

def obfective_function(weights, ideal, real):
    '''Возвращает значение целевой функции'''
    return np.sum((1 - real/(ideal + 10**(-8)))**2, axis=1).dot(weights)

def algorithm_A1(delta, weights, ideal):
    '''Ищет распределение связок по книгам с перебором по всем оставшимся парам (k, f)'''
    duration = time() #время начала
    M, N, K = delta.shape #размерность задачи
    real = np.zeros((N, K)) #начальные значения игреков
    undist = np.arange(M) #индексы нераспределённых связок
    dist = [[] for k in range(K)] #распределение связок по книгам

    for step in range(1, M + 1):
        print('_', end='') #линия загрузки

        best_f, best_k = undist[0], 0 
        zero = np.zeros((N, K))
        zero[:, best_k] = delta[best_f, :, best_k]
        best_real = real + zero
        best_value = obfective_function(weights, ideal, best_real)
    
        for k in range(K):
            for f in undist:
                zero = np.zeros((N, K))
                zero[:, k] = delta[f, :, k]
                try_real = real + zero
                try_value = obfective_function(weights, ideal, try_real)
                if try_value <= best_value:
                    best_f, best_k = f, k
                    best_real = try_real
                    best_value = try_value
                    
        dist[best_k].append(best_f)
        undist = undist[undist != best_f]
        real = best_real

        if step % 100 == 0:
            print('\nШаг #{}'.format(step), 
                  '\nТекущее значение целевой функции:\t{:.2f}'.format(best_value),
                  '\nПрошло времени:\t{:.2f} сек'.format(time() - duration))
            
    print('\nВремя работы функции:\t{:.4f} сек'.format(time() - duration))
    return dist

def algorithm_A2(unsorted_delta, weights, ideal, sort_function=np.nan):
    '''Ищет распределение связок по книгам с перебором по всем k'''

    if np.isnan(sort_function):
        undist, delta = np.arange(unsorted_delta.shape[0] + 1), unsorted_delta
    else:
        undist, delta = sort_function(unsorted_delta)
    
    duration = time() #время начала
    M, N, K = delta.shape #размерность задачи
    real = np.zeros((N, K)) #начальные значения игреков
    f = undist[0]
    dist = [[] for k in range(K)] #распределение связок по книгам

    for step in range(1, M + 1):
        best_k = 0 
        zero = np.zeros((N, K))
        zero[:, best_k] = delta[f, :, best_k]
        best_real = real + zero
        best_value = obfective_function(weights, ideal, best_real)
    
        for k in range(K):
            zero = np.zeros((N, K))
            zero[:, k] = delta[f, :, k]
            try_real = real + zero
            try_value = obfective_function(weights, ideal, try_real)
            if try_value <= best_value:
                best_k = k
                best_real = try_real
                best_value = try_value
                    
        dist[best_k].append(f)
        real = best_real
        undist = undist[1:]
        f = undist[0]
            
    print('Время работы функции:\t{:.4f} сек'.format(time() - duration))
    return best_value, dist

def sort_function_1(delta):
    return delta

def sort_function_2(delta):
    return delta


class Solver():

    count = 0

    solutions = {}
    
    specifications = {}
    
    algorithms = {'A1' : algorithm_A1, 'A2' : algorithm_A2}

    sorts = {'S1' : sort_function_1, 'S2' : sort_function_2}

    def __init__(self, data, crew, delta='None', ideal='None'):
        if type(delta) == str:
            self.delta = read_delta(data, crew)
        else:
            self.delta = delta

        if type(ideal) == str:
            self.ideal = read_ideal_values(data, crew)
        else:
            self.ideal = ideal
        self.algorithm = 'A1'
        self.sort = 'S1'

    def solve(self, weights=np.ones(94)/94):
        self.algorithm, self.sort = solver_setting(self.algorithm, self.sort)
        Solver.count += 1
        duration = time()
        if self.algorithm == 'A1':
            Solver.solutions[Solver.count] = algorithm_A1(self.delta, weights, self.ideal)
            Solver.specifications[Solver.count] = {
                'Веса критериев' : weights, 
                'Алгоритм' : 'A1', 
                'Сортировка' : Solver.sorts[self.sort], 
                'Время работы (сек)' : time() - duration
            }
        else:
            Solver.solutions[Solver.count] = algorithm_A2(self.delta, weights, self.ideal)
            Solver.specifications[Solver.count] = {
                'Веса критериев' : weights, 
                'Алгоритм' : 'A2', 
                'Сортировка' : Solver.sorts[self.sort], 
                'Время работы (сек)' : time() - duration
            }
        return '''\nРешение записано в Solver.solutions;
Спецификации решения сохранены в Solver.specifications;
Идентификатор решения: {}'''.format(Solver.count)