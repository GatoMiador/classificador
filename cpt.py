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

def cpt(data, v, i, time, cycles=1024):
    
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
            return self
        
        def get(self):
            return self.full / cycles

    class UnbiasedIntegral(MAF):
        integral = 0

        def feed(self, n):
            self.integral = self.integral + n
            super().feed(self.integral)
            return self
        
        def get(self):
            return (self.integral - super().get() ) * 2 * math.pi / cycles

    Pa = MAF() # Potência ativa média

    v_c = UnbiasedIntegral() # Integral imparcial da tensão
    W = MAF() # Energia reativa média

    V = [0] * len(v)
    U = MAF() # Valor eficaz da tensão

    U_C = MAF() # Valor eficaz da integral imparcial da tensão

    I = [0] * len(v)
    _I = MAF() # Valor eficaz da corrente

    i_a = MAF() # Corrente ativa

    i_r = MAF() # Corrente reativa

    i_v = MAF() # Corrente residual

    P = [0] * len(v) # Potência ativa média

    Q = [0] * len(v) # Potência reativa média

    D = [0] * len(v) # Potência residual média

    fp = [0] * len(v) # Fator de potência

    fl = [0] * len(v) # Fator de não lineridade

    fr = [0] * len(v) # Fator de reatividade

    for index in range(len(v) ):
        # Calcula a potência ativa média
        _P = Pa.feed(v[index]*i[index]).get()

        # Calcula a integral parcial da tensão
        _v_c = v_c.feed(v[index]).get()

        # Calcula a energia reativa
        _W = W.feed(_v_c * i[index]).get()

        # Calcula a tensão eficaz
        _U = U.feed(v[index] ** 2).get()
        V[index] = math.sqrt(_U)

        # Calcula a corrente eficaz
        I[index] = math.sqrt(_I.feed(i[index] ** 2).get() )

        # Calcula a corrente ativa
        _ia = 0
        if _U != 0:
            _ia = _P * v[index] / _U
        Ia = math.sqrt(i_a.feed(_ia ** 2).get() )

        # Calcula a potência ativa
        P[index] = V[index] * Ia

        # Calcula a integral parcial da tensão eficaz ao quadrado
        _U_C = U_C.feed(_v_c ** 2).get()

        # Calcula a corrente reativa
        _ir = 0
        if _U_C != 0:
            _ir = _W * _v_c / _U_C
        Ir = math.sqrt(i_r.feed(_ir ** 2).get() )

        # Calcula a potência reativa
        Q[index] = V[index] * Ir

        # Calcula a corrente residual
        _iv = i[index] - _ia - _ir
        Iv = math.sqrt(i_v.feed(_iv ** 2).get() )

        # Calcula a potência residual
        D[index] = V[index] * Iv

        # Calcula a potência aparente
        A = math.sqrt(P[index]**2 + Q[index]**2 + D[index]**2)

        if A != 0:
            # Calcula o fator de potência
            fp[index] = P[index] / A

            # Calcula o fator de linearidade
            fl[index] = D[index] / A

            # Calcula o fator de reatividade
            fr[index] = Q[index] / A
        else:
            fp[index] = 0
            fl[index] = 0
            fr[index] = 0
    return { 'time': time, 'V': V, 'I': I, 'P': P, 'Q': Q, 'D': D, 'fp': fp, 'fl': fl, 'fr': fr }

arquivo = "../test.csv"

col_names = ['date', 'VA', 'VB', 'VC', 'VN', 'IA', 'IB', 'IC', 'IN']
data = pd.read_csv(arquivo, header=None, names=col_names, sep='\t')

start = time.time()
res = cpt(data, v=data['VA'], i=data['IA'], time=data['date'])
end = time.time()

print("The time of execution of above program is :", end-start)

with open(os.path.splitext(arquivo)[0] + "_d.csv", "w") as outfile:
   writer = csv.writer(outfile)
   writer.writerow(res.keys() )
   writer.writerows(zip(*res.values() ) )

plt.plot(res['V'])
plt.plot(res['I'])
plt.plot(res['P'])
plt.plot(res['Q'])
plt.plot(res['D'])
plt.show()
