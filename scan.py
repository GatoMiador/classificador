#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 08:34:12 2021

@author: marcos
"""

import pandas as pd
import classify as nd

def rep(o):
    print('Nome:', o.nome)
    print('Tensão:', o.V)
    print('Corrente:', o.I)
    print('Potência Ativa:', o.P)
    print('Potência Reativa:', o.Q)
    print('Potência de Distorção:', o.D)
    print('Faror de não potência:', o.fp)
    print('Faror de não linearidade:', o.fl)
    print('Faror de não reatividade:', o.fr)
    print('Início:', o.ini)
    print('Fim:', o.fim)
    print('Duração:', o.fim - o.ini)
    print('Falso:', o.falso)

I0 = 0
delta = 0.03
step = 0;
n = 0
cycles = 1024
n0 = 0;

def_velocidade = cycles*6
velocidade = def_velocidade

def_ign = (cycles*2)-1
ign = def_ign

inrush = False
hora_inrush = 0

ac = nd.Carga()

cargas = []
report = []

path = "../"
ia = nd.IA(path + "out_table", type=nd.Type.KNN)

nomes = ia.n.inputs + [ 'V', 'I' ]
for chunk in pd.read_csv(path + "multi2_d.csv", \
                         usecols=nomes, \
                         chunksize=1024*1024):
    for n, row in chunk.iterrows():
        if step == 0: # Espera pela estabilização dos dados
            if n >= ign:
                step = 1
        elif step == 1: # Verifica se a variação é maior que o threshold
            d = abs(row['I'] - ac.I)
            if d >= delta:
                n0 = n
                step = 2
        elif step == 2: # Espera o delta ir até o valor programado
            # Só classifica se a corrente se mantém acima do delta pelo tempo
            d = abs(row['I'] - ac.I)
            if d >= delta:
                if (n - n0) >= velocidade:
                    I0 = row['I']
                    n0 = n
                    step = 3
            else:
                step = 1 # Volta para o passo 1 se baixou
        elif step == 3: # Espera estabilizar
            # Verifica se estabilizou
            d = abs(row['I'] - I0)
            if d < delta:
                if (n - n0) >= velocidade:
                    # Encontra a "hora" de quando a carga possivelmente entrou
                    hora = n - velocidade * 2
                    # Sinaliza para voltar a encontrar mudanças
                    step = 1;
                    # Verifica se a carga entrou ou saiu
                    d = row['I'] - ac.I
                    if d >= 0:
                        # Faz aqui se a carga entrou
                        
                        # Remove a carga 'nada' que interfere
                        if len(cargas) == 1:
                            if cargas[0].nome == 'nada':
                                ac = nd.Carga()
                                del cargas[0]
                        # Calcula a carga que entrou e classifica ela
                        l = nd.Carga()
                        l.ini = hora;
                        l.P = row['P'] - ac.P
                        l.Q = row['Q'] - ac.Q
                        l.D = row['D'] - ac.D
                        l.I = row['I'] - ac.I
                        l.V = row['V']
                        l.calc_factors()
                        [ l.nome, f] = ia.classify(l)
                        # Verifica se temos que acionar o modo inrush
                        if f is not None:
                            if 'inrush' in f:
                                if f['inrush'] == True:
                                    if inrush == False:
                                        print('modo inrush acionado:', n)
                                        inrush = True
                                        hora_inrush = hora
                                        velocidade = cycles*60
                                        ign = n + (cycles*60)-1
                                        step = 0
                                    else:
                                        print('modo inrush desligado:', n)
                                        inrush = False
                                        hora = hora_inrush
                                        velocidade = def_velocidade
                                        ign = def_ign
                        if inrush == False:
                            if l.nome != "nada":
                                print("carga entrou:", l.nome, ' -->', hora)
                                # Seta o novo patamar, se a carga não foi 'nada'
                                ac.P = row['P']
                                ac.Q = row['Q']
                                ac.D = row['D']
                                ac.V = row['V']
                                ac.I = row['I']
                            else: 
                                # Se a carga classificada é 'nada' e temos 
                                # cargas ativas, zera os valores para que ela 
                                # seja detectada. Isso acontece porque a carga
                                # 'nada' é *maior* que a menor carga possível
                                if len(cargas) > 0:
                                    ac = nd.Carga()
                            cargas.append(l)
                    else:
                        # Faz aqui se a carga saiu

                        # Calcula a carga que saiu e classifica ela
                        o = nd.Carga()
                        o.fim = hora;
                        o.P = ac.P - row['P']
                        o.Q = ac.Q - row['Q']
                        o.D = ac.D - row['D']
                        o.I = ac.I - row['I']
                        o.V = row['V']
                        o.calc_factors()
                        [ o.nome, f] = ia.classify(o)
                        # Procura pela carga que saiu
                        index = -1
                        i = 0
                        for k in cargas:
                            if k.nome == o.nome:
                                index = i
                                break
                            i = i + 1
                        if index >= 0:
                            print("carga saiu:", cargas[index].nome,
                                  ' -->', hora)
                            ac = nd.Carga()
                            if cargas[index].nome != 'nada':
                                # Recalcula o thresold
                                for o in cargas:
                                    if o != cargas[index]:
                                        ac.P = ac.P + o.P
                                        ac.Q = ac.Q + o.Q
                                        ac.D = ac.D + o.D
                                        ac.I = ac.I + o.I
                                ac.V = row['V']
                                # Retorna os parâmetros default caso alterados
                                velocidade = def_velocidade
                                ign = def_ign
                                inrush = False
                            # Atualiza, remove e coloca as cargas no relatório
                            cargas[index].fim = hora
                            report.append(cargas[index])
                            cargas.remove(cargas[index])
                        else:
                            # Adiciona a falsa detecção no relatório
                            o.ini = hora
                            o.fim = hora
                            o.falso=True
                            report.append(o)
                            print("detecção falsa :", o.nome)
            else:
                # Volta se a entrada se desestabiizou
                step = 2
        else:
            print('default')

# Finaliza as cargas que ainda estavam ativas aqui devido a leitura incorreta
for o in cargas:
    o.fim = n
    report.append(o)
    
report.sort(key=lambda x: x.ini)
print('Relatório:')
for o in report:
    print('---------------------------------')
    rep(o)
