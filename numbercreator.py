import random as rd
import numpy.random

# **************************************************************************
# Declaracao de variaveis globais
# **************************************************************************

# E[L] onde L (variavel aleatoria) eh o numero de bytes de um pacote de dados
EL = 735.8

# E[X1] onde X1 (variavel aleatoria) eh o tempo de servico de um pacote de dados
EX1 = (EL*8)/2097152

# Tamanho fixo dos pacotes de voz, em bits
tamanho_pacote_voz = 512

# Tempo de servico fixo de um pacote de voz, em segundos
tempo_servico_pacote_voz = tamanho_pacote_voz/2097152

# Media da duracao do periodo de silencio dos pacotes de voz em segundos
media_periodo_silencio = 0.650

# Inverso da media /\
# Definido aqui para economizar uma operacao de divisao toda vez que for necessario calcular o periodo de silencio
inverso_media_periodo_silencio  = 1/media_periodo_silencio


# Recebe ro e E[X]
# Retorna lambda tal que lambda = ro / E[X]
def calcula_lambda(ro, EX):
    return ro/EX

# **************************************************************************
# Funcoes dos pacotes de dados
# **************************************************************************

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
    print "--> Saiu de [gera_tempo_servico_pacote_dados]"
    return tempo_servico

# **************************************************************************
# Funcoes dos pacotes de voz
# **************************************************************************

# def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

# Retorna uma amostra aleatoria do numero de pacotes de voz durante um periodo de atividade
# (Amostra de uma distribuicao geometrica com media de 22 pacotes)
def gera_numero_pacotes_voz():
    print "--> Entrou em [gera_numero_pacotes_voz]"
    numero_pacotes = numpy.random.geometric(float(1)/22)
    print "numero_pacotes: [" + str(numero_pacotes) + "]"
    print "--> Saiu de [gera_numero_pacotes_voz]"
    return numero_pacotes

# Recebe numero de pacotes de voz de um periodo de atividade
# Retorna duracao em segundos do periodo de atividade
def calcula_duracao_periodo_atividade_voz(n_pacotes):
    print "--> Entrou em [calcula_duracao_periodo_atividade_voz]"
    duracao = (0.016)*n_pacotes
    print "duracao: [" + str(duracao) + "]"
    print "--> Saiu de [calcula_duracao_periodo_atividade_voz]"
    return duracao

# Retorna uma amostra aleatoria da duracao do periodo de silencio dos pacotes de voz
# (Amostra de uma distribuicao exponencial com media de 650ms)
def calcula_duracao_periodo_silencio_voz():
    print "--> Entrou em [calcula_duracao_periodo_silencio_voz]"
    duracao = numpy.random.exponential(inverso_media_periodo_silencio)
    print "duracao: [" + str(duracao) + "]"
    print "--> Saiu de [calcula_duracao_periodo_silencio_voz]"
    return duracao


# **************************************************************************
# Programa principal
# **************************************************************************

print "--> Iniciou programa principal"
X1 = gera_tempo_servico_pacote_dados()
print X1
amostra_periodo_silencio = calcula_duracao_periodo_silencio_voz()
print amostra_periodo_silencio
amostra_periodo_atividade = calcula_duracao_periodo_atividade_voz(gera_numero_pacotes_voz())
print "--> Terminou programa principal"