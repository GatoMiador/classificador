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

    voltage = [0] * len(v)
    U = MAF() # Tensão eficaz

    i_a = MAF()

    U_C = MAF() # Valor eficaz da integral imparcial da tensão

    i_r = MAF()

    i_v = MAF()

    Pa = [0] * len(v)

    Q = [0] * len(v)

    D = [0] * len(v)
    
    for index in range(len(v) ):
        # Calcula a potência ativa
        P.feed(v[index]*i[index])
        power[index] = P.get()

        # Calcula a integral parcial da tensão
        v_c.feed(v[index])
        _v_c = v_c.get()

        # Calcula a energia reativa
        W.feed(_v_c * i[index])
        reactive[index] = W.get()

        # Calcula a tensão eficaz
        U.feed(v[index] * v[index])
        _U = U.get()
        
        voltage[index] = math.sqrt(_U)

        # Calcula a corrente ativa
        _ia = 0
        if _U != 0:
            _ia = power[index] * v[index] / _U
        i_a.feed(_ia * _ia)
        Ia = math.sqrt(i_a.get() )

        # Calcula a integral parcial da tensão eficaz ao quadrado
        U_C.feed(_v_c * _v_c)
        _U_C = U_C.get()

        # Calcula a corrente reativa
        _ir = 0
        if _U_C != 0:
            _ir = reactive[index] * _v_c / _U_C
        i_r.feed(_ir * _ir)

        Ir = math.sqrt(i_r.get() )

        # Calcula a corrente residual
        _iv = i[index] - _ia - _ir
        i_v.feed(_iv * _iv)

        Iv = math.sqrt(i_v.get() )

        # Calcula a potência ativa
        Pa[index] = voltage[index] * Ia

        # Calcula a potência reativa
        Q[index] = voltage[index] * Ir

        # Calcula a potência residual
        D[index] = voltage[index] * Iv

    return { 'power': power, 'reactive': reactive, 'voltage': voltage, 'Pa': Pa, 'Q': Q, 'D': D }

arquivo = "../test.csv"

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

#plt.plot(res['power'])
#plt.plot(res['reactive'])
#plt.plot(res['voltage'])
#plt.plot(res['ia'])
#plt.plot(res['ir'])
#plt.plot(res['iv'])
#plt.plot(res['Pa'])
plt.plot(res['Q'])
#plt.plot(res['D'])
#plt.plot(data['VA'])
#plt.plot(res['Ia'])
plt.show()
