#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 12:42:12 2021

@author: marcos
"""

import pandas as pd

output = "tabela_ia.csv"

nomes = ['P', 'fp', 'fl', 'fr' ]

table = pd.DataFrame(columns=nomes)

path = "../"

def load_table(arquivo, field, ini, fim, num):
    n = path + arquivo + "_d.csv"
    data = pd.read_csv(n, usecols=nomes)
    data = data.drop(data[data[field] < ini].index)
    data = data.drop(data[data[field] > fim].index)

    data['class'] = [ arquivo ] * len(data.index)
    return data.sample(num)

table = table.append(load_table('laptop', 'P', 50, 60, 1000) )
table = table.append(load_table('luminaria', 'P', 1, 2, 1000) )
table = table.append(load_table('nada', 'P', 4, 6, 1000) )
table = table.append(load_table('osciloscópio', 'P', 10, 20, 1000) )
table = table.append(load_table('esmeril', 'P', 60, 90, 1000) )
table = table.append(load_table('ferro_de_solda', 'P', 160, 180, 1000) )

table.to_csv(path + "out_table.csv", index = False)
