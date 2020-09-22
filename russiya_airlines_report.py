import os

import numpy as np 
import pandas as pd 

def total_time(start, duration): #сложение часов
    st = list(map(lambda x: int(x), start.split(':')))
    dur = list(map(lambda x: int(x), duration.split(':')))
    a = [st[0] + dur[0],st[1] + dur[1]]
    if a[1]>= 60:
        a[0] += 1
        a[1] -= 60
    if a[0] < 10:
        h = '0'+ str(a[0])
    else:
        h = str(a[0])
    if a[1] < 10:
        m = '0'+ str(a[1])
    else:
        m = str(a[1])
    return h + ':' + m

def sum_time(start, duration): #сложение часов с обнулением
    st = list(map(lambda x: int(x), start.split(':')))
    dur = list(map(lambda x: int(x), duration.split(':')))
    a = [st[0] + dur[0],st[1] + dur[1]]
    if a[1]>= 60:
        a[0] += 1
        a[1] -= 60
    if a[0]>=24:
        a[0] -= 24
    return str(a[0])+':'+str(a[1])

def in_minuts(duration):
    dur  = np.array(list(map(lambda x: int(x), duration.split(':'))))
    return dur[0]*60 + dur[1]

def in_hours(minuts):
    h = int(minuts // 60)
    m = int(minuts % 60)
    if h < 10:
        h = '0'+ str(h)
    else:
        h = str(h)
    if m < 10:
        m = '0'+ str(m)
    else:
        m = str(m)
    return h + ':' + m

def find_night_minuts(fligt_time):  # Количество ночных минут полёта
    night_h1 = list(map(lambda x: in_minuts(x), ['00:00','06:00']))
    night_h2 = list(map(lambda x: in_minuts(x), ['22:00','23:59']))
    f = list(map(lambda x: in_minuts(x), fligt_time))
    delta = 0

    if f[0] < night_h1[1]:
        if f[1] < night_h1[1]: # весь полёт попал в первую половину ночи
            delta += f[1] - f[0] # Длительность полёта в минутах
        else:
            delta += 6*60 - f[0] 
    elif f[0] > night_h1[1] and f[0] < night_h2[0]:
        if f[1] > night_h1[1] and f[1] < night_h2[0]:
            if f[0] < f[1]:
                delta += 0  #дневное время
            else:
                delta += night_h1[1] + night_h2[1] - night_h2[0] + 1#очень длинный перелёт

        elif f[1] > night_h2[0] and f[1] < night_h2[1]:
            delta += f[1] - night_h2[0] #часть полёта в вечернее время

        elif f[1] > night_h1[0] and f[1] < night_h1[1]:
            delta += f[1] + night_h2[1] - night_h2[0] + 1

    elif f[0] > night_h2[0]:
        if f[1] > night_h2[0] and f[1] < night_h2[1]:
            delta += f[1]-f[0]
        elif f[1] < night_h1[1]: 
            delta += night_h2[1] - f[0] + f[1] + 1
        elif f[1] > night_h1[1] and f[1] < night_h2[0]:
            delta += night_h2[1] - f[0] + night_h1[1] + 1

    return delta 

def night_percent(start, duration): # start и duration 'hh:mm'   - % от полёта, проходящий в ночное время
    d0 = in_minuts(duration)
    d = in_hours(d0/2)
    t = sum_time(start, d)
    h1 = [start, t]
    t = sum_time(t, '01:30')
    h2 = [t, sum_time(t,d)]
    return (find_night_minuts(h1) + find_night_minuts(h2))/d0

def is_night_flight(flight): # Является ли связка ночной
    start = flight['Время вылета'].iloc[0]
    duration = flight['Налет'].iloc[0]
    n_pc = night_percent(start, duration)
    if n_pc > 0.5:
        return True
    else:
        return False


def table_round_trip(solution):
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
            group = solution.iloc[j][i]
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
def table_flight_time(solution):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "планируемое время налёта"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    a = np.array(['000:000']*6*6).reshape([6,6])

    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][i]
            if group == 0:
                i += 1
            else:
                d = t[t['День месяца']==i]
                rout_type = d['Тип связи'].iloc[0]
                dur = d['Налет'].iloc[0]
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
    delta = []
    for i in h:
        delta += [in_hours(in_minuts(max(h[i])) - in_minuts(min(h[i])))]
    h.loc['delta'] = delta
    return h
def table_flight_on_direction(solution):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "количество связок по направлениям"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    ans = pd.DataFrame(np.zeros([len(destin),8]), index = destin, columns=['1','2','3','4','5','6','All', 'delta'])
    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][i]
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

def table_flight_on_date(solution):
    '''Принимает на вход решение в виде pd.DataFrame, 
    возвращает табличку "число вылетов по датам"
    в виде pd.DataFrame
    >>> print(type(solution))
    <class 'pandas.core.frame.DataFrame'>
    '''
    ans = pd.DataFrame(np.zeros([len(solution.iloc[0])-3,8]), index = range(1,len(solution.iloc[0])-2), columns=['1','2','3','4','5','6','All', 'delta'])
    for j in range(len(solution)):
        rout = solution.iloc[j].iloc[0]
        start = solution.iloc[j].iloc[1]
        t = data[data['Связка']==rout]
        t = t[t['Время вылета']==start]
        for i in t['День месяца'].values:
            group = solution.iloc[j][i]
            if group == 0:
                i += 1
            else:
                ans.loc[i][str(group)] += 1
    ans['All'] = ans['1'] + ans['2'] + ans['3'] + ans['4'] + ans['5']+ ans['6']

    delta = []
    for i in range(1,len(solution.iloc[0])-2):
        s = ans.loc[i]
        delta += [max(s['1'],s['2'],s['3'],s['4'],s['5'],s['6']) - min(s['1'],s['2'],s['3'],s['4'],s['5'],s['6'])]
    ans['delta'] = delta

    return(ans)

def table_flight_on_plane(solution):
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
            group = solution.iloc[j][i]
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

def solution_report(solution, specification):
    '''Принимает на вход решение в виде pd.DataFrame, 
    строит все таблицы и экспортирует их в эксель с названием 
    
    "Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])

    Если такой файл уже существует, в конце добавляется (1). Если уже существует файл с названием 
    "Решение ({}, {}, {}) (k).xlsx".format(...)

    в конце добавляется (k + 1)
    file_name = ["Решение ({}, {}, {}).xlsx".format(specification['Алгоритм'], specification['Сортировка'], specification['Веса критериев'])]''' t1 = table_round_trip(solution)
    t1.to_excel(file_name, sheet = 'Таблица 1')
    t2 = table_flight_time(solution)
    t2.to_excel(file_name, sheet = 'Таблица 2')
    t3 = table_flight_on_direction(solution)
    t3.to_excel(file_name, sheet = 'Таблица 3')
    t4 = table_flight_on_date(solution)
    t4.to_excel(file_name, sheet = 'Таблица 4')
    t5 = table_flight_on_plane(solution)
    t5.to_excel(file_name, sheet = 'Таблица 5')
