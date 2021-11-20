#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 08:34:12 2021

@author: marcos
"""

import pandas as pd
import classify as nd

I0 = 0
delta = 0.03
step = 0;
n = 0
cycles = 1024
n0 = 0;

ac = nd.Carga()

cargas = []
report = []

path = "../"
ia = nd.IA(path + "out_table", type=nd.Type.KNN)

nomes = ia.n.inputs + [ 'V', 'I' ]
for chunk in pd.read_csv(path + "multi2_d.csv", \
                         usecols=nomes, \
                         chunksize=1024*1024):
    for n, row in chunk.iterrows():
        if step == 0: # Espera pela estabilização dos dados
            if n >= ((cycles*2)-1):
                step = 1
        elif step == 1: # Verifica se a variação é maior que o threshold
            d = abs(row['I'] - ac.I)
            if d > delta:
                I0 = row['I']
                n0 = n
                step = 2
        elif step == 2: # Espera por 200ms
            if (n - n0) >= (cycles*12):
                # Verifica se estabilizou
                d = abs(row['I'] - I0)
                if d < delta:
                    # Faz a detecção de carga se estabilizou
                    d = row['I'] - ac.I
                    if d >= 0:
                        # Remove a carga 'nada' que interfere
                        if len(cargas) == 1:
                            if cargas[0].nome == 'nada':
                                ac = nd.Carga()
                                del cargas[0]
                        # Calcula a carga que entrou e classifica ela
                        l = nd.Carga()
                        l.ini = n;
                        l.P = row['P'] - ac.P
                        l.Q = row['Q'] - ac.Q
                        l.D = row['D'] - ac.D
                        l.V = row['V']
                        l.I = row['I'] - ac.I
                        l.calc_factors()
                        l.nome = ia.classify(l)
                        if l.nome != "nada":
                            print("carga entrou:", l.nome)
                            # Seta o novo patamar, se a carga não foi 'nada'
                            ac.P = row['P']
                            ac.Q = row['Q']
                            ac.D = row['D']
                            ac.V = row['V']
                            ac.I = row['I']
                        cargas.append(l)
                    else:
                        # Calcula a carga que saiu e classifica ela
                        o = nd.Carga()
                        o.fim = n;
                        o.P = ac.P - row['P']
                        o.Q = ac.Q - row['Q']
                        o.D = ac.D - row['D']
                        o.V = row['V']
                        o.I = ac.I - row['I']
                        o.calc_factors()
                        o.nome = ia.classify(o)
                        # Procura pela carga que saiu
                        index = -1
                        i = 0
                        for k in cargas:
                            if k.nome == o.nome:
                                index = i
                                break
                            i = i + 1
                        if index >= 0:
                            print("carga saiu:", cargas[index].nome)
                            ac = nd.Carga()
                            if cargas[index].nome != 'nada':
                                # Recalcula o thresold
                                for o in cargas:
                                    if o != cargas[index]:
                                        ac.P = ac.P + o.P
                                        ac.Q = ac.Q + o.Q
                                        ac.D = ac.D + o.D
                                        ac.I = ac.I + o.I
                                ac.V = row['V']
                            # Atualiza, remove e coloca as cargas no relatório
                            cargas[index].fim = n
                            report.append(cargas[index])
                            cargas.remove(cargas[index])
                        else:
                            # Adiciona a falsa detecção no relatório
                            o.ini = n
                            o.fim = n
                            report.append(o)
                            print("detecção falsa :", o.nome)
                    step = 1; # Volta a procurar por mudamças
                else:
                    I0 = row['I'] # Aguarda a estabilização
                    n0 = n
        else:
            print('default')
