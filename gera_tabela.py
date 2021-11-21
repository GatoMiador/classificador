#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 12:42:12 2021

@author: marcos
"""

import classify as nd

path = "../"

size=1000

n = nd.Normal();

# Carrega as tabelas com os limites
n.load_table(path, 'laptop', 'P', 50, 60, size)
n.load_table(path, 'luminaria', 'P', 1, 2, size)
n.load_table(path, 'nada', 'P', 4, 6, size)
n.load_table(path, 'osciloscópio', 'P', 10, 20, size)
n.load_table(path, 'esmeril', 'P', 60, 295, size)
n.load_table(path, 'ferro_de_solda', 'P', 160, 180, size)

# Salva
nd.Normal.save(path + "out_table", n)
