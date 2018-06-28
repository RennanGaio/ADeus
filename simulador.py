import random as rd
import numpy.random

# ********************************************************************
# Declaracao de variaveis globais
# ********************************************************************

modo_debug = False

# Recebe ro e E[X]
# Retorna lambda tal que lambda = ro / E[X]
def calcula_lambda(ro, EX):
    return ro/EX

# E[L] onde L (variavel aleatoria) eh o numero de bytes de um pacote de dados
EL = float(755)

# E[X1] onde X1 (variavel aleatoria) eh o tempo de servico de um pacote de dados
EX1 = (EL*8)/float(2097152)

# ro1, utilizacao do sistema levando em conta apenas os pacotes de dados
# ro1 = lambda1 * E[X1] -- ver descricao do trabalho
ro1 = 0.3

# lambda1, taxa de chegada dos pacotes de dados
lamb1 = calcula_lambda(ro1, EX1)

# Tamanho fixo dos pacotes de voz, em bits
tamanho_pacote_voz = 512

# Tempo de servico fixo de um pacote de voz, em segundos
tempo_servico_pacote_voz = tamanho_pacote_voz/2097152

# Media da duracao do periodo de silencio dos pacotes de voz em segundos
media_periodo_silencio = 0.650




# ********************************************************************
# Funcoes dos pacotes de dados
# ********************************************************************

# Retorna uma amostra aleatoria do tamanho em bytes de um pacote de dados
# (Amostra da variavel aleatoria L - ver descricao do trabalho)
def gera_tamanho_pacote_dados():
    if modo_debug: print "--> Entrou em [gera_tamanho_pacote_dados]"
    # 0.3 de chance de indice=1, 0.1 de chance de indice=2, e assim por diante
    indice=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
    if modo_debug: print "\tindice: [" + str(indice) + "]"
    if indice==4:
        tamanho=numpy.random.randint(64,1500)
    elif indice==1:
        tamanho=64
    elif indice==2:
        tamanho=512
    else:
        tamanho=1500
    if modo_debug: print "\ttamanho: [" + str(tamanho) + "]"
    if modo_debug: print "--> Saiu de [gera_tamanho_pacote_dados]"
    return tamanho

# Retorna uma amostra aleatoria do tempo de servico em segundos de um pacote de dados
# (Amostra da variavel aleatoria X1 - ver descricao do trabalho)
def gera_tempo_servico_pacote_dados():
    if modo_debug: print "--> Entrou em [gera_tempo_servico_pacote_dados]"
    tamanho = gera_tamanho_pacote_dados()
    # Converte o tamanho de bytes para bits (multiplicando por 8), e divide por 2Mbps para obter o tempo de transmissao
    tempo_servico = float(tamanho*8)/2097152
    if modo_debug: print "\ttempo_servico: [" + str(tempo_servico) + "]"
    if modo_debug: print "--> Saiu de [gera_tempo_servico_pacote_dados]"
    return tempo_servico

# Retorna uma amostra aleatoria de uma chegada de um pacote de dados em segundos
# (Amostra de uma variavel exponencial com taxa lamb = ro/E[X1])
def gera_chegada_pacote_dados(lamb):
    if modo_debug: print "--> Entrou em [gera_chegada_pacote_dados]"
    tempo_chegada = numpy.random.exponential(1/lamb)
    if modo_debug: print "\ttempo_chegada: [" + str(tempo_chegada) + "]"
    if modo_debug: print "--> Saiu de [gera_chegada_pacote_dados]"
    return tempo_chegada

# ********************************************************************
# Funcoes dos pacotes de voz
# ********************************************************************

# def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

# Retorna uma amostra aleatoria do numero de pacotes de voz durante um periodo de atividade
# (Amostra de uma distribuicao geometrica com media de 22 pacotes)
def gera_numero_pacotes_voz():
    if modo_debug: print "--> Entrou em [gera_numero_pacotes_voz]"
    numero_pacotes = numpy.random.geometric(float(1)/22)
    if modo_debug: print "\tnumero_pacotes: [" + str(numero_pacotes) + "]"
    if modo_debug: print "--> Saiu de [gera_numero_pacotes_voz]"
    return numero_pacotes

