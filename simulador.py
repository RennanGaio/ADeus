import random as rd
import numpy.random

# ********************************************************************
# Declaracao de variaveis globais
# ********************************************************************

modo_debug = False
preempcao = True

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
ro1 = 0.7

# lambda1, taxa de chegada dos pacotes de dados
lamb1 = calcula_lambda(ro1, EX1)

# Tamanho fixo dos pacotes de voz, em bits
tamanho_pacote_voz = 512

# Tempo de servico fixo de um pacote de voz, em segundos
tempo_servico_pacote_voz = tamanho_pacote_voz/2097152

# Media da duracao do periodo de silencio dos pacotes de voz em segundos
media_periodo_silencio = 0.650

# Intervalo de tempo entre as chegadas de pacotes de voz num periodo de atividade
intervalo_entre_pacotes_voz = 0.016


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
    duracao = intervalo_entre_pacotes_voz * n_pacotes
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
        self.tempo_chegada = 0
        self.tamanho  = gera_tamanho_pacote_dados()
        self.tempo_servico = gera_tempo_servico_pacote_dados()
        self.tempo_entrou_em_servico = 0

class canal_voz:
    def __init__(self):
        self.tempo_prox_chegada = 0
        self.esta_em_atividade = False
        self.quantos_pacotes_faltam_nesse_periodo_atividade = 0

class pacote_voz:
    def __init__(self, t_chegada):
        self.tempo_chegada = t_chegada
        self.tempo_servico = tempo_servico_pacote_voz
        self.tempo_entrou_em_servico = 0

# ********************************************************************
# Programa principal
# ********************************************************************

def printa_fila(t, capacidade, n_fila, n_servidor, rotulo):
    linha = ""
    asteriscos = ""
    for j in range(0, capacidade-n_fila): linha += "_"
    for j in range(0, n_fila): asteriscos += "x"
    servidor = ""
    if n_servidor==1: servidor = "x"
    else: servidor = "_"
    print "t = "+str(t)+"\t"+linha+asteriscos+"|"+servidor+" ("+rotulo+")"

def printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz):
    print "inicio_fila_dados: " + str(inicio_fila_dados)
    print "fim_fila_dados: " + str(fim_fila_dados)
    print "n_fila_dados: " + str(n_fila_dados)
    print "inicio_fila_voz: " + str(inicio_fila_voz)
    print "fim_fila_voz: " + str(fim_fila_voz)
    print "n_fila_voz: " + str(n_fila_voz)

if modo_debug: print "--> Iniciou programa principal"

# CRIACAO DE UM VETOR CONTENDO TODAS AS CHEGADAS QUE OCORRERAO DO FUTURO
# Numero de chegadas de pacotes de dados que serao geradas
total_pacotes_dados = 99
# Cria as chegadas de pacotes de dados que irao acontecer
chegadas = []
t = 0
for i in range(0, total_pacotes_dados):
    chegadas.append(pacote_dados())
    chegadas[i].tempo_chegada = t + gera_chegada_pacote_dados(lamb1)
    t = chegadas[i].tempo_chegada
# Determina que a chegada do primeiro pacote ocorre em t=0 -- ver descricao do trabalho
chegadas[0].tempo_chegada = 0

# SIMULACAO DAS FILAS
# Numero de canais de voz
n_canais = 30
# Tempo passado (em segundos)
t = 0
n_pacotes_criados = 0
# Ponteiros para o inicio e fim das filas
# As filas sao listas onde eu vou colocar os pacotes, mas nunca vou tirar
# O ato de colocar um novo pacote na fila corresponde a concatenar o novo pacote a lista e a incrementar o indice de final da fila em 1
# O ato de tirar um pacote da fila corresponde a incrementar o indice de inicio da fila em 1
# O ato de colocar um pacote de volta ao inicio da fila (quando esse pacote teve seu servico interrompido) corresponde a decrementar o indice de inicio de fila em 1
# O numero de pacotes numa fila eh sempre igual a fim - inicio + 1
inicio_fila_dados = 0
fim_fila_dados = -1
inicio_fila_voz = 0
fim_fila_voz = -1
# Filas
fila_dados = []
fila_voz = []
# Contadores das filas
n_fila_dados = 0
n_fila_voz = 0
# Servidor
servidor = []
n_servidor = 0

