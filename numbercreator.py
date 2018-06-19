import random as rd
import numpy.random

def calc_lambda(ro, EX):
    return ro/EX

def generete_package_size_dados():
    tam_pacote=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
    print tam_pacote
    if tam_pacote==4:
        true_tam=numpy.random.randint(64,1500)
    elif tam_pacote==1:
        true_tam=64
    elif tam_pacote==2:
        true_tam=512
    else:
        true_tam=1500
    return true_tam

def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

def numero_pacotes_atividade_voz():
    return numpy.random.geometric(float(1)/22)

def periodo_atividade_voz(n_pacotes):
    return 16*n_pacotes


true_tam = generete_package_size_dados()

X1 = (float(true_tam)*8)/2097152

EX1 = (float(735.8)*8)/2097152

print X1
