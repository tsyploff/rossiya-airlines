import os

import numpy as np 
import pandas as pd 

def is_night_flight(flight):
	'''Определяет, является полёт ночным.
	Работает от строк файла ID.xls загруженного в pandas.DataFrame
	>>> flight = data.iloc[0]
	>>> print(type(flight))
	<class 'pandas.core.series.Series'>
	'''
	pass

def table_round_trip(solution):
	'''Принимает на вход решение в виде pd.DataFrame, 
	возвращает табличку "распределение связок по группам"
	в виде pd.DataFrame
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	'''
	pass

def table_flight_time(solution):
	'''Принимает на вход решение в виде pd.DataFrame, 
	возвращает табличку "планируемое время налёта"
	в виде pd.DataFrame
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	'''
	pass

def table_flight_on_direction(solution):
	'''Принимает на вход решение в виде pd.DataFrame, 
	возвращает табличку "количество связок по направлениям"
	в виде pd.DataFrame
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	'''
	pass

def table_flight_on_date(solution):
	'''Принимает на вход решение в виде pd.DataFrame, 
	возвращает табличку "число вылетов по датам"
	в виде pd.DataFrame
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	'''
	pass

def table_flight_on_plane(solution):
	'''Принимает на вход решение в виде pd.DataFrame, 
	возвращает табличку "количество связок по типу воздушного судна"
	в виде pd.DataFrame
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	'''
	pass

def table_compare_solutions(solutions, specifications):
	'''Принимает на вход словарь решений и словарь спецификаций,
	возвращает табличку "сравнение решений"
	в виде pd.DataFrame
	>>> solution = solutions[id]
	>>> print(type(solution))
	<class 'pandas.core.frame.DataFrame'>
	>>> specifications[id]
	{'Веса критериев' : [...], 'Алгоритм' : 'A1', 'Сортировка' : 'sort_function', 'Время работы (сек)' : 3.12}
	'''
	pass

def export_tables(title, tables):
	'''Принимает на вход словарь таблиц
	>>> tables
	{'Название таблицы 1' : table1, 'Название таблицы 2' : table2, ...}

	Экспортирует таблицы в эксель, каждую на свой лист, 
	каждый лист именуется названием таблицы'''
	pass

def solution_report(solution, specification):
	'''Принимает на вход решение в виде pd.DataFrame, 
	строит все таблицы и экспортирует их в эксель с названием 
	
	"Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])

	Если такой файл уже существует, в конце добавляется (1). Если уже существует файл с названием 
	"Решение ({}, {}, {}) (k).xlsx".format(...)

	в конце добавляется (k + 1)

	'''
	sheets = {'Распределение связок по группам' : table_round_trip(solution), ...}
	pass
