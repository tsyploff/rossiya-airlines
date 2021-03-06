import numpy as np 
import pandas as pd 
from time import time
from russiya_airlines_import import read_ideal_values, read_delta
from russiya_airlines_interface import solver_setting, weights_setting

def obfective_function(weights, ideal, real):
    '''Возвращает значение целевой функции MAPE'''
    return np.sum((1 - (real + 1)/(ideal + 1))**2, axis=1).dot(weights)
    
def weighted_mean_square(weights, ideal, real):
    '''Возвращает значение целевой функции MSE'''
    return np.sum((real - ideal)**2, axis=1).dot(weights)

def algorithm_A1(delta, weights, ideal):
    '''Ищет распределение связок по книгам с перебором по всем оставшимся парам (k, f)'''
    duration = time() #время начала
    M, N, K = delta.shape #размерность задачи
    real = np.zeros((N, K)) #начальные значения игреков
    undist = np.arange(M) #индексы нераспределённых связок
    dist = [[] for k in range(K)] #распределение связок по книгам

    print('Алгоритм сделает {} итераций.\n'.format(M))
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
                  '\nТекущее значение целевой функции:\t{:.2f}'.format(obfective_function(weights, ideal, real)),
                  '\nПрошло времени:\t{:.2f} сек'.format(time() - duration))
            
    print('\nВремя работы функции:\t{:.4f} сек'.format(time() - duration))
    return obfective_function(weights, ideal, real), dist

def algorithm_A2(unsorted_delta, weights, ideal, sort_function='None'):
    '''Ищет распределение связок по книгам с перебором по всем k'''

    if type(sort_function) == str:
        undist, delta = np.arange(unsorted_delta.shape[0] + 1), unsorted_delta
    else:
        undist, delta = sort_function(unsorted_delta, ideal)
    
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
    return obfective_function(weights, ideal, real), dist

def sort_function_1(delta0, ideal0):
    '''Сортировка по коэффициенту Отиаи'''
    ideal = ideal0.reshape(1, -1)
    ideal = ideal[0]
    M, N, K = delta0.shape
    delta = delta0.reshape(M, -1)
    unsorted = pd.DataFrame()
    unsorted['Коэффициент Отиаи'] = delta.dot(ideal) / np.linalg.norm(delta, axis=1) / np.linalg.norm(ideal)
    undist = unsorted.sort_values(by=['Коэффициент Отиаи']).index.values
    delta = delta.reshape(M, N, K)
    delta = delta[undist]
    undist = np.hstack((undist, -np.ones(1, dtype='int64')))
    return undist, delta

def sort_function_2(delta0, ideal0):
    ideal = ideal0.reshape(1, -1)
    ideal = ideal[0]
    M, N, K = delta0.shape
    delta = delta0.reshape(M, -1)
    delta /= np.linalg.norm(delta, axis=1).reshape(-1, 1)
    unsorted = pd.DataFrame()
    unsorted['Нормированное расстояние'] = np.linalg.norm(delta - ideal/np.linalg.norm(ideal), axis=1)
    undist = unsorted.sort_values(by=['Нормированное расстояние']).index.values
    delta = delta.reshape(M, N, K)
    delta = delta[undist]
    undist = np.hstack((undist, -np.ones(1, dtype='int64')))
    return undist, delta

def to_expert_format(data, solution):
    '''Приводит решение к формату Expert.xls'''
    result = pd.DataFrame(columns=['Связка', 'Вылет', 'Тип'] + [str(day) for day in data['День месяца'].unique()])
    result.loc[0] = np.array([np.NaN, np.NaN, 'ВС', 'СБ ', 'ВС ', 
                              'ПН ', 'ВТ ', 'СР ', 'ЧТ ', 'ПТ ', 
                              'СБ ', 'ВС ', 'ПН ', 'ВТ ', 'СР ', 
                              'ЧТ ', 'ПТ ', 'СБ ', 'ВС ', 'ПН ', 
                              'ВТ ', 'СР ', 'ЧТ ', 'ПТ ', 'СБ ', 
                              'ВС ', 'ПН ', 'ВТ ', 'СР ', 'ЧТ ', 
                              'ПТ ', 'СБ ', 'ВС ', 'ПН '])
    
    table = data[['День месяца', 'Время вылета', 'Связка', 'Тип судна']].copy()
    table['Рабочий стол'] = np.zeros(len(table), dtype='int64')
    for book in range(len(solution)):
        for i in solution[book]:
            table.loc[i, 'Рабочий стол'] = book
    
    indexes = table.groupby(by=['Время вылета', 'Связка', 'Тип судна']).count().index
    
    for i in range(len(indexes)):
        result.loc[i + 1, 'Связка'] = indexes[i][1]
        result.loc[i + 1, 'Вылет'] = indexes[i][0]
        result.loc[i + 1, 'Тип'] = indexes[i][2]
        subtable = table[np.all(table[['Время вылета', 'Связка', 'Тип судна']] == indexes[i], axis=1)]
        for row in range(len(subtable)):
            result.loc[i + 1, str(subtable.iloc[row]['День месяца'])] = subtable.iloc[row]['Рабочий стол']

    return result


class Solver():

    count = 0

    solutions = {}

    formated_solutions = {}
    
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
        self.data = data
        self.crew = crew
        self.R = data['Назначение'].unique().shape[0]
        self.L = data['Тип судна'].unique().shape[0]
        self.T = data['День месяца'].unique().shape[0]

    def solve(self, weights=np.ones(94)/94):
        self.algorithm, self.sort = solver_setting()
        weights = weights_setting(self.T, self.L, self.R)
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
            Solver.formated_solutions[Solver.count] = to_expert_format(self.data, Solver.solutions[Solver.count][1])
        else:
            Solver.solutions[Solver.count] = algorithm_A2(self.delta, weights, self.ideal, sort_function=Solver.sorts[self.sort])
            Solver.specifications[Solver.count] = {
                'Веса критериев' : weights, 
                'Алгоритм' : 'A2', 
                'Сортировка' : Solver.sorts[self.sort], 
                'Время работы (сек)' : time() - duration
            }
            Solver.formated_solutions[Solver.count] = to_expert_format(self.data, Solver.solutions[Solver.count][1])
        return '''\nРешение записано в Solver.solutions;
Решение приведённое к формату Expert.xls записано в Solver.formated_solutions;
Спецификации решения сохранены в Solver.specifications;
Идентификатор решения: {}'''.format(Solver.count)