import random as rd
import numpy.random

# *******************************
# Declaracao de variaveis globais
# *******************************

# E[L] onde L (variavel aleatoria) eh o numero de bytes de um pacote de dados
EL = 735.8

# E[X1] onde X1 (variavel aleatoria) eh o tempo de servico de um pacote de dados
EX1 = (EL*8)/2097152


# Recebe ro e E[X]
# Retorna lambda tal que lambda = ro / E[X]
def calcula_lambda(ro, EX):
    return ro/EX

# ****************************
# Funcoes dos pacotes de dados
# ****************************

# Retorna uma amostra aleatoria do tamanho em bytes de um pacote de dados
# (Amostra da variavel aleatoria L - ver descricao do trabalho)
def gera_tamanho_pacote_dados():
    print "--> Entrou em [gera_tamanho_pacote_dados]"
    # 0.3 de chance de indice=1, 0.1 de chance de indice=2, e assim por diante
    indice=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
    print "indice: [" + str(indice) + "]"
    if indice==4:
        tamanho=numpy.random.randint(64,1500)
    elif indice==1:
        tamanho=64
    elif indice==2:
        tamanho=512
    else:
        tamanho=1500
    print "tamanho: [" + str(tamanho) + "]"
    print "--> Saiu de [gera_tamanho_pacote_dados]"
    return tamanho

# Retorna uma amostra aleatoria do tempo de servico em segundos de um pacote de dados
# (Amostra da variavel aleatoria X1 - ver descricao do trabalho)
def gera_tempo_servico_pacote_dados():
    print "--> Entrou em [gera_tempo_servico_pacote_dados]"
    tamanho = gera_tamanho_pacote_dados()
    # Converte o tamanho de bytes para bits (multiplicando por 8), e divide por 2Mbps para obter o tempo de transmissao
    tempo_servico = float(tamanho*8)/2097152
    print "tempo_servico: [" + str(tempo_servico) + "]"
    print "--> Saiu de [gera_tamanho_pacote_dados]"
    return tempo_servico

# **************************
# Funcoes dos pacotes de voz
# **************************

# def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

# Retorna uma amostra aleatoria do numero de pacotes de voz durante um periodo de atividade
# (Amostra de uma distribuicao geometrica com media de 22 pacotes)
def gera_numero_pacotes_voz():
    return numpy.random.geometric(float(1)/22)

# Recebe numero de pacotes de voz de um periodo de atividade
# Retorna duracao em milisegundos do periodo de atividade
def calcula_duracao_periodo_atividade_voz(n_pacotes):
    return 16*n_pacotes


# ******************
# Programa principal
# ******************

print "--> Iniciou programa principal"
X1 = gera_tempo_servico_pacote_dados()

print X1
print "--> Terminou programa principal"