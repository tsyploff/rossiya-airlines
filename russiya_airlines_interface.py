import pandas as pd

from tkinter import *
from tkinter import filedialog as fd

def get_data():
    global data
    filename = fd.askopenfilename()
    data = pd.read_excel(filename)
    
def get_crew():
    global crew
    filename = fd.askopenfilename()
    crew = pd.read_json(filename)

def solver_setting(a='A1', s='S1'):
    root = Tk()
    root.title('Настройки алгоритма')
    root.geometry('300x150')
    
    algorithm_label = Label(root, text='Выберите алгоритм: ')
    algorithm_label.pack()
    
    algorithm = StringVar(root)
    algorithm.set(a) 
    
    algorithm_option = OptionMenu(root, algorithm, 'A1', 'A2')
    algorithm_option.pack()
    
    sort_label = Label(root, text='Выберите сортировку: ')
    sort_label.pack()
    
    sort = StringVar(root)
    sort.set(s) 
    
    sort_option = OptionMenu(root, sort, 'S1', 'S2')
    sort_option.pack()
    
    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.pack()
    
    mainloop()
    
    return algorithm.get(), sort.get()

def data_setting():
    root = Tk()
    
    data_label = Label(root, text='Выберите файл с исходными данными о связках: ')
    data_label.pack()

    data_button = Button(root, text='Открыть', command=get_data)
    data_button.pack()
    
    crew_label = Label(root, text='Выберите файл с исходными данными о книгах: ')
    crew_label.pack()

    crew_button = Button(root, text='Открыть', command=get_crew)
    crew_button.pack()
    
    exit_button = Button(root, text='Готово', command=root.destroy)
    exit_button.pack()
    
    mainloop()

    return data, crew