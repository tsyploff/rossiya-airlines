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