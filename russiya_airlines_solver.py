import numpy as np 
import pandas as pd 
from time import time

def obfective_function(weights, ideal, real):
    '''Возвращает значение целевой функции'''
    if np.any(np.sign(ideal) <= 0): #защита от деления на нуль
        sigma = real / (ideal + 10**(-8))
        return np.sum((1 - sigma)**2, axis=1).dot(weights)
    else:
        return np.sum((1 - real/ideal)**2, axis=1).dot(weights)

def algorithm_A1(delta, weights, ideal):
    '''Ищет распределение связок по книгам с перебором по всем оставшимся парам (k, f)'''
    duration = time() #время начало
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

def algorithm_A2(delta, weights, ideal):
    '''Ищет распределение связок по книгам с перебором по всем оставшимся парам (k, f)'''
    duration = time() #время начало
    M, N, K = delta.shape #размерность задачи
    real = np.zeros((N, K)) #начальные значения игреков
    f = 0
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
        f += 1
            
    print('Время работы функции:\t{:.4f} сек'.format(time() - duration))
    return best_value, dist