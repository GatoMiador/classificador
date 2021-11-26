#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 12:42:12 2021

@author: marcos
"""

import classify as nd

path = "../"

size=10

n = nd.Normal();

# Carrega as tabelas com os limites
outliers = {
    'P' : [ 43, 57 ],
    'Q' : [ -15.91, -13.17 ],
    'D' : [ 120.3, 150.3 ],
}
n.load_table(path, 'laptop', outliers, 2799000, 11000000, size)
outliers = {
    'P' : [ 1.12, 1.45 ],
    'Q' : [ -3.1, -2.819 ],
    'D' : [ 17.29, 19.98 ],
}
n.load_table(path, 'luminaria', outliers, 2435000, 11000000, size)
outliers = {
    'P' : [ 4.66, 5.226 ],
    'Q' : [ -3.722, -3.222 ],
    'D' : [ 13.48, 17.77 ],
}
n.load_table(path, 'nada', outliers, 2435000, 11000000, size)
outliers = {
    'P' : [ 13.87, 16.91 ],
    'Q' : [ -7.777, -5.671 ],
    'D' : [ 36.13, 43.85 ],
}
n.load_table(path, 'osciloscópio', outliers, 884100, 11000000, size)
outliers = {
    'P' : [ 75.24, 78.39 ],
    'Q' : [ 77.99, 80.48 ],
    'D' : [ 11.35, 12.37 ],
}
n.load_table(path, 'esmeril', outliers, 2800000, 11000000, size, { 'inrush': True } )
outliers = {
    'P' : [ 280, 300 ],
    'Q' : [ 94.67, 97.36 ],
    'D' : [ 12.09, 14.66 ],
}
n.load_table(path, 'esmeril', outliers, 2176000, 2238000, size, { 'inrush': True } )
outliers = {
    'P' : [ 166, 176 ],
    'Q' : [ -10.35, -9.065 ],
    'D' : [ 10.17, 11.15 ],
}
n.load_table(path, 'ferro_de_solda', outliers, 2098000, 11000000, size)

# Salva
nd.Normal.save(path + "out_table", n)
