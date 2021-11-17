#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 08:49:01 2021

@author: marcos
"""

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

class Carga:
    nome = 'nada'
    P = 0 
    Q = 0 
    D = 0 
    V = 0 
    I = 0 
    fp = 0 
    fl = 0
    fr = 0
    ini = -1
    fim = -1

class IA:
    def __init__(self, path):    
        ia = pd.read_csv(path, \
                         usecols=[ 'P', 'Q', 'D', 'fp', 'fl', 'fr', 'class' ] )
        self.__neigh = KNeighborsClassifier(n_neighbors=1)
        self.__neigh.fit(ia[ ['P', 'Q', 'D', 'fp', 'fl', 'fr'] ], ia['class'])

    # Normaliza dados para a IA
    @staticmethod
    def normalize(P, Q, D, fr):
        P = P / 800
        Q = (Q + 400) / 800
        D = D / 1400
        fr = (fr + 1) / 2
        return [ P, Q, D, fr ]

    # Faz a classificação dos dados de carga
    def classify(self, l):
        [ P, Q, D, fr ] = self.normalize(l.P, l.Q, l.D, l.fr)
        nome = self.__neigh.predict([[ P, Q, D, l.fp, l.fl, l.fr ]])
        return nome[0]
