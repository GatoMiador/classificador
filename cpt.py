#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 14:18:26 2021

@author: marcos
"""

import pandas as pd
import matplotlib.pyplot as plt
import time
import math
import os
import csv

def cpt(data, v, i, cycles=1024):
    
    class MAF:
        index = 0
        full = 0

        def __init__(self):
            self.moving = [0] * cycles
        
        def feed(self, n):
            self.full = self.full - self.moving[self.index]
            self.full = self.full + n
            self.moving[self.index] = n
            
            self.index = self.index + 1
            if self.index >= cycles:
                self.index = self.index - cycles
            return
        
        def get(self):
            return self.full / cycles

    class UnbiasedIntegral(MAF):
        integral = 0

        def feed(self, n):
            self.integral = self.integral + n
            super().feed(self.integral)
            return
        
        def get(self):
            return (self.integral - super().get() ) * 2 * math.pi / cycles

    power = [0] * len(v)
    P = MAF() # Potência ativa média

    reactive = [0] * len(v)
    v_c = UnbiasedIntegral() # Integral imparcial da tensão
    W = MAF() # Energia reativa média

    for index in range(len(v) ):
        P.feed(v[index]*i[index])
        power[index] = P.get()

        v_c.feed(v[index])
        W.feed(v_c.get() * i[index])

        reactive[index] = W.get()

    return { 'power': power, 'reactive': reactive }

arquivo = "../luminaria.csv"

col_names = ['date', 'VA', 'VB', 'VC', 'VN', 'IA', 'IB', 'IC', 'IN']
data = pd.read_csv(arquivo, header=None, names=col_names, sep='\t')

start = time.time()
res = cpt(data, v=data['VA'], i=data['IA'])
end = time.time()

print("The time of execution of above program is :", end-start)

with open(os.path.splitext(arquivo)[0] + "_d.csv", "w") as outfile:
   writer = csv.writer(outfile)
   writer.writerow(res.keys())
   writer.writerows(zip(*res.values()))

plt.plot(res['power'])
plt.plot(res['reactive'])
plt.show()
