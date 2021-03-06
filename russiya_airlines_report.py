import os

import numpy as np
import pandas as pd
from air_modules import*
## Глобальная переменная
numberOfCrue=pd.DataFrame({'group': [1,2,3,4,5,6],
                           'ВВЛ': [125.54, 122.84, 129.97, 127.26, 123.32, 130.64],
                          'МВЛ': [119.88, 117.30, 124.10, 121.51, 117.76, 124.75],
                           'СНГ': [122.03, 119.41, 126.33, 123.69, 119.87, 126.99]})

def table_round_trip(solution, data):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "распределение связок по группам"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    a = np.zeros([6,8])

    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][str(i)]
            if group == 0:
                i += 1
            else:
                d = t[t['День месяца']==i]
                rout_type = d['Тип связи'].iloc[0]
                if rout_type == 'ВВЛ':
                    a[group-1, 0] += d['Экипаж'].iloc[0]
                    a[group-1, 1] += 1
                elif rout_type == 'МВЛ':
                    a[group-1, 2] += d['Экипаж'].iloc[0]
                    a[group-1, 3] += 1
                else:
                #СНГ
                    a[group-1, 4] += d['Экипаж'].iloc[0]
                    a[group-1, 5] += 1

                a[group-1, 6] += 1
                if is_night_flight(d):
                    a[group-1, 7] += 1
    return pd.DataFrame(a, columns=['ВВЛ: БП','ВВЛ: Связки','МВЛ: БП','МВЛ: СВ','СНГ: БП','СНГ: Связки','Всего связок','Всего носных связок'])

def table_flight_time(solution, data, crew=numberOfCrue):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "планируемое время налёта"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    a = np.array(['000:000']*6*6).reshape([6,6])
    types = list(set(data['Тип связи']))

    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][str(i)]
            if group == 0:
                i += 1
            else:
                d = t[t['День месяца']==i]
                rout_type = d['Тип связи'].iloc[0]
                dur = in_hours(in_minuts(d['Налет'].iloc[0])*int(d['Экипаж'].iloc[0]))
                flight_time = total_time(start, dur)
                per = in_hours(in_minuts(dur)*night_percent(start,dur))
                if rout_type == 'ВВЛ':
                    a[group-1, 0] = total_time(a[group-1, 0],dur)
                    a[group-1, 1] = total_time(a[group-1, 1],per)
                elif rout_type == 'МВЛ':
                    a[group-1, 2] = total_time(a[group-1, 2],dur)
                    a[group-1, 3] = total_time(a[group-1, 3],per)
                else:
                #СНГ
                    a[group-1, 4] = total_time(a[group-1, 4],dur)
                    a[group-1, 5] = total_time(a[group-1, 5],per)
    h = pd.DataFrame(a, columns=['ВВЛ: Планируемый налёт','ВВЛ: Планируемый ночной налёт','МВЛ: Планируемый налёт','МВЛ: Планируемый ночной налёт','СНГ: Планируемый налёт','СНГ: Планируемый ночной налёт'], index = range(1,7))
    
    for i in h.columns:
        type_r = i[:3]
        for j in range(1,7):
            ideal_time = str(crew[crew['group']==j][type_r].iloc[0]).split('.')
            ideal_time = ideal_time[0]+':'+ideal_time[1]
            h[i].loc[j] = in_minuts(h[i].loc[j])/in_minuts(ideal_time)
    
    delta = []
    for i in h:
        delta += [max(h[i]) - min(h[i])]
    h.loc['delta'] = delta
    return h


def table_flight_on_direction(solution, data):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "количество связок по направлениям"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    destin = set(data['Назначение'])
    ans = pd.DataFrame(np.zeros([len(destin),8]), index = destin, columns=['1','2','3','4','5','6','All', 'delta'])
    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][str(i)]
            if group == 0:
                i += 1
            else:
                d = t[t['День месяца']==i]
                des = d['Назначение'].iloc[0]
                ans.loc[des][str(group)] += 1
    ans['All'] = ans['1'] + ans['2'] + ans['3'] + ans['4'] + ans['5']+ ans['6']

    delta = []
    for i in destin:
        s = ans.loc[i]
        delta += [max(s['1'],s['2'],s['3'],s['4'],s['5'],s['6']) - min(s['1'],s['2'],s['3'],s['4'],s['5'],s['6'])]
    ans['delta'] = delta

    return(ans)

def table_flight_on_date(solution, data):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "число вылетов по датам"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    ans = pd.DataFrame(np.zeros([len(solution.iloc[0])-2,8]), index = range(1,len(solution.iloc[0])-1), columns=['1','2','3','4','5','6','All', 'delta'])
    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][str(i)]
            if group == 0:
                i += 1
            else:
                ans.loc[i][str(group)] += 1
    ans['All'] = ans['1'] + ans['2'] + ans['3'] + ans['4'] + ans['5']+ ans['6']

    delta = []
    for i in range(1,len(solution.iloc[0])-1):
        s = ans.loc[i]
        delta += [max(s['1'],s['2'],s['3'],s['4'],s['5'],s['6']) - min(s['1'],s['2'],s['3'],s['4'],s['5'],s['6'])]
    ans['delta'] = delta

    return(ans)

def table_flight_on_plane(solution, data):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "количество связок по типу воздушного судна"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    ans = pd.DataFrame(np.zeros([2,8]), index =['А-319', 'А-320'], columns=['1','2','3','4','5','6','All', 'delta'])
    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][str(i)]
            if group == 0:
                i += 1
            else:
                d = t[t['День месяца']==i]
                board_type = d['Тип судна'].iloc[0][:5]
                ans.loc[board_type][str(group)] += 1
    ans['All'] = ans['1'] + ans['2'] + ans['3'] + ans['4'] + ans['5']+ ans['6']

    delta = []
    for i in ['А-319', 'А-320']:
        s = ans.loc[i]
        delta += [max(s['1'],s['2'],s['3'],s['4'],s['5'],s['6']) - min(s['1'],s['2'],s['3'],s['4'],s['5'],s['6'])]
    ans['delta'] = delta

    return(ans)

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

def solution_report(solution, data):
    '''Принимает на вход решение в виде pd.DataFrame, 
    строит все таблицы и экспортирует их в эксель с названием 
    
    "Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])

    Если такой файл уже существует, в конце добавляется (1). Если уже существует файл с названием 
    "Решение ({}, {}, {}) (k).xlsx".format(...)

    в конце добавляется (k + 1)
    file_name = ["Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])]'''
    #file_name = ["Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])]
    t1 = table_round_trip(solution, data)
    
    t2 = table_flight_time(solution, data)
    
    t3 = table_flight_on_direction(solution, data)
    
    t4 = table_flight_on_date(solution, data)
    
    t5 = table_flight_on_plane(solution, data)
    
    with pd.ExcelWriter(file_name + '.xlsx') as writer: 
        t1.to_excel(writer, sheet_name = 'Таблица 1')
        t2.to_excel(writer, sheet_name = 'Таблица 2')
        t3.to_excel(writer, sheet_name = 'Таблица 3')
        t4.to_excel(writer, sheet_name = 'Таблица 4')
        t5.to_excel(writer, sheet_name = 'Таблица 5')