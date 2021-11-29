#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 10:53:40 2021

@author: marcos
"""

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

def conf(y_true, y_pred, labels, title):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    disp = ConfusionMatrixDisplay.from_predictions(y_true, y_pred, labels=labels, normalize='all', ax=ax)

    disp.ax_.set_title(title)

    print(title)
    print(disp.confusion_matrix)

    plt.show()
    

labels = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril"]

y_true = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "esmeril"       , "ferro_de_solda", "luminaria"]
y_pred = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "ferro_de_solda", "ferro_de_solda", "luminaria"]

conf(y_true, y_pred, labels, "KNN(1)")

y_true = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "esmeril"       , "ferro_de_solda", "luminaria"]
y_pred = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "ferro_de_solda", "ferro_de_solda", "luminaria"]

conf(y_true, y_pred, labels, "KNN(1) com PCA")

y_true = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "osciloscópio"       , "ferro_de_solda", "luminaria"]
y_pred = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "ferro_de_solda", "ferro_de_solda", "luminaria"]

conf(y_true, y_pred, labels, "MLP")

labels = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "nada"]

y_true = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "nada"       , "ferro_de_solda", "luminaria"]
y_pred = ["luminaria", "ferro_de_solda", "laptop", "osciloscópio", "esmeril", "esmeril", "osciloscópio", "laptop", "ferro_de_solda", "ferro_de_solda", "luminaria"]

conf(y_true, y_pred, labels, "MLP com PCA")
