import air_modules as am
import numpy as np
import pandas as pd
import itertools


def read_ideal_values(data=pd.read_excel('ID.xls'), crew=pd.read_json('crew.json')):
    '''На вход принимает информацию о связках и книгах,
    возвращает матрицу np.array идеальных значений
    >>> ideals = read_ideal_values(data, crew)
    >>> ideals[j, k] #сначала номер критерия, затем номер книги
    >>> print(type(ideals))
    <class 'numpy.ndarray'>
    '''
    # --------- IMPORT------------
    # data = pd.read_excel('ID.xls')
    # crew = pd.read_json('crew.json')
    data['night'] = np.array([am.is_night_flight(data.iloc[i])*1 for i in range(data.shape[0])])
    M = data.shape[0]
    # ---------Preprocessing ---------
    F_columns = ['t', 'p', 'v', 'd', 'a', 's', 'goodbye', 'night']
    F = pd.DataFrame(columns=F_columns, index=data['Связка'])
    data_columns = ['Налет', 'Экипаж', 'Тип связи', 'День месяца',\
                    'Тип судна', 'Назначение', 'Время вылета', 'night']
    F[F_columns] = data[data_columns].values
    F['t'] = pd.to_datetime(F['t']).dt.minute / 60 + \
        pd.to_datetime(F['t']).dt.hour
    F['goodbye'] = pd.to_datetime(F['goodbye']).dt.minute / 60 +\
        pd.to_datetime(F['goodbye']).dt.hour
    F[['p', 'd', 'night']] = F[['p', 'd', 'night']].astype(int)
    F[['v', 'a', 's']] = F[['v', 'a', 's']].astype(str)
    F['a'] = F['a'].apply(lambda x: x.strip())
    v_mapping = {'ВВЛ': 1, 'МВЛ': 2, 'СНГ': 3}
    a_mapping = {'А-319': 1, 'А-320': 2}
    F['a'] = F['a'].map(a_mapping)
    F['v'] = F['v'].map(v_mapping)
    F['s'] = F['s'].apply(lambda x: int(x.split()[1]))
    K = len(crew.columns)
    L = sorted(pd.unique(F['a']))
    R = sorted(pd.unique(F['s']))
    T = sorted(pd.unique(F['d']))
    U = sorted(pd.unique(F['v']))
    j = np.arange(len(U)) + 1
    k = np.arange(K) + 1
    t = np.arange(len(T)) + 1
    l = np.arange(len(L)) + 1
    s = np.arange(len(R)) + 1
    N = 10 + len(T) + len(L) + len(R)
    # -----------------permutations------------------
    all_permutations_j_k = list(itertools.product(j, k))
    all_permutations_t_k = list(itertools.product(t, k))
    all_permutations_l_k = list(itertools.product(l, k))
    all_permutations_s_k = list(itertools.product(s, k))
    # ------------------1 критерий------------------
    y1 = np.array([f"y[{j}, {k}]" for j,k in all_permutations_j_k]) 
    y1_ideal = np.array([(F[F['v']==j]['p']*F[F['v']==j]['t']).sum() / crew.iloc[j-1].sum()  for j, k in all_permutations_j_k]) 
    c_1 = pd.DataFrame(data=y1_ideal, index = y1, columns = ['c_1']) 
    # ------------------2 критерий------------------
    y2 = np.array([f"y[{j+3}, {k}]" for j, k in all_permutations_j_k])
    y2_ideal = np.array([(F[(F['v']==j) & (F['night']==1)]['p']*F[(F['v']==j) & (F['night']==1)]['t']).sum() / crew.iloc[j-1].sum()  for j, k in all_permutations_j_k])
    c_2 = pd.DataFrame(data=y2_ideal, index = y2, columns = ['c_2'])
    # ------------------2 критерий-------------------
    y3 = np.array([f"y[{7}, {item}]" for item in k])
    y3_ideal = np.array([crew.iloc[0][item]*F[(F['night']==1)].shape[0] / crew.iloc[0].sum() for item in k ])
    c_3 = pd.DataFrame(data=y3_ideal, index = y3, columns = ['c_3'])
    # ------------------4 критерий-------------------------
    y4 = np.array([f"y[{7+j}, {k}]" for j, k in all_permutations_j_k])
    y4_ideal = np.array([F[F['v']==j].shape[0]*crew.iloc[j-1][k] / crew.iloc[j-1].sum()  for j, k in all_permutations_j_k])
    c_4 = pd.DataFrame(data=y4_ideal, index = y4, columns = ['c_4'])
    # ---------------------5 критерий-------------------
    y5 = np.array([f"y[{10+j}, {k}]" for j, k in all_permutations_t_k])
    y5_ideal = np.array([ F[F['d']==t].shape[0] / K for t, k in all_permutations_t_k])
    c_5 = pd.DataFrame(data=y5_ideal, index = y5, columns = ['c_5'])
    # ------------------------6 критерий-------------------
    y6 = np.array([f"y[{10+j+len(T)}, {k}]" for j, k in all_permutations_l_k])
    y6_ideal = np.array([F[F['a']==l].shape[0] / K for l, k in all_permutations_l_k])
    c_6 = pd.DataFrame(data=y6_ideal, index = y6, columns = ['c_6'])
    # -----------------7 критерий-------------------
    y7 = np.array([f"y[{10+j+len(T)+len(L)}, {k}]" for j, k in all_permutations_s_k])
    y7_ideal = np.array([F[F['s']==s].shape[0] / K for s, k in all_permutations_s_k])
    c_7 = pd.DataFrame(data=y7_ideal, index = y7, columns = ['c_7'])
    ideals = np.concatenate([c_1.values.reshape(-1, K), c_2.values.reshape(-1,K),\
                    c_3.values.reshape(-1,K), c_4.values.reshape(-1,K),\
                    c_5.values.reshape(-1,K), c_6.values.reshape(-1,K),\
                    c_7.values.reshape(-1,K)])
        
    full_index  = [f"y[{i}]" for i in np.arange(1, N + 1) ]
    full_columns = np.arange(K) + 1
    ideal_dataframe = pd.DataFrame(data = ideals, index =  full_index, columns=full_columns)
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
    
    data['night'] = np.array([am.is_night_flight(data.iloc[i])*1 for i in range(data.shape[0])])
    M = data.shape[0]
    # ---------Preprocessing ---------
    F_columns = ['t', 'p', 'v', 'd', 'a', 's', 'goodbye', 'night']
    F = pd.DataFrame(columns=F_columns, index=data['Связка'])
    data_columns = ['Налет', 'Экипаж', 'Тип связи', 'День месяца',\
                    'Тип судна', 'Назначение', 'Время вылета', 'night']
    F[F_columns] = data[data_columns].values
    F['t'] = pd.to_datetime(F['t']).dt.minute / 60 + \
        pd.to_datetime(F['t']).dt.hour
    F['goodbye'] = pd.to_datetime(F['goodbye']).dt.minute / 60 +\
        pd.to_datetime(F['goodbye']).dt.hour
    F[['p', 'd', 'night']] = F[['p', 'd', 'night']].astype(int)
    F[['v', 'a', 's']] = F[['v', 'a', 's']].astype(str)
    F['a'] = F['a'].apply(lambda x: x.strip())
    v_mapping = {'ВВЛ': 1, 'МВЛ': 2, 'СНГ': 3}
    a_mapping = {'А-319': 1, 'А-320': 2}
    F['a'] = F['a'].map(a_mapping)
    F['v'] = F['v'].map(v_mapping)
    F['s'] = F['s'].apply(lambda x: int(x.split()[1]))
    K = len(crew.columns)
    L = sorted(pd.unique(F['a']))
    R = sorted(pd.unique(F['s']))
    T = sorted(pd.unique(F['d']))
    U = sorted(pd.unique(F['v']))
    j = np.arange(len(U)) + 1
    k = np.arange(K) + 1
    t = np.arange(len(T)) + 1
    l = np.arange(len(L)) + 1
    s = np.arange(len(R)) + 1
    N = 10 + len(T) + len(L) + len(R)
    
    me = np.arange(M)
    all_permutations_m_j_k = list(itertools.product(me, j, k))
    all_permutations_m_t_k = list(itertools.product(me, t, k))
    all_permutations_m_l_k = list(itertools.product(me, l, k))
    all_permutations_m_s_k = list(itertools.product(me, s, k))
    
    test1 = np.array([(F.iloc[m]['t']*F.iloc[m]['p']*int(F.iloc[m]['v']==j) / crew.iloc[j-1][k]) for m, j, k in all_permutations_m_j_k])
    u1 = test1.reshape(M,len(U),K)
    
    test2 = np.array([(F.iloc[m]['t']*F.iloc[m]['p']*int(F.iloc[m]['v']==j)*int(F.iloc[m]['night']==1) / crew.iloc[j-1][k]) \
                      for m,j,k in all_permutations_m_j_k])
    u2 = test2.reshape(M,len(U),K)
    
    u3 = np.zeros((M,1,K))
    
    test4 = np.array([int(F.iloc[m]['v']==j) for m,j,k in all_permutations_m_j_k])
    u4 = test4.reshape(M,len(U),K)
    
    test5 = np.array([ int(F.iloc[m]['d'] == t) / K for m,t,k in all_permutations_m_t_k])
    u5 = test5.reshape(M,len(T),K)
    
    test6 = np.array([ int(F.iloc[m]['a'] == l) / K for m,l,k in all_permutations_m_l_k])
    u6 = test6.reshape(M,len(L),K)
    
    test7 = np.array([ int(F.iloc[m]['s'] == s) / K for m,s,k in  all_permutations_m_s_k])
    u7 = test7.reshape(M,len(R),K)
    
    delta = np.concatenate([u1,u2,u3,u4,u5,u6,u7], axis = 1)
    return delta


ideal = read_ideal_values()
delta = read_delta()


    






