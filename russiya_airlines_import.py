import os

import numpy as np 
import pandas as pd 

def read_ideal_values(data, crew):
    '''На вход принимает информацию о связках и книгах, 
    возвращает матрицу np.array идеальных значений 
    >>> ideals = read_ideal_values(data, crew)
    >>> ideals[j, k] #сначала номер критерия, затем номер книги
    >>> print(type(ideals))
    <class 'numpy.ndarray'>
    '''
    pass

def read_delta(data, crew): 
    '''На вход принимает информацию о связках и книгах, 
    возвращает тензор дельта большое 
    >>> delta = read_ideal_values(data, crew)
    >>> delta[f, j, k] #сначала номер связки, затем номер критерия, затем номер книги
    >>> print(type(ideals))
    <class 'numpy.ndarray'>
    '''
    pass