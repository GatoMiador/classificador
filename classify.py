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
import math
import copy
from sklearn.decomposition import PCA

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
    falso=False

    # Calcula os fatores do CPT
    def calc_factors(self):
        A = math.sqrt(self.P**2 + self.Q**2 + self.D**2)
        self.fp = self.P / A
        self.fl = self.D / A
        self.fr = self.Q / A


class Normal:
    inputs = [ 'P', 'Q', 'D', 'fp', 'fl', 'fr']
    learning_data = [ 'P', 'fp', 'fl', 'fr']
    features = [ 'features' ]
    outputs = [ 'class' ]

    def __init__(self):
        self.params = {}
        for o in self.inputs:
            self.params[o] = [ 0, 1 ]

    table = pd.DataFrame(columns=inputs)

    def clean_table(self):
        self.table.clear()
        self.params.clear();

    # Carrega uma tabela com dados para ensinar a IA
    def load_table(self, path, nome, outliers, start, stop, size, f=None):
        # Carrega o dataset
        n = path + nome + "_d.csv"
        data = pd.read_csv(n, usecols=self.inputs, nrows=stop)
        # Calcula os mínimos e máximos
        minvals = data.min(axis=0)
        maxvals = data.max(axis=0)
        if hasattr(self, 'minvals') == False:
            self.minvals = copy.copy(minvals)
        if hasattr(self, 'maxvals') == False:
            self.maxvals = copy.copy(maxvals)
        for (a, b) in zip(self.minvals, minvals):
            a = min(a, b)
        for (a, b) in zip(self.maxvals, maxvals):
            a = max(a, b)
        # Carrega a tabela
        data.drop(range(start,), inplace=True)
        # Remove os outliers
        for field in outliers:
            data = data.drop(data[data[field] < outliers[field][0] ].index)
            data = data.drop(data[data[field] > outliers[field][1] ].index)
        if data.shape[0] < size:
            raise ValueError('Dados insuficientes após a remoção dos outliers,'
                ' arquivo ', nome, '.')
        # Pega as amostras aleatórias
        sample = data.sample(size)
        # Adiciona as features
        sample[self.features[0]] = \
            [ f ] * len(sample.index)
        # Adiciona o nome da carga
        sample[self.outputs[0] ] = [ nome ] * len(sample.index)
        self.table = self.table.append(sample)
        return

    # Carrega a tabela de descritores para uso
    @staticmethod
    def load(arquivo):
        with open(arquivo + ".data", 'rb') as inp:
            r = pickle.load(inp)
            inp.close()
            return r

    # Salva a tabela de descritores e o relatório para verificação
    @staticmethod
    def save(arquivo, f, normalize=True, report=True):
        to = pd.DataFrame()
        f.table.reset_index(drop=True, inplace=True)
        # Salva os dados normalizados, se configurado
        if normalize == True:
            # Salva os dados não normalizados, não usados pela IA
            to = copy.deepcopy(f.table)
            to.drop(f.outputs[0], axis='columns', inplace=True)
            to.drop(f.features[0], axis='columns', inplace=True)
            for c in f.inputs:
                to.rename(columns = {c: c+'_o'}, inplace = True)
            # Normaliza os dados
            f.params.clear()
            inputs = copy.copy(f.inputs)
            factors = [ 'fp', 'fl', 'fr']
            for e in factors:
                if e in inputs:
                    inputs.remove(e)
            for o in inputs:
                mini = f.minvals[o]
                maxi = (f.maxvals[o] - f.minvals[o]) / 10
                f.table[o] = f.table[o] - mini
                f.table[o] = f.table[o] / maxi
                f.params[o] = [ mini, maxi ]
            # Trata os fatores de potência e etc. como casos especiais
            # já que seus valores já estão entre 0 e 1
            f.params['fp'] = [ 0, 1 ]
            f.params['fl'] = [ 0, 1 ]
            # O fator de reatividade está sempre entre -1 e 1, normaliza
            f.params['fr'] = [ -1, 2 ]
            f.table['fr'] = f.table['fr'] - f.params['fr'][0]
            f.table['fr'] = f.table['fr'] / f.params['fr'][1]
        # Salva os parâmetros que a IA vai usar
        del f.minvals
        del f.maxvals
        with open(arquivo + ".data", 'wb') as outp:
            pickle.dump(f, outp, pickle.HIGHEST_PROTOCOL)
            outp.close()
        # Salva o report dos dados aprendidos, se configurado
        if report == True:
            # Adiciona ao relatório os dados não normalizados
            if normalize == True:
                f.table = pd.concat([f.table, to], axis=1)
            # Adiciona os dados usados pela IA
            f.table.to_csv(arquivo + ".csv", index = False)
            with open(arquivo + "_params.txt", 'w') as file:
                file.write(json.dumps(f.params) )
                file.close()

    # Normaliza os dados de teste e validação
    def normalize(self, f):
        for o in self.inputs:
            f[o] = f[o] - self.params[o][0]
            f[o] = f[o] / self.params[o][1]
        return f

class Type(Enum):
    KNN = 1
    NEURAL = 2

class IA:
    def __init__(self, f, type=Type.KNN, pca=True):
        self.n = Normal.load(f)
        # Faz a PCA
        self.pca = pca
        if self.pca == True:
            self.p = PCA(n_components=3)
            X = self.p.fit_transform(self.n.table[Normal.learning_data].values)
            print('PCA:',
                  len(self.n.table[ Normal.learning_data ].columns),
                  '-->',
                  len(X[0]) )
        else:
            X = self.n.table[Normal.learning_data].values
        # Faz a classificação de acordo com os dados de aprendizado
        if type == Type.KNN:
            self.predictor = KNeighborsClassifier(n_neighbors=1)
            self.predictor.fit(X, self.n.table[Normal.outputs[0] ])
        elif type == Type.NEURAL:
            self.predictor = MLPClassifier(
                solver='lbfgs', alpha=1e-5,
                hidden_layer_sizes=(13, 2), random_state=1)
            self.__predictor.fit(X, self.n.tablez[Normal.outputs[0] ])

    # Faz a classificação dos dados de carga
    def classify(self, l):
        # Normaliza a entrada para o classificador
        r = self.n.normalize({
            'P': l.P,
            'Q': l.Q,
            'D': l.D,
            'fp': l.fp,
            'fl': l.fl,
            'fr': l.fr })
        z = [ ]
        for n in Normal.learning_data:
            z = z + [ r[n] ]
        # Faz a PCA caso habilitada
        if self.pca == True:
            z = self.p.transform([z])
        else:
            z = [ z ]
        # Envia para a IA para encontrar o número da carga
        n = self.predictor.predict(z)[0]
        # Devolve as peculiaridades da carga
        f = self.n.table[self.n.table[self.n.outputs[0] ] == n] \
            [self.n.features[0]].head(1).values[0]

        return [ n, f ]
