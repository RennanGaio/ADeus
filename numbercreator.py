import random as rd
import numpy.random

# Recebe ro e E[X]
# Retorna lambda tal que lambda = ro / E[X]
def calcula_lambda(ro, EX):
    return ro/EX

# Retorna uma amostra aleatoria do tamanho em bytes de um pacote de dados
# (Amostra da variavel aleatoria X1 - ver descricao do trabalho)
def gera_tamanho_pacote_dados():
    # 0.3 de chance de indice=1, 0.1 de chance de indice=2, e assim por diante
    indice=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
    print indice
    if indice==4:
        tamanho=numpy.random.randint(64,1500)
    elif indice==1:
        tamanho=64
    elif indice==2:
        tamanho=512
    else:
        tamanho=1500
    return tamanho

# def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

# Retorna uma amostra aleatoria do numero de pacotes de voz durante um periodo de atividade
# (Amostra de uma distribuicao geometrica com media de 22 pacotes)
def gera_numero_pacotes_voz():
    return numpy.random.geometric(float(1)/22)

# Recebe numero de pacotes de voz de um periodo de atividade
# Retorna duracao em milisegundos do periodo de atividade
def calcula_duracao_periodo_atividade_voz(n_pacotes):
    return 16*n_pacotes


true_tam = gera_tamanho_pacote_dados()

X1 = (float(true_tam)*8)/2097152

EX1 = (float(735.8)*8)/2097152

print X1
