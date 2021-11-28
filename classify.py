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
from sklearn.decomposition import PCA
import copy

class Carga:
    nome = 'nada'
    P = 0 
    Q = 0 
    D = 0 
    V = 0 
    I = 0 
    Ia = 0
    Ir = 0
    Iv = 0
    fp = 0 
    fl = 0
    fr = 0
    ini = -1
    fim = -1
    falso=False
    prob = 0

    # Calcula os fatores do CPT
    def calc_factors(self):
        # Calcula o fator de potência
        self.fp = self.Ia / self.I
        # Calcula o fator de linearidade (versão Wesley)
        self.fl = 1 - self.Iv / self.I
        # Calcula o fator de reatividade (versão Wesley)
        self.fr = 1 - self.Ir / self.I


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
        # Remove os dados de início
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
    def save(arquivo, f, report=True):
        f.table.reset_index(drop=True, inplace=True)
        # Salva os parâmetros que a IA vai usar
        with open(arquivo + ".data", 'wb') as outp:
            pickle.dump(f, outp, pickle.HIGHEST_PROTOCOL)
            outp.close()
        # Salva o report dos dados aprendidos, se configurado
        if report == True:
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

    def calc_params(self, data):
        minvals = data[self.inputs].min(axis=0)
        maxvals = data[self.inputs].max(axis=0)
        # Normaliza os dados das potências
        self.params.clear()
        inputs = copy.copy(self.inputs)
        factors = [ 'fp', 'fl', 'fr']
        for e in factors:
            if e in inputs:
                inputs.remove(e)
        for o in inputs:
            self.params[o] = [ minvals[o], maxvals[o] - minvals[o] ]
        # Trata os fatores de potência e etc. como casos especiais
        # já que seus valores já estão entre 0 e 1
        self.params['fp'] = [ 0, 1 ]
        self.params['fl'] = [ 0, 1 ]
        self.params['fr'] = [ 0, 1 ]

class Type(Enum):
    KNN = 1
    NEURAL = 2

class IA:
    def __init__(self, f, type=Type.KNN, pca=True):
        self.n = Normal.load(f)
        # Encontra os valores de normalização
        self.n.calc_params(self.n.table)
        # Adicionado o peso para a potência ativa
        self.n.params['P'][1] = self.n.params['P'][1] / 4
        # Faz a normalização
        for o in self.n.inputs:
            self.n.table[o] = self.n.table[o] - self.n.params[o][0]
            self.n.table[o] = self.n.table[o] / self.n.params[o][1]
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
                solver='lbfgs', hidden_layer_sizes=(13,), random_state=1)
            self.predictor.fit(X, self.n.table[Normal.outputs[0] ])

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
        p = max(self.predictor.predict_proba(z)[0])
        # Devolve as peculiaridades da carga
        f = self.n.table[self.n.table[self.n.outputs[0] ] == n] \
            [self.n.features[0]].head(1).values[0]

        return [ n, f,  p]
