#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 08:49:01 2021

@author: marcos
"""

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import pickle
import json
from enum import Enum

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

class Normal:
    inputs = [ 'P', 'Q', 'D', 'fp', 'fl', 'fr']
    outputs = [ 'class' ]

    def __init__(self):
        self.params = {}
        for o in self.inputs:
            self.params[o] = [ 0, 1 ]
        self.classes = []

    table = pd.DataFrame(columns=inputs)

    def clean_table(self):
        self.table.clear()
        self.params.clear();

    def load_table(self, path, nome, field, ini, fim, num):
        n = path + nome + "_d.csv"
        data = pd.read_csv(n, usecols=self.inputs)
        data = data.drop(data[data[field] < ini].index)
        data = data.drop(data[data[field] > fim].index)
        sample = data.sample(num)
        self.classes = self.classes + [ nome ]
        sample[self.outputs[0] ] = \
            [ int(self.classes.index(nome) ) ] * len(sample.index)
        self.table = self.table.append(sample)
        return

    @staticmethod
    def load(arquivo):
        with open(arquivo + ".data", 'rb') as inp:
            r = pickle.load(inp)
            inp.close()
            return r

    @staticmethod
    def save(arquivo, f, normalize=True, report=True):
        # Salva os dados normalizados, se configurado
        if normalize == True:
            f.params.clear()
            for o in f.inputs:
                mn = min(f.table[o])
                f.table[o] = f.table[o] - mn
                mx = max(f.table[o])
                f.table[o] = f.table[o] / mx
                f.params[o] = [ mn, mx ]
        # Salva os parâmetros
        with open(arquivo + ".data", 'wb') as outp:
            pickle.dump(f, outp, pickle.HIGHEST_PROTOCOL)
            outp.close()
        # Salva o report dos dados aprendidos, se configurado
        if report == True:
            f.table.to_csv(arquivo + ".csv", index = False)
            with open(arquivo + "_params.txt", 'w') as file:
                file.write(json.dumps(f.params) )
                file.close()
            with open(arquivo + "_classes.txt", 'w') as file:
                file.writelines(f.classes)
                file.close()

    def normalize(self, f):
        for o in self.inputs:
            f[o] = f[o] - self.params[o][0]
            f[o] = f[o] / self.params[o][1]
        return f

class Type(Enum):
    KNN = 1
    NEURAL = 2

class IA:
    def __init__(self, f, type=Type.KNN):
        self.n = Normal.load(f)
        if type == Type.KNN:
            self.__predictor = KNeighborsClassifier(n_neighbors=1)
            self.__predictor.fit(
                self.n.table[ Normal.inputs ].values,
                self.n.table[Normal.outputs[0] ])
        elif type == Type.NEURAL:
            self.__predictor = MLPClassifier(
                solver='lbfgs', alpha=1e-5,
                hidden_layer_sizes=(13, 2), random_state=1)
            self.__predictor.fit(
                self.n.table[ Normal.inputs ].values,
                self.n.table[Normal.outputs[0] ])

    # Faz a classificação dos dados de carga
    def classify(self, l):
        r = self.n.normalize({
            'P': l.P,
            'Q': l.Q,
            'D': l.D,
            'fp': l.fp,
            'fl': l.fl,
            'fr': l.fr })
        n = self.__predictor.predict([[
            r['P'],
            r['Q'],
            r['D'],
            r['fp'],
            r['fl'],
            r['fr'] ]])[0]
        return self.n.classes[int(n)]
