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
            return (self.integral - super().get() ) * math.pi / cycles

    class Reactive:
        def __init__(self):
            self.v_c = UnbiasedIntegral()
            self.maf = MAF()

        def feed(self, v, i):
            self.v_c.feed(v)
            w = self.v_c.get()
            self.maf.feed(w * i)
            return
        
        def get(self):
            return self.maf.get()

    _power = MAF()
    power = [0] * len(v)
    
    reactive = [0] * len(v)
    _reactive = Reactive()
    
    for index in range(len(v) ):
        _power.feed(v[index]*i[index])
        power[index] = _power.get()

        _reactive.feed(v[index], i[index])
        reactive[index] = _reactive.get()
        
    return { 'power': power, 'reactive': reactive }

arquivo = "../test.csv"

col_names = ['date', 'VA', 'VB', 'VC', 'VN', 'IA', 'IB', 'IC', 'IN']
data = pd.read_csv(arquivo, header=None, names=col_names, sep='\t')

start = time.time()
res = cpt(data, v=data['VA'], i=data['IA'])
end = time.time()

print("The time of execution of above program is :", end-start)

plt.plot(res['power'])
plt.plot(res['reactive'])
plt.show()
