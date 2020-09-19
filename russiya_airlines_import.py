import air_modules as am
import numpy as np
import pandas as pd
import itertools
from sklearn.preprocessing import OneHotEncoder

def preprocess(data):
    
    data['night'] = np.array([am.is_night_flight(data.iloc[i]) * 1 for i in range(data.shape[0])])
    data_columns = ['Налет', 'Экипаж', 'Тип связи', 'День месяца', 'Тип судна', 'Назначение', 'Время вылета', 'night']
    
    F_columns = ['t', 'p', 'v', 'd', 'a', 's', 'goodbye', 'night']
    F = pd.DataFrame(columns=F_columns, index=data['Связка'])
    F[F_columns] = data[data_columns].values
    
    F['t'] = pd.to_datetime(F['t']).dt.minute / 60 + pd.to_datetime(F['t']).dt.hour
    F['goodbye'] = pd.to_datetime(F['goodbye']).dt.minute / 60 + pd.to_datetime(F['goodbye']).dt.hour
    F[['p', 'd', 'night']] = F[['p', 'd', 'night']].astype(int)
    
    v_mapping = {'ВВЛ': 1, 'МВЛ': 2, 'СНГ': 3}
    a_mapping = {'А-319': 1, 'А-320': 2}
    
    F['a'] = F['a'].apply(lambda x: x.strip())
    F['a'] = F['a'].map(a_mapping)
    F['v'] = F['v'].map(v_mapping)
    F['s'] = F['s'].apply(lambda x: int(x.split()[1]))
    
    return F

def fit_transform(F, ser, K):
        ft_OH = OneHotEncoder().fit_transform(F[ser].values.reshape(-1,1)).toarray()
        res = np.tile(ft_OH.reshape(-1,1), K).reshape(F.shape[0], len(pd.unique(F[ser])) , K)
        return res

def read_ideal_values(data=pd.read_excel('ID.xls'), crew=pd.read_json('crew.json')):
    '''На вход принимает информацию о связках и книгах,
    возвращает матрицу np.array идеальных значений
    >>> ideals = read_ideal_values(data, crew)
    >>> ideals[j, k] #сначала номер критерия, затем номер книги
    >>> print(type(ideals))
    <class 'numpy.ndarray'>
    '''

    F = preprocess(data) #data
    
    M = F.shape[0] # количество связок
    K = len(crew.columns) # количество групп
    L = sorted(pd.unique(F['a'])) # множество связок с типом воздушного судна
    R = sorted(pd.unique(F['s'])) # множество направлений
    T = sorted(pd.unique(F['d'])) # множество дней горизонта планирования
    U = sorted(pd.unique(F['v'])) # тип сообщения
    N = 10 + len(T) + len(L) + len(R) # размерность вектора
    
    j = np.arange(len(U)) + 1
    k = np.arange(K) + 1
    t = np.arange(len(T)) + 1
    l = np.arange(len(L)) + 1
    s = np.arange(len(R)) + 1
    
    all_permutations_j_k = list(itertools.product(j, k))
    all_permutations_t_k = list(itertools.product(t, k))
    all_permutations_l_k = list(itertools.product(l, k))
    all_permutations_s_k = list(itertools.product(s, k))
    
    # 1 критерий
    y1 = np.array([f"y[{j}, {k}]" for j, k in all_permutations_j_k]) 
    y1_ideal = np.array([(F[F['v']==j]['p']*F[F['v']==j]['t']).sum() / crew.iloc[j-1].sum() for j, k in all_permutations_j_k]) 
    c_1 = pd.DataFrame(data=y1_ideal, index=y1, columns=['c_1']) 
    
    # 2 критерий
    y2 = np.array([f"y[{j+3}, {k}]" for j, k in all_permutations_j_k])
    y2_ideal = np.array([(F[(F['v']==j) & (F['night']==1)]['p']*F[(F['v']==j) & (F['night']==1)]['t']).sum() / crew.iloc[j-1].sum() for j, k in all_permutations_j_k])
    c_2 = pd.DataFrame(data=y2_ideal, index=y2, columns=['c_2'])
    
    # 3 критерий
    y3 = np.array([f"y[{7}, {item}]" for item in k])
    y3_ideal = np.array([crew.iloc[0][item]*F[(F['night']==1)].shape[0] / crew.iloc[0].sum() for item in k ])
    c_3 = pd.DataFrame(data=y3_ideal, index=y3, columns=['c_3'])
    
    # 4 критерий
    y4 = np.array([f"y[{7+j}, {k}]" for j, k in all_permutations_j_k])
    y4_ideal = np.array([F[F['v']==j].shape[0]*crew.iloc[j-1][k] / crew.iloc[j-1].sum() for j, k in all_permutations_j_k])
    c_4 = pd.DataFrame(data=y4_ideal, index=y4, columns=['c_4'])
    
    # 5 критерий
    y5 = np.array([f"y[{10+j}, {k}]" for j, k in all_permutations_t_k])
    y5_ideal = np.array([ F[F['d']==t].shape[0] / K for t, k in all_permutations_t_k])
    c_5 = pd.DataFrame(data=y5_ideal, index=y5, columns=['c_5'])
    # 6 критерий
    y6 = np.array([f"y[{10+j+len(T)}, {k}]" for j, k in all_permutations_l_k])
    y6_ideal = np.array([F[F['a']==l].shape[0] / K for l, k in all_permutations_l_k])
    c_6 = pd.DataFrame(data=y6_ideal, index=y6, columns=['c_6'])
    
    # 7 критерий
    y7 = np.array([f"y[{10+j+len(T)+len(L)}, {k}]" for j, k in all_permutations_s_k])
    y7_ideal = np.array([F[F['s']==s].shape[0] / K for s, k in all_permutations_s_k])
    c_7 = pd.DataFrame(data=y7_ideal, index=y7, columns=['c_7'])
    
    # ideal
    ideals = np.concatenate([c_1.values.reshape(-1, K), c_2.values.reshape(-1,K),\
                    c_3.values.reshape(-1,K), c_4.values.reshape(-1,K),\
                    c_5.values.reshape(-1,K), c_6.values.reshape(-1,K),\
                    c_7.values.reshape(-1,K)])
        
    assert N == ideals.shape[0]
    assert type(ideals) == np.ndarray
    
    return ideals