# Recebe numero de pacotes de voz de um periodo de atividade
# Retorna duracao em segundos do periodo de atividade
def calcula_duracao_periodo_atividade_voz(n_pacotes):
    if modo_debug: print "--> Entrou em [calcula_duracao_periodo_atividade_voz]"
    duracao = (0.016)*n_pacotes
    if modo_debug: print "\tduracao: [" + str(duracao) + "]"
    if modo_debug: print "--> Saiu de [calcula_duracao_periodo_atividade_voz]"
    return duracao

# Retorna uma amostra aleatoria da duracao do periodo de silencio dos pacotes de voz
# (Amostra de uma distribuicao exponencial com media de 650ms)
def calcula_duracao_periodo_silencio_voz():
    if modo_debug: print "--> Entrou em [calcula_duracao_periodo_silencio_voz]"
    duracao = numpy.random.exponential(media_periodo_silencio)
    if modo_debug: print "\tduracao: [" + str(duracao) + "]"
    if modo_debug: print "--> Saiu de [calcula_duracao_periodo_silencio_voz]"
    return duracao

# ********************************************************************
# Classes
# ********************************************************************

class pacote_dados:
    def __init__(self):
        self.tempo_chegada = gera_chegada_pacote_dados(lamb1)
        self.tamanho  = gera_tamanho_pacote_dados()
        self.tempo_servico = gera_tempo_servico_pacote_dados()

class evento_pacote_dados:       # Tipos: chegada, inicio_servico, fim_servico
    def __init__(self, tipo, tempo, pacote):
        self.tipo = tipo
        self.tempo = tempo
        self.pacote = pacote

# ********************************************************************
# Programa principal
# ********************************************************************

if modo_debug: print "--> Iniciou programa principal"


# Numero de chegadas de pacotes de dados que serao geradas
n = 99

# CRIANDO OS PACOTES
pacotes = []
for i in range(0, n): pacotes.append(pacote_dados())
# Ordena os pacotes por tempo de chegada
pacotes = sorted(pacotes, key=lambda pacote: pacote.tempo_chegada)
# Determina que o primeiro pacote de dados ira chegar em t=0 -- ver descricao do trabalho
pacotes[0].tempo_chegada = 0

# CRIANDO OS EVENTOS
eventos = []
quando_servidor_vai_liberar = 0
for i in range(0, n):
    # Cria o evento da chegada do pacote
    t_chegada = pacotes[i].tempo_chegada
    eventos.append(evento_pacote_dados("chegada", t_chegada, pacotes[i]))
    if t_chegada > quando_servidor_vai_liberar:
        # Se o servidor ja esta vazio (que ocorre quando esse pacote chega depois do servidor liberar)
        quando_servidor_vai_liberar = t_chegada
    # Cria o evento do pacote entrando no servico
    t_entrada = quando_servidor_vai_liberar
    eventos.append(evento_pacote_dados("inicio_servico", t_entrada, pacotes[i]))
    # Cria o evento do pacote terminando o servico, que sera apos o seu tempo de servico
    t_termino = t_entrada + pacotes[i].tempo_servico
    eventos.append(evento_pacote_dados("fim_servico", t_termino, pacotes[i]))
    # Registra o tempo em que o servidor estara liberado para o proximo pacote
    quando_servidor_vai_liberar = t_termino
# Ordena a lista de eventos por tempo de ocorrencia
eventos = sorted(eventos, key=lambda evento: evento.tempo)

# SIMULANDO A FILA
def printa_fila(t, capacidade, n_fila, n_servidor, rotulo):
    linha = ""
    asteriscos = ""
    for j in range(0, capacidade-n_fila): linha += "_"
    for j in range(0, n_fila): asteriscos += "x"
    servidor = ""
    if n_servidor==1: servidor = "x"
    else: servidor = "_"
    print "t = "+str(t)+"\t"+linha+asteriscos+"|"+servidor+" ("+rotulo+")"

n_fila = 0
n_servidor = 0
for evento in eventos:
    if evento.tipo == "chegada":
        n_fila+=1
        printa_fila(evento.tempo, n, n_fila, n_servidor, "chegada")
    if evento.tipo == "inicio_servico":
        n_fila-=1
        n_servidor+=1
        printa_fila(evento.tempo, n, n_fila, n_servidor, "inicio_servico")
    if evento.tipo == "fim_servico":
        n_servidor-=1
        printa_fila(evento.tempo, n, n_fila, n_servidor, "fim_servico")

if modo_debug: print "--> Terminou programa principal"