# Gera a chegada do primeiro pacote de dados
# Como o sistema acaba de abrir, esse pacote ira passar direto pela fila e ira para o servidor
# Mas, mesmo assim, precisa primeiro inserir ele na fila, pois ele pode ser interrompido e ter que voltar pra fila
fila_dados.append(chegadas[n_pacotes_criados])
fim_fila_dados += 1 # Entrou na fila
n_pacotes_criados += 1
servidor.append(fila_dados[inicio_fila_dados])
inicio_fila_dados += 1 # Saiu da fila e entrou no servidor
n_servidor += 1
servidor[0].tempo_entrou_em_servico = t
printa_fila(0, 20, 0, 1, "DADOS")
# printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
# Cria os canais de voz
canais = []
for i in range(0, n_canais):
    canais.append(canal_voz())
    # Gera o periodo de silencio do canal
    canais[i].tempo_prox_chegada = calcula_duracao_periodo_silencio_voz()

# Enquanto ainda ha pacotes de dados para chegar ou para servir
while n_pacotes_criados < total_pacotes_dados or n_servidor > 0 or n_fila_dados > 0 or n_fila_voz > 0:

    raw_input ("Press enter to continue...")

    # Descobre qual eh o proximo evento que deve ser tratado
    # Se o menor tempo eh o termino do servico de algum pacote do servidor, ou o tempo de alguma chegada
    proximos_eventos = []
    # Pega o tempo das proximas chegadas de pacotes de voz
    for i in range(0, n_canais): proximos_eventos.append([canais[i].tempo_prox_chegada, "pacote_voz", i])
    # Pega o tempo da proxima chegada de pacote de dados
    print n_pacotes_criados
    if n_pacotes_criados < total_pacotes_dados: proximos_eventos.append([chegadas[n_pacotes_criados].tempo_chegada, "pacote_dados"])
    # Pega o tempo de termino do servico do pacote que esta no servidor
    if n_servidor > 0: proximos_eventos.append([servidor[0].tempo_entrou_em_servico + servidor[0].tempo_servico, "servico"])
    # Descobre o tempo que ocorrera o proximo evento
    tempo_prox_evento = 999999
    for i in range(0, len(proximos_eventos)):
        if proximos_eventos[i][0] < tempo_prox_evento:
            tempo_prox_evento = proximos_eventos[i][0]
            indice_prox_evento = i

    # Atualiza o contador do tempo
    t = tempo_prox_evento

    # Se o proximo evento eh a chegada de um pacote de voz
    if proximos_eventos[indice_prox_evento][1] == "pacote_voz":
        # Obtem o indice do canal que ira gerar uma chegada
        indice_canal = proximos_eventos[indice_prox_evento][2]
        # Verifica se esse eh o primeiro pacote do periodo de atividade desse canal
        if canais[indice_canal].esta_em_atividade == False:
            # Determina que agora este canal entrou em periodo de atividade
            canais[indice_canal].esta_em_atividade = True
            # Gera o numero de pacotes que esse canal ira transmitir durante esse periodo de atividade
            canais[indice_canal].quantos_pacotes_faltam_nesse_periodo_atividade = gera_numero_pacotes_voz()
            # Determina o tempo de chegada do proximo pacote de voz desse canal
            canais[indice_canal].tempo_prox_chegada = t + intervalo_entre_pacotes_voz
        else:
            # Se esse nao eh o primeiro pacote do periodo de atividade desse canal
            # Verifica se esse canal ainda tem outros pacotes para enviar nesse periodo de atividade
            if canais[indice_canal].quantos_pacotes_faltam_nesse_periodo_atividade > 0:
                # Determina o tempo de chegada do proximo pacote de voz desse canal
                canais[indice_canal].tempo_prox_chegada = t + intervalo_entre_pacotes_voz
            else:
                # Se o periodo de atividade desse canal acaba de terminar
                canais[indice_canal].esta_em_atividade = False
                # Gera o periodo de silencio desse canal
                canais[indice_canal].tempo_prox_chegada = t + calcula_duracao_periodo_silencio_voz()
        # Verifica se o novo pacote devera entrar direto no servidor ou se tera que esperar na fila
        if n_servidor == 0:
            servidor.append(pacote_voz(t))
            n_servidor += 1
            servidor[0].tempo_entrou_em_servico = t
            # Oficialmente, um pacote de voz acaba de entrar no servidor.
            printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - servico")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
        else:
            # Se nao ha preempcao, o pacote de voz ira para a fila invaravelmente.
            if preempcao == False:
                fila_voz.append(pacote_voz(t))
                fim_fila_voz += 1
                n_fila_voz += 1
                # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - fila")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                # Se ha preempcao, vamos checar se devemos interromper um pacote de dados
                if n_fila_voz == 0 and servidor[0].__class__ == pacote_dados:
                    # Se o pacote que esta sendo servido eh um pacote de dados
                    # Chuta ele do servidor
                    inicio_fila_dados -= 1
                    n_fila_dados += 1
                    del servidor[0]
                    servidor.append(pacote_voz(t))
                    servidor[0].tempo_entrou_em_servico = t
                    # Oficialmente, um pacote de voz acaba de entrar no servidor.
                    printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - preempcao")
                    printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
                else:
                    fila_voz.append(pacote_voz(t))
                    fim_fila_voz += 1
                    n_fila_voz += 1
                    # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                    printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - fila")
                    printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
                    print type(servidor[0])

        canais[indice_canal].quantos_pacotes_faltam_nesse_periodo_atividade -= 1
        
        # FALTA COISA AINDA: SE TEM QUE INTERROMPER UM PACOTE DE DADOS...

    # Se o proximo evento eh a chegada de um pacote de dados
    elif proximos_eventos[indice_prox_evento][1] == "pacote_dados":
        # Verifica se o novo pacote devera entrar direto no servidor ou se tera que esperar na fila
        if n_servidor == 0:
            fila_dados.append(chegadas[n_pacotes_criados])
            fim_fila_dados += 1 # Inserindo o pacote na fila mesmo assim, pois ele pode ser interrompido e ter que voltar pra fila
            servidor.append(chegadas[n_pacotes_criados])
            inicio_fila_dados += 1 # Agora, tirando da fila e pondo no servidor
            n_pacotes_criados += 1
            n_servidor += 1
            servidor[0].tempo_entrou_em_servico = t
            # Oficialmente, um pacote de dados acaba de entrar no servidor.
            printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - servico")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
        else:
            fila_dados.append(chegadas[n_pacotes_criados])
            n_pacotes_criados += 1
            fim_fila_dados += 1
            n_fila_dados += 1
            # Oficialmente, um pacote de dados acaba de entrar na fila de dados.
            printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - fila")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

    # Se o proximo evento eh o termino de um servico
    elif proximos_eventos[indice_prox_evento][1] == "servico":
        # Retira o pacote atual do servidor
        del servidor[0]
        n_servidor -= 1
        # Verifica se tem pacotes de voz na fila de voz
        if n_fila_voz > 0:
            # Coloca o proximo pacote de voz no servidor
            servidor.append(fila_voz[inicio_fila_voz])
            inicio_fila_voz += 1
            n_fila_voz -= 1
            n_servidor += 1
            servidor[0].tempo_entrou_em_servico = t
            # Oficialmente, um pacote de voz acaba de entrar em servico
            printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - servico")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
        # Verifica se tem pacotes de dados na fila de dados
        elif n_fila_dados > 0:
            # Coloca o proximo pacote de dados no servidor
            servidor.append(fila_dados[inicio_fila_dados])
            inicio_fila_dados += 1
            n_fila_dados -= 1
            n_servidor += 1
            servidor[0].tempo_entrou_em_servico = t
            # Oficialmente, um pacote de dados acaba de entrar em servico
            printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - servico")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
        else:
            # As duas filas estao vazias
            printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - vazia")
            printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - vazia")
            printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

if modo_debug: print "--> Terminou programa principal"