def read_delta(data=pd.read_excel('ID.xls'), crew=pd.read_json('crew.json')): 
    '''На вход принимает информацию о связках и книгах, 
    возвращает тензор дельта большое 
    >>> delta = read_ideal_values(data, crew)
    >>> delta[f, j, k] #сначала номер связки, затем номер критерия, затем номер книги
    >>> print(type(ideals))
    <class 'numpy.ndarray'>
    '''
    
    F = preprocess(data) #data
    
    M = F.shape[0] # количество связок
    K = len(crew.columns) # количество групп
    L = sorted(pd.unique(F['a'])) # множество связок с типом воздушного судна
    R = sorted(pd.unique(F['s'])) # множество направлений
    T = sorted(pd.unique(F['d'])) # множество дней горизонта планирования
    U = sorted(pd.unique(F['v'])) # тип сообщения
    N = 10 + len(T) + len(L) + len(R) # размерность вектора
    
    j = np.arange(len(U)) + 1
    k = np.arange(K) + 1
    t = np.arange(len(T)) + 1
    l = np.arange(len(L)) + 1
    s = np.arange(len(R)) + 1
    me = np.arange(M)
        
    # 1 критерий delta
    test1 = fit_transform(F, 'v', K)
    u1 = test1*F['t'].values.reshape(M, 1, 1)*F['p'].values.reshape(M, 1, 1) / crew.values.reshape(1, len(U), K)
    
    # 2 критерий delta
    u2 = test1*F['t'].values.reshape(M, 1, 1)*F['p'].values.reshape(M, 1, 1)*\
        F['night'].values.reshape(M, 1, 1) / crew.values.reshape(1, len(U), K)
    
    # 3 критерий delta
    u3 = np.tile(F['night'].values.reshape(-1,1), K).reshape(M, 1, K)
    
    # 4 критерий delta
    u4 = test1
    
    # 5 критерий delta
    u5 = fit_transform(F, 'd', K)
    
    # 6 критерий delta
    u6 = fit_transform(F, 'a', K)
    
    # 7 критерий delta
    u7 = fit_transform(F, 's', K)
        
    # delta
    delta = np.concatenate([u1, u2, u3, u4, u5, u6, u7], axis=1)
    
    assert delta.shape[1] == N
    assert type(delta) == np.ndarray
    
    return delta

if __name__ == '__main__':
    ideal = read_ideal_values()
    delta = read_delta()
