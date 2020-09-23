import numpy as np 
import pandas as pd

from tkinter import *
from tkinter import filedialog as fd

def get_data():
    global data, data_file
    filename = fd.askopenfilename()
    data = pd.read_excel(filename)
    data_file.config(text = filename)
    
def get_crew():
    global crew, crew_file
    filename = fd.askopenfilename()
    crew = pd.read_json(filename)
    crew_file.config(text = filename)

def solver_setting():
    root = Tk()
    root.title('Настройки алгоритма')
    root.geometry('300x150')
    
    algorithm_label = Label(root, text='Выберите алгоритм: ')
    algorithm_label.pack()
    
    algorithm = StringVar(root)
    algorithm.set('A1') 
    
    algorithm_option = OptionMenu(root, algorithm, 'A1', 'A2')
    algorithm_option.pack()
    
    sort_label = Label(root, text='Выберите сортировку: ')
    sort_label.pack()
    
    sort = StringVar(root)
    sort.set('S1') 
    
    sort_option = OptionMenu(root, sort, 'S1', 'S2')
    sort_option.pack()
    
    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.pack()
    
    mainloop()
    
    return algorithm.get(), sort.get()

def weights_setting(T, L, R):
    root = Tk()
    root.title('Настройки весов')
    root.geometry('300x210')

    title = Label(root, text='Введите веса критериев\nВеса автоматически нормируются')
    title.grid(row=0, column=0)

    var_1 = DoubleVar(); var_1.set(1.0)
    var_2 = DoubleVar(); var_2.set(1.0)
    var_3 = DoubleVar(); var_3.set(1.0)
    var_4 = DoubleVar(); var_4.set(1.0)
    var_5 = DoubleVar(); var_5.set(1.0)
    var_6 = DoubleVar(); var_6.set(1.0)
    var_7 = DoubleVar(); var_7.set(1.0)

    Label(root, text='Введите вес 1-го критерия: ').grid(row=1, column=0)
    crt_1 = Entry(text=var_1, width=10); crt_1.grid(row=1, column=1)

    Label(root, text='Введите вес 2-го критерия: ').grid(row=2, column=0)
    crt_2 = Entry(text=var_2, width=10); crt_2.grid(row=2, column=1)

    Label(root, text='Введите вес 3-го критерия: ').grid(row=3, column=0)
    crt_3 = Entry(text=var_3, width=10); crt_3.grid(row=3, column=1)

    Label(root, text='Введите вес 4-го критерия: ').grid(row=4, column=0)
    crt_4 = Entry(text=var_4, width=10); crt_4.grid(row=4, column=1)

    Label(root, text='Введите вес 5-го критерия: ').grid(row=5, column=0)
    crt_5 = Entry(text=var_5, width=10); crt_5.grid(row=5, column=1)

    Label(root, text='Введите вес 6-го критерия: ').grid(row=6, column=0)
    crt_6 = Entry(text=var_6, width=10); crt_6.grid(row=6, column=1)

    Label(root, text='Введите вес 7-го критерия: ').grid(row=7, column=0)
    crt_7 = Entry(text=var_7, width=10); crt_7.grid(row=7, column=1)

    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.grid(row=8, column=1)

    mainloop()
    
    weights = np.hstack((
            np.ones(3)*var_1.get(),
            np.ones(3)*var_2.get(),
            np.ones(1)*var_3.get(),
            np.ones(3)*var_4.get(),
            np.ones(T)*var_5.get(),
            np.ones(L)*var_6.get(),
            np.ones(R)*var_7.get(),
    ))

    return weights / np.sum(weights)


def data_setting():
    global data, crew, data_file, crew_file
    root = Tk()
    
    data_label = Label(root, text='Выберите файл с исходными данными о связках: ')
    data_label.pack()

    data_button = Button(root, text='Открыть', command=get_data)
    data_button.pack()

    data_file = Label(root, text='')
    data_file.pack()
    
    crew_label = Label(root, text='Выберите файл с исходными данными о книгах: ')
    crew_label.pack()

    crew_button = Button(root, text='Открыть', command=get_crew)
    crew_button.pack()

    crew_file = Label(root, text='')
    crew_file.pack()
    
    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.pack()
    
    mainloop()

    return data, crew

def solution_import():
    global data, data_file
    root = Tk()
    
    data_label = Label(root, text='Выберите файл с примером решения: ')
    data_label.pack()

    data_button = Button(root, text='Открыть', command=get_data)
    data_button.pack()

    data_file = Label(root, text='')
    data_file.pack()
       
    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.pack()
    
    mainloop()

    return data.iloc[1:] #Так надо делать с нашими данными из-за французской нумерации