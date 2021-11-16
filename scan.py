#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 08:34:12 2021

@author: marcos
"""

import pandas as pd

path = "../"

nomes = ['P', 'I', 'fp', 'fl', 'fr' ]

curr0 = 0
curr = 0
delta = 0.03
step = 0;
n = 0
cycles = 1024
n0 = 0;

for chunk in pd.read_csv(path + "multi_d.csv", usecols=nomes, chunksize=1024*1024):
    for d in range(len(chunk['I'])):
        data = chunk['I'][n]
        n = n + 1
        if step == 0: # Espera pela estabilização dos dados
            if n >= (cycles*2):
                step = 1
        elif step == 1: # Verifica se a variação é maior que o threshold
            d1 = abs(data - curr)
            if (d1 > delta):
                n0 = 0
                step = 2
        elif step == 2: # Espera por um ciclo
            n0 = n0 + 1
            if n0 >= cycles:
                curr0 = data
                step = 3
        elif step == 3: # Espera a variação se estabilizar
            d1 = abs(data - curr0)
            if (d1 < delta):
                d2 = data - curr
                if d2 >= 0:
                    print("carga entrou")
                else:
                    print("carga saiu")
                curr = data # Seta o novo patamar
                step = 1; # Volta a procurar por mudamças
            curr0 = data
        else:
            print('default')
