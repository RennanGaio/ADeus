import random as rd
import numpy.random
from scipy import stats
import math

# ********************************************************************
# Declaracao de variaveis globais
# ********************************************************************

preempcao = True
numero_rodadas = 5
numero_fregueses = 5000
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
ro1 = 0.7

# lambda1, taxa de chegada dos pacotes de dados
lamb1 = calcula_lambda(ro1, EX1)

# Tamanho fixo dos pacotes de voz, em bits
tamanho_pacote_voz = float(512)

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
    # 0.3 de chance de indice=1, 0.1 de chance de indice=2, e assim por diante
    indice=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
    if indice==4:
        tamanho=numpy.random.randint(64,1500)
    elif indice==1:
        tamanho=64
    elif indice==2:
        tamanho=512
    else:
        tamanho=1500
    return tamanho

# Retorna uma amostra aleatoria do tempo de servico em segundos de um pacote de dados
# (Amostra da variavel aleatoria X1 - ver descricao do trabalho)
def gera_tempo_servico_pacote_dados():
    tamanho = gera_tamanho_pacote_dados()
    # Converte o tamanho de bytes para bits (multiplicando por 8), e divide por 2Mbps para obter o tempo de transmissao
    tempo_servico = float(tamanho*8)/2097152
    return tempo_servico

# Retorna uma amostra aleatoria de uma chegada de um pacote de dados em segundos
# (Amostra de uma variavel exponencial com taxa lamb = ro/E[X1])
def gera_chegada_pacote_dados(lamb):
    tempo_chegada = numpy.random.exponential(1/lamb)
    return tempo_chegada

# ********************************************************************
# Funcoes dos pacotes de voz
# ********************************************************************

# def chegada_pacote_voz(intervalo_deterministico=0.016, tamanho_pacote=512):

# Retorna uma amostra aleatoria do numero de pacotes de voz durante um periodo de atividade
# (Amostra de uma distribuicao geometrica com media de 22 pacotes)
def gera_numero_pacotes_voz():
    numero_pacotes = numpy.random.geometric(float(1)/22)
    return numero_pacotes

# Recebe numero de pacotes de voz de um periodo de atividade
# Retorna duracao em segundos do periodo de atividade
def calcula_duracao_periodo_atividade_voz(n_pacotes):
    duracao = intervalo_entre_pacotes_voz * n_pacotes
    return duracao

# Retorna uma amostra aleatoria da duracao do periodo de silencio dos pacotes de voz
# (Amostra de uma distribuicao exponencial com media de 650ms)
def calcula_duracao_periodo_silencio_voz():
    duracao = numpy.random.exponential(media_periodo_silencio)
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
        self.tempo_deixou_servico = 0
        self.tempo_ultima_vez_entrou_na_fila = 0

class canal_voz:
    def __init__(self):
        self.tempo_prox_chegada = 0
        self.esta_em_atividade = False
        self.quantos_pacotes_faltam_nesse_periodo_atividade = 0
        # Os proximos dois campos sao usados para gerar as estatisticas E[delta] e V(delta) -- ver descricao do trabalho
        self.tempo_inicio_servico_ultimo_pacote = -1 # Igual a -1 quando esse canal esta em silencio
        self.numero_intervalos_entre_inicios_servico = 0 # Numero total de intervalos entre transmissoes que foram medidos

class pacote_voz:
    def __init__(self, t_chegada):
        self.tempo_chegada = t_chegada
        self.tempo_servico = tempo_servico_pacote_voz
        self.tempo_entrou_em_servico = 0
        self.tempo_deixou_servico = 0

# ********************************************************************
# Funcoes do programa principal
# ********************************************************************

# Imprime na tela um pequeno desenho de uma fila
def printa_fila(t, capacidade, n_fila, n_servidor, servidor, rotulo):
    if modo_debug:
        simbolo_servidor = ""
        if n_servidor == 1 and servidor[0].__class__ == pacote_voz: simbolo_servidor = "V"
        elif n_servidor == 1 and servidor[0].__class__ == pacote_dados: simbolo_servidor = "D"
        else: simbolo_servidor = "_"
        linha = ""
        asteriscos = ""
        for j in range(0, capacidade-n_fila): linha += "_"
        for j in range(0, n_fila): asteriscos += "x"
        servidor = ""
        print "t = "+str(t)+"\t"+linha+asteriscos+"|"+simbolo_servidor+" ("+rotulo+")"

# Imprime na tela os valores correntes dos indices das filas
def printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz):
    if modo_debug:
        print "inicio_fila_dados: " + str(inicio_fila_dados)
        print "fim_fila_dados: " + str(fim_fila_dados)
        print "n_fila_dados: " + str(n_fila_dados)
        print "inicio_fila_voz: " + str(inicio_fila_voz)
        print "fim_fila_voz: " + str(fim_fila_voz)
        print "n_fila_voz: " + str(n_fila_voz)

# Descobre qual eh o proximo evento que deve ser tratado
# Se o menor tempo eh o termino do servico de algum pacote do servidor, ou o tempo de alguma chegada
def descobre_proximo_evento(n_canais, canais, n_pacotes_dados_criados, n_pacotes_dados_criados_fora_fase_transiente, total_pacotes_dados, chegadas, n_servidor, servidor):
    # Descobre qual eh o proximo evento que deve ser tratado
    # Se o menor tempo eh o termino do servico de algum pacote do servidor, ou o tempo de alguma chegada
    proximos_eventos = []
    # Pega o tempo das proximas chegadas de pacotes de voz
    for i in range(0, n_canais): proximos_eventos.append([canais[i].tempo_prox_chegada, "pacote_voz", i])
    # Pega o tempo da proxima chegada de pacote de dados
    if n_pacotes_dados_criados_fora_fase_transiente < total_pacotes_dados: proximos_eventos.append([chegadas[n_pacotes_dados_criados-1].tempo_chegada, "pacote_dados"])
    # Pega o tempo de termino do servico do pacote que esta no servidor
    if n_servidor > 0: proximos_eventos.append([servidor[0].tempo_entrou_em_servico + servidor[0].tempo_servico, "servico"])
    # Descobre o tempo que ocorrera o proximo evento
    tempo_prox_evento = 999999
    for i in range(0, len(proximos_eventos)):
        if proximos_eventos[i][0] < tempo_prox_evento:
            tempo_prox_evento = proximos_eventos[i][0]
            indice_prox_evento = i
    return tempo_prox_evento, proximos_eventos, indice_prox_evento

# Executa uma rodada de simulacao
# Parametros:
#       Numero de fregueses (quantidade total de pacotes de dados a serem transmitidos),
#       Fase transiente (quantidade de pacotes de dados a serem transmitidos durante a fase transiente, deve ser menor do que a quantidade total de pacotes a serem transmitidos)
# Retorno: Um dicionario de dados contendo as estatisticas referentes a rodada corrente de simulacao
#       E[T1k]
#       E[W1k]
#       E[X1k]
#       E[Nq1k]
#       E[T2k]
#       E[W2k]
#       E[Nq2k]
#       E[deltak]
#       V(deltak)
# -- ver descricao do trabalho
def simulacao(total_pacotes_dados):
    # Valida os parametros
    if total_pacotes_dados <= 0:
        print "Erro: Numero de fregueses menor que um"
        exit()

    # Declaracao do dicionario de dados que sera retornado
    estatisticas = {
    "E[T1k]":0,
    "E[W1k]":0,
    "E[X1k]":0,
    "E[Nq1k]":0,
    "E[T2k]":0,
    "E[W2k]":0,
    "E[Nq2k]":0,
    "E[deltak]":0,
    "V[deltak]":0
    }

    #criacao de uma lista com tempos de intervalos entre pacotes de voz que sera usada para calcular V[deltak]
    lista_intervalo_chegada_voz=[]

    # Vetor que ira armazenar as chegadas dos pacotes de dados. Uma chegada por vez sera gerada
    # Cria a chegada do primeiro pacote, que ocorre em t=0 -- ver descricao do trabalho
    chegadas = []
    chegadas.append(pacote_dados())
    chegadas[0].tempo_chegada = 0

    # SIMULACAO DAS FILAS
    # Numero de canais de voz
    n_canais = 30
    # Tempo passado (em segundos)
    t = 0
    # Tempo que ocorreu a ultima iteracao do simulador. Usado para calcular E[Nq1] e E[Nq2] pelo metodo das areas
    t_anterior = 0
    # Numero de pacotes de dados ja criados. Usado para conhecer o progresso da rodada
    n_pacotes_dados_criados = 1
    # Numero total de pacotes de dados criados durante a fase transiente
    n_pacotes_dados_criados_fase_transiente = -1
    # Numero de pacotes de dados criados fora da fase transiente
    n_pacotes_dados_criados_fora_fase_transiente = 0
    # Numero total de pacotes de voz criados
    n_pacotes_voz_criados = 0
    # Numero de pacotes de voz criados fora da fase transiente
    n_pacotes_voz_criados_fora_da_fase_transiente = 0
    n_pacotes_voz_criados_fase_transiente = 0
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

    # Fase transiente
    fase_transiente = True
    # Tempo de espera de um dado pacote de dados. Calculado durante a fase transiente.
    # Usado para estimar a fase transiente quando a disciplina usada eh a nao preemptiva
    tempo_espera_pacote_dados_atual = -1
    # Variaveis usadas para calcular a media amostral e a variancia amostral do tempo de espera dos pacotes de dados
    somatorio_tempos_espera_pacotes_dados = 0
    somatorio_tempos_espera_quadrado_pacotes_dados = 0
    media_tempos_espera_pacotes_dados = 0
    primeiro_termo_variancia_tempos_espera_pacotes_dados = 0
    segundo_termo_variancia_tempos_espera_pacotes_dados = 0
    variancia_tempos_espera_pacotes_dados = 0
    # Recolheremos 10 amostras da variancia do tempo de espera dos pacotes de dados
    # Essas 10 amostras serao as 10 ultimas coletas da variancia
    # Isso sera usado para avaliar a variacao do tempo de espera dos pacotes de dados, e, assim, estimar o fim da fase transiente
    amostras_variancia_tempos_espera_pacotes_dados = []
    n_amostras_variancia_tempos_espera_pacotes_dados = 0
    n_max_amostras_variancia_tempos_espera_pacotes_dados = 10

    # Tempo de espera de um dado pacote de voz. Calculado durante a fase transiente.
    # Usado para estimar a fase transiente quando a disciplina usada eh a preemptiva
    tempo_espera_pacote_voz_atual = -1
    # Variaveis usadas para calcular a media amostral e a variancia amostral do tempo de espera dos pacotes de voz
    somatorio_tempos_espera_pacotes_voz = 0
    somatorio_tempos_espera_quadrado_pacotes_voz = 0
    media_tempos_espera_pacotes_voz = 0
    primeiro_termo_variancia_tempos_espera_pacotes_voz = 0
    segundo_termo_variancia_tempos_espera_pacotes_voz = 0
    variancia_tempos_espera_pacotes_voz = 0
    # Recolheremos 10 amostras da variancia do tempo de espera dos pacotes de voz
    # Essas 10 amostras serao as 10 ultimas coletas da variancia
    # Isso sera usado para avaliar a variacao do tempo de espera dos pacotes de voz, e, assim, estimar o fim da fase transiente
    amostras_variancia_tempos_espera_pacotes_voz = []
    n_amostras_variancia_tempos_espera_pacotes_voz = 0
    n_max_amostras_variancia_tempos_espera_pacotes_voz = 10

    n_atual_amostras = 0

    # Insere na fila o primeiro pacote de dados
    # Como o sistema acaba de abrir, esse pacote ira passar direto pela fila e ira para o servidor
    # Mas, mesmo assim, precisa primeiro inserir ele na fila, pois ele pode ser interrompido e ter que voltar pra fila
    fila_dados.append(chegadas[n_pacotes_dados_criados-1])
    fim_fila_dados += 1 # Entrou na fila
    fila_dados[fim_fila_dados].tempo_ultima_vez_entrou_na_fila = t
    # n_pacotes_dados_criados += 1
    servidor.append(fila_dados[inicio_fila_dados])
    inicio_fila_dados += 1 # Saiu da fila e entrou no servidor
    n_servidor += 1
    servidor[0].tempo_entrou_em_servico = t
    printa_fila(0, 20, 0, 1, servidor, "DADOS")
    printa_fila(0, 20, 0, 1, servidor, "VOZ")
    # printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
    # Cria os canais de voz
    canais = []
    for i in range(0, n_canais):
        canais.append(canal_voz())
        # Gera o periodo de silencio do canal
        canais[i].tempo_prox_chegada = calcula_duracao_periodo_silencio_voz()

    # Enquanto ainda ha pacotes de dados para chegar ou pacotes de qualquer tipo para servir
    while n_pacotes_dados_criados_fora_fase_transiente < total_pacotes_dados:
        # Descobre qual eh o proximo evento que deve ser tratado
        # Se o menor tempo eh o termino do servico de algum pacote do servidor, ou o tempo de alguma chegada
        tempo_prox_evento, proximos_eventos, indice_prox_evento = descobre_proximo_evento(n_canais, canais, n_pacotes_dados_criados, n_pacotes_dados_criados_fora_fase_transiente, total_pacotes_dados, chegadas, n_servidor, servidor)

        # Atualiza o contador do tempo
        t_anterior = t
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
                    # O periodo de silencio somente se inicia 16ms apos a chegada do ultimo pacote do periodo de atividade
                    canais[indice_canal].tempo_prox_chegada = t + calcula_duracao_periodo_silencio_voz() + intervalo_entre_pacotes_voz
            # Verifica se o novo pacote devera entrar direto no servidor ou se tera que esperar na fila
            if n_servidor == 0:
                servidor.append(pacote_voz(t))
                n_servidor += 1
                servidor[0].tempo_entrou_em_servico = t
                # Verifica se deve gerar as estatisticas sobre esse pacote
                if fase_transiente == False:
                    n_pacotes_voz_criados_fora_da_fase_transiente += 1
                    if canais[indice_canal].tempo_inicio_servico_ultimo_pacote != -1:
                        # Atualiza o nosso E[deltak] e lista de intervalos
                        estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                        lista_intervalo_chegada_voz.append((t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote))
                        canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                    if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                    else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
                # Oficialmente, um pacote de voz acaba de entrar no servidor.
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - servico")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                # Se nao ha preempcao, o pacote de voz ira para a fila invariavelmente.
                if preempcao == False:
                    fila_voz.append(pacote_voz(t))
                    if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                    fim_fila_voz += 1
                    n_fila_voz += 1
                    # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                    printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS")
                    printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - fila")
                    printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
                else:
                    # Se ha preempcao, vamos checar se devemos interromper um pacote de dados
                    if n_fila_voz == 0 and servidor[0].__class__ == pacote_dados:
                        # Se o pacote que esta sendo servido eh um pacote de dados
                        # Verifica se deve gerar as estatisticas sobre o pacote que vai ser interrompido e sobre o pacote que vai entrar em servico
                        if fase_transiente == False:
                            # Atualiza o nosso E[X1k]
                            estatisticas["E[X1k]"] += (t - servidor[0].tempo_entrou_em_servico)
                            if canais[indice_canal].tempo_inicio_servico_ultimo_pacote != -1:
                                # Atualiza o nosso E[deltak] e lista de intervalos
                                estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                                lista_intervalo_chegada_voz.append((t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote))
                                canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                            if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                            else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
                        # Chuta ele do servidor
                        inicio_fila_dados -= 1
                        n_fila_dados += 1
                        # Anotamos o tempo em que o pacote de dados voltou para a fila apos ser chutado do servidor
                        # Isso eh necessario para gerar a estatistica de E[W1]
                        fila_dados[inicio_fila_dados].tempo_ultima_vez_entrou_na_fila = t
                        del servidor[0]
                        servidor.append(pacote_voz(t))
                        if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                        servidor[0].tempo_entrou_em_servico = t
                        # Oficialmente, um pacote de voz acaba de entrar no servidor.
                        printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS")
                        printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - preempcao")
                        printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
                    else:
                        fila_voz.append(pacote_voz(t))
                        if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                        fim_fila_voz += 1
                        n_fila_voz += 1
                        # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                        printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS")
                        printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - fila")
                        printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

            canais[indice_canal].quantos_pacotes_faltam_nesse_periodo_atividade -= 1
            n_pacotes_voz_criados += 1

        # Se o proximo evento eh a chegada de um pacote de dados
        elif proximos_eventos[indice_prox_evento][1] == "pacote_dados":
            # Verifica se o novo pacote devera entrar direto no servidor ou se tera que esperar na fila
            if n_servidor == 0:
                fila_dados.append(chegadas[n_pacotes_dados_criados-1])
                fim_fila_dados += 1 # Inserindo o pacote na fila mesmo assim, pois ele pode ser interrompido e ter que voltar pra fila
                servidor.append(chegadas[n_pacotes_dados_criados-1])
                inicio_fila_dados += 1 # Agora, tirando da fila e pondo no servidor
                n_servidor += 1
                servidor[0].tempo_entrou_em_servico = t
                # Oficialmente, um pacote de dados acaba de entrar no servidor.
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS - servico")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                fila_dados.append(chegadas[n_pacotes_dados_criados-1])
                fim_fila_dados += 1
                n_fila_dados += 1
                # Para gerar a estatistica de E[W1], precisamos anotar o tempo em que esse pacote entrou na fila separadamente
                # do tempo em que ele chegou, pois esse pacote pode ser interrompido.
                fila_dados[fim_fila_dados].tempo_ultima_vez_entrou_na_fila = t
                # Oficialmente, um pacote de dados acaba de entrar na fila de dados.
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS - fila")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            # Gera a chegada do proximo pacote de dados
            chegadas.append(pacote_dados())
            n_pacotes_dados_criados += 1
            if fase_transiente == False: n_pacotes_dados_criados_fora_fase_transiente += 1
            chegadas[n_pacotes_dados_criados-1].tempo_chegada = t + gera_chegada_pacote_dados(lamb1)

        # Se o proximo evento eh o termino de um servico
        elif proximos_eventos[indice_prox_evento][1] == "servico":
            # Verifica se deve gerar as estatisticas sobre esse pacote
            if fase_transiente == False:
                # Anota o tempo em que esse pacote deixou o servico, para o calculo de E[T1], E[T2], e de E[X1]
                servidor[0].tempo_deixou_servico = t
                if servidor[0].__class__ == pacote_dados:
                    # Atualiza o nosso E[T1k]
                    estatisticas["E[T1k]"] += (servidor[0].tempo_deixou_servico - servidor[0].tempo_chegada)
                    # Atualiza o nosso E[X1k]]
                    estatisticas["E[X1k]"] += (servidor[0].tempo_deixou_servico - servidor[0].tempo_entrou_em_servico)
                elif servidor[0].__class__ == pacote_voz:
                    # Atualiza o nosso E[T2k]
                    estatisticas["E[T2k]"] += (servidor[0].tempo_deixou_servico - servidor[0].tempo_chegada)
            # Se estiver na fase transiente, avalia a condicao para o seu termino
            # Caso nao preemptivo: medir a variacao do tempo de espera dos pacotes de dados
            # Caso preemptivo: medir a variacao do tempo de espera dos pacotes de voz
            if fase_transiente == True:
                if preempcao == False and servidor[0].__class__ == pacote_dados:
                    tempo_espera_pacote_dados_atual = servidor[0].tempo_entrou_em_servico - servidor[0].tempo_chegada
                    media_tempos_espera_pacotes_dados += tempo_espera_pacote_dados_atual
                    n_atual_amostras += 1
                    if n_atual_amostras == 100:
                        media_tempos_espera_pacotes_dados = media_tempos_espera_pacotes_dados / n_atual_amostras
                        if ro1 == 0.1:
                            if media_tempos_espera_pacotes_voz < 0.0005:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.2:
                            if media_tempos_espera_pacotes_voz < 0.0009:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.3:
                            if media_tempos_espera_pacotes_voz < 0.0015:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.4:
                            if media_tempos_espera_pacotes_voz < 0.0025:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.5:
                            if media_tempos_espera_pacotes_voz < 0.0045:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.6:
                            if media_tempos_espera_pacotes_voz < 0.007:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        elif ro1 == 0.7:
                            if media_tempos_espera_pacotes_voz < 0.013:
                                fase_transiente = False
                                n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                                n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        media_tempos_espera_pacotes_voz = 0
                        n_atual_amostras = 0

                if preempcao == True and servidor[0].__class__ == pacote_voz:
                    tempo_espera_pacote_voz_atual = servidor[0].tempo_entrou_em_servico - servidor[0].tempo_chegada
                    media_tempos_espera_pacotes_voz += tempo_espera_pacote_voz_atual
                    n_atual_amostras += 1
                    if n_atual_amostras == 100:
                        media_tempos_espera_pacotes_voz = media_tempos_espera_pacotes_voz / n_atual_amostras
                        if media_tempos_espera_pacotes_voz < 10**(-5):
                            fase_transiente = False
                            n_pacotes_dados_criados_fase_transiente = n_pacotes_dados_criados
                            n_pacotes_voz_criados_fase_transiente = n_pacotes_voz_criados
                        media_tempos_espera_pacotes_voz = 0
                        n_atual_amostras = 0

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
                # Verifica se deve gerar as estatisticas sobre o pacote
                if fase_transiente == False:
                    # Atualiza o nosso E[W2k]
                    estatisticas["E[W2k]"] += (servidor[0].tempo_entrou_em_servico - servidor[0].tempo_chegada)
                    if canais[indice_canal].tempo_inicio_servico_ultimo_pacote != -1:
                        # Atualiza o nosso E[deltak] e lista de intervalos
                        estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                        lista_intervalo_chegada_voz.append((t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote))
                        canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                    if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                    else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
                # Oficialmente, um pacote de voz acaba de entrar em servico
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - servico")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            # Verifica se tem pacotes de dados na fila de dados
            elif n_fila_dados > 0:
                # Coloca o proximo pacote de dados no servidor
                servidor.append(fila_dados[inicio_fila_dados])
                inicio_fila_dados += 1
                n_fila_dados -= 1
                n_servidor += 1
                servidor[0].tempo_entrou_em_servico = t
                # Verifica se deve gerar as estatisticas sobre o pacote
                if fase_transiente == False:
                    # Atualiza o nosso E[W1k]
                    estatisticas["E[W1k]"] += (servidor[0].tempo_entrou_em_servico - servidor[0].tempo_ultima_vez_entrou_na_fila)
                # Oficialmente, um pacote de dados acaba de entrar em servico
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS - servico")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                # As duas filas estao vazias
                printa_fila(t, 20, n_fila_dados, n_servidor, servidor, "DADOS - vazia")
                printa_fila(t, 20, n_fila_voz, n_servidor, servidor, "VOZ - vazia")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

        # Atualiza os nossos E[Nq1k] e E[Nq2k] pelo metodo das areas
        if fase_transiente == False:
            delta_tempo = t - t_anterior
            estatisticas["E[Nq1k]"] += (n_fila_dados * delta_tempo)
            estatisticas["E[Nq2k]"] += (n_fila_voz * delta_tempo)

    # Fim - while
    if fase_transiente == True:
        print "Erro: simulacao nunca saiu da fase transiente"
        exit()

    print "[DADOS]"
    print "\tNumero total de pacotes de dados: [" + str(n_pacotes_dados_criados) + "]"
    print "\tNumero de pacotes de dados na fase transiente: [" + str(n_pacotes_dados_criados_fase_transiente) + "]"
    print "\tNumero de pacotes de dados fora da fase transiente: [" + str(n_pacotes_dados_criados - n_pacotes_dados_criados_fase_transiente) + "]"
    print "[VOZ]"
    print "\tNumero total de pacotes de voz: [" + str(n_pacotes_voz_criados) + "]"
    print "\tNumero de pacotes de voz na fase transiente: [" + str(n_pacotes_voz_criados_fase_transiente) + "]"
    print "\tNumero de pacotes de voz fora da fase transiente: [" + str(n_pacotes_voz_criados_fora_da_fase_transiente) + "]"

    # Termina de calcular os nossos E[T1k], E[T2k], E[X1k], E[W1k], E[Nq1k], E[Nq2k], E[deltak] e V[deltak]
    estatisticas["E[T1k]"] = estatisticas["E[T1k]"] / (n_pacotes_dados_criados_fora_fase_transiente)
    estatisticas["E[T2k]"] = estatisticas["E[T2k]"] / n_pacotes_voz_criados_fora_da_fase_transiente
    estatisticas["E[X1k]"] = estatisticas["E[X1k]"] / (n_pacotes_dados_criados_fora_fase_transiente)
    estatisticas["E[W1k]"] = estatisticas["E[W1k]"] / (n_pacotes_dados_criados_fora_fase_transiente)
    estatisticas["E[W2k]"] = estatisticas["E[W2k]"] / n_pacotes_voz_criados_fora_da_fase_transiente
    estatisticas["E[Nq1k]"] = estatisticas["E[Nq1k]"] / t
    estatisticas["E[Nq2k]"] = estatisticas["E[Nq2k]"] / t
    total_intervalos = 0
    for i in range(0, n_canais): total_intervalos += canais[i].numero_intervalos_entre_inicios_servico
    estatisticas["E[deltak]"] = estatisticas["E[deltak]"] / total_intervalos
    #calculo final de V[deltak] usando o valor final de E[deltak] e a lista de intervalos entre chegadas
    temp=0
    for i in range(0, len(lista_intervalo_chegada_voz)):
        temp+=(estatisticas["E[deltak]"]-lista_intervalo_chegada_voz[i])**2
    estatisticas["V[deltak]"]=temp/(total_intervalos-1)

    return estatisticas

# ********************************************************************
# Programa principal
# ********************************************************************

# Calculo incremental do desvio padrao utilizado:
# desvio padrao = somatorio{amostra**2}/(n-1) - (somatorio{amostra}**2)/n*(n-1)
#                primeiro termo /\                   segundo termo /\

# Dicionarios que irao guardar os valores correntes dos somatorios descritos acima
somatorio_primeiro_termo_desvio_padrao = {
    "V[T1]":0,
    "V[W1]":0,
    "V[X1]":0,
    "V[Nq1]":0,
    "V[T2]":0,
    "V[W2]":0,
    "V[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}
somatorio_segundo_termo_desvio_padrao = {
    "V[T1]":0,
    "V[W1]":0,
    "V[X1]":0,
    "V[Nq1]":0,
    "V[T2]":0,
    "V[W2]":0,
    "V[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

# Dicionario que ira guardar o primeiro termo do calculo do desvio padrao das estatisticas, para o calculo dos ICs
primeiro_termo_desvio_padrao = {
    "V[T1]":0,
    "V[W1]":0,
    "V[X1]":0,
    "V[Nq1]":0,
    "V[T2]":0,
    "V[W2]":0,
    "V[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

# Dicionario que ira guardar o segundo termo do calculo do desvio padrao das estatisticas, para o calculo dos ICs
segundo_termo_desvio_padrao = {
    "V[T1]":0,
    "V[W1]":0,
    "V[X1]":0,
    "V[Nq1]":0,
    "V[T2]":0,
    "V[W2]":0,
    "V[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

# Dicionario que ira guardar o desvio padrao das estatisticas, para o calculo dos ICs
desvio_padrao = {
    "V[T1]":0,
    "V[W1]":0,
    "V[X1]":0,
    "V[Nq1]":0,
    "V[T2]":0,
    "V[W2]":0,
    "V[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

# Dicionarios que irao guardar os limites inferior e superior dos ICs
IC_limite_inferior = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

IC_limite_superior = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
}

# Dicionario que guarda a proporcao entre a largura e o ponto medio de cada IC
proporcoes = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0
}

# Estatisticas globais sao as que dizem respeito a todas as rodadas de simulacao
somatorio_estatisticas_globais = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
    }
estatisticas_globais = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0,
    "E[delta]":0,
    "V[delta]":0
    }

termino = False
i = 1
um_menos_alfa_sobre_dois = 0.95 # O nosso alfa vale 0.1, pois o IC deve ter precisao de 90%
while termino == False:
    # Executa uma rodada de simulacao
    estatisticas_rodada = simulacao(numero_fregueses)
    print "RODADA: [" + str(i) + "]"
    print "[DADOS]"
    print "\tE[T1k] ---------->  " + str(estatisticas_rodada["E[T1k]"])
    print "\tE[X1k] ---------->  " + str(estatisticas_rodada["E[X1k]"])
    print "\tE[W1k] ---------->  " + str(estatisticas_rodada["E[W1k]"])
    print "\tE[Nq1k]---------->  " + str(estatisticas_rodada["E[Nq1k]"])
    print "[VOZ]"
    print "\tE[T2k] ---------->  " + str(estatisticas_rodada["E[T2k]"])
    print "\tE[X2k] ---------->  " + str(tempo_servico_pacote_voz)
    print "\tE[W2k] ---------->  " + str(estatisticas_rodada["E[W2k]"])
    print "\tE[Nq2k]---------->  " + str(estatisticas_rodada["E[Nq2k]"])
    print "\tE[deltak]-------->  " + str(estatisticas_rodada["E[deltak]"])
    print "\tV[deltak]-------->  " + str(estatisticas_rodada["V[deltak]"])
    print "~~~~~~~~~~~~~"

    # Atualiza as estatisticas globais
    somatorio_estatisticas_globais["E[T1]"] += estatisticas_rodada["E[T1k]"]
    somatorio_estatisticas_globais["E[W1]"] += estatisticas_rodada["E[W1k]"]
    somatorio_estatisticas_globais["E[X1]"] += estatisticas_rodada["E[X1k]"]
    somatorio_estatisticas_globais["E[T2]"] += estatisticas_rodada["E[T2k]"]
    somatorio_estatisticas_globais["E[W2]"] += estatisticas_rodada["E[W2k]"]
    somatorio_estatisticas_globais["E[Nq1]"] += estatisticas_rodada["E[Nq1k]"]
    somatorio_estatisticas_globais["E[Nq2]"] += estatisticas_rodada["E[Nq2k]"]
    somatorio_estatisticas_globais["E[delta]"] += estatisticas_rodada["E[deltak]"]
    somatorio_estatisticas_globais["V[delta]"] += estatisticas_rodada["V[deltak]"]

    # Atualiza o calculo do desvio padrao das estatisticas
    somatorio_primeiro_termo_desvio_padrao["V[T1]"] += (estatisticas_rodada["E[T1k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[T1]"] += estatisticas_rodada["E[T1k]"]
    somatorio_primeiro_termo_desvio_padrao["V[W1]"] += (estatisticas_rodada["E[W1k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[W1]"] += estatisticas_rodada["E[W1k]"]
    somatorio_primeiro_termo_desvio_padrao["V[X1]"] += (estatisticas_rodada["E[X1k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[X1]"] += estatisticas_rodada["E[X1k]"]
    somatorio_primeiro_termo_desvio_padrao["V[Nq1]"] += (estatisticas_rodada["E[Nq1k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[Nq1]"] += estatisticas_rodada["E[Nq1k]"]
    somatorio_primeiro_termo_desvio_padrao["V[T2]"] += (estatisticas_rodada["E[T2k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[T2]"] += estatisticas_rodada["E[T2k]"]
    somatorio_primeiro_termo_desvio_padrao["V[W2]"] += (estatisticas_rodada["E[W2k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[W2]"] += estatisticas_rodada["E[W2k]"]
    somatorio_primeiro_termo_desvio_padrao["V[Nq2]"] += (estatisticas_rodada["E[Nq2k]"])**2
    somatorio_segundo_termo_desvio_padrao["V[Nq2]"] += estatisticas_rodada["E[Nq2k]"]
    somatorio_primeiro_termo_desvio_padrao["E[delta]"] += (estatisticas_rodada["E[deltak]"])**2
    somatorio_segundo_termo_desvio_padrao["E[delta]"] += estatisticas_rodada["E[deltak]"]
    somatorio_primeiro_termo_desvio_padrao["V[delta]"] += (estatisticas_rodada["V[deltak]"])**2
    somatorio_segundo_termo_desvio_padrao["V[delta]"] += estatisticas_rodada["V[deltak]"]

    # Caso tenha atingido o numero desejado de rodadas, comeca a calcular os ICs e a medir a qualidade das simulacoes
    # Se determinar que a qualidade ainda nao esta boa, continua a executar
    if (i >= numero_rodadas):
        # Para verificar se ja pode parar de executar as rodadas, termina o calculo dos ICs

        # Variaveis para economizar tempo
        raiz_i = math.sqrt(i)
        i_vezes_i_menos_um = i * (i - 1)

        # Termina o calculo do desvio padrao das estatisticas
        for chave in primeiro_termo_desvio_padrao:
            primeiro_termo_desvio_padrao[chave] = somatorio_primeiro_termo_desvio_padrao[chave] / (i-1)
            segundo_termo_desvio_padrao[chave] = ((somatorio_segundo_termo_desvio_padrao[chave])**2) / (i_vezes_i_menos_um)
            desvio_padrao[chave] = math.sqrt(primeiro_termo_desvio_padrao[chave] - segundo_termo_desvio_padrao[chave])

        # Termina de calcular as estatisticas globais
        for chave in estatisticas_globais:
            estatisticas_globais[chave] = somatorio_estatisticas_globais[chave] / i

        print "ESTATISTICAS GLOBAIS:"
        print "[DADOS]"
        print "\tE[T1] ---------->  " + str(estatisticas_globais["E[T1]"])
        print "\tE[X1] ---------->  " + str(estatisticas_globais["E[X1]"])
        print "\tE[W1] ---------->  " + str(estatisticas_globais["E[W1]"])
        print "\tE[Nq1]---------->  " + str(estatisticas_globais["E[Nq1]"])
        print "[VOZ]"
        print "\tE[T2] ---------->  " + str(estatisticas_globais["E[T2]"])
        print "\tE[W2] ---------->  " + str(estatisticas_globais["E[W2]"])
        print "\tE[Nq2]---------->  " + str(estatisticas_globais["E[Nq2]"])
        print "\tE[delta]-------->  " + str(estatisticas_globais["E[delta]"])
        print "\tV[delta]-------->  " + str(estatisticas_globais["V[delta]"])
        # print "######################"
        # print "DESVIO PADRAO:"
        # print "grupo 1:"
        # print "T1 ------------->  " + str(desvio_padrao["V[T1]"])
        # print "X1 ------------->  " + str(desvio_padrao["V[X1]"])
        # print "W1 ------------->  " + str(desvio_padrao["V[W1]"])
        # print "Nq1 ------------>  " + str(desvio_padrao["V[Nq1]"])
        # print "grupo 2:"
        # print "T2 ------------->  " + str(desvio_padrao["V[T2]"])
        # print "W2 ------------->  " + str(desvio_padrao["V[W2]"])
        # print "Nq2 ------------>  " + str(desvio_padrao["V[Nq2]"])

        # Calculo dos limites do IC
        percentil = stats.t.ppf(um_menos_alfa_sobre_dois, i-1)
        IC_limite_inferior["E[T1]"] = estatisticas_globais["E[T1]"] - percentil * desvio_padrao["V[T1]"] / raiz_i
        IC_limite_superior["E[T1]"] = estatisticas_globais["E[T1]"] + percentil * desvio_padrao["V[T1]"] / raiz_i
        IC_limite_inferior["E[X1]"] = estatisticas_globais["E[X1]"] - percentil * desvio_padrao["V[X1]"] / raiz_i
        IC_limite_superior["E[X1]"] = estatisticas_globais["E[X1]"] + percentil * desvio_padrao["V[X1]"] / raiz_i
        IC_limite_inferior["E[W1]"] = estatisticas_globais["E[W1]"] - percentil * desvio_padrao["V[W1]"] / raiz_i
        IC_limite_superior["E[W1]"] = estatisticas_globais["E[W1]"] + percentil * desvio_padrao["V[W1]"] / raiz_i
        IC_limite_inferior["E[Nq1]"] = estatisticas_globais["E[Nq1]"] - percentil * desvio_padrao["V[Nq1]"] / raiz_i
        IC_limite_superior["E[Nq1]"] = estatisticas_globais["E[Nq1]"] + percentil * desvio_padrao["V[Nq1]"] / raiz_i
        IC_limite_inferior["E[T2]"] = estatisticas_globais["E[T2]"] - percentil * desvio_padrao["V[T2]"] / raiz_i
        IC_limite_superior["E[T2]"] = estatisticas_globais["E[T2]"] + percentil * desvio_padrao["V[T2]"] / raiz_i
        IC_limite_inferior["E[W2]"] = estatisticas_globais["E[W2]"] - percentil * desvio_padrao["V[W2]"] / raiz_i
        IC_limite_superior["E[W2]"] = estatisticas_globais["E[W2]"] + percentil * desvio_padrao["V[W2]"] / raiz_i
        IC_limite_inferior["E[Nq2]"] = estatisticas_globais["E[Nq2]"] - percentil * desvio_padrao["V[Nq2]"] / raiz_i
        IC_limite_superior["E[Nq2]"] = estatisticas_globais["E[Nq2]"] + percentil * desvio_padrao["V[Nq2]"] / raiz_i
        IC_limite_inferior["E[delta]"] = estatisticas_globais["E[delta]"] - percentil * desvio_padrao["E[delta]"] / raiz_i
        IC_limite_superior["E[delta]"] = estatisticas_globais["E[delta]"] + percentil * desvio_padrao["E[delta]"] / raiz_i
        IC_limite_inferior["V[delta]"] = estatisticas_globais["V[delta]"] - percentil * desvio_padrao["V[delta]"] / raiz_i
        IC_limite_superior["V[delta]"] = estatisticas_globais["V[delta]"] + percentil * desvio_padrao["V[delta]"] / raiz_i


        # Calcula a proporcao entre o ponto medio e a largura dos ICs
        chaves = {}
        if preempcao == False:
            chaves = {"E[T1]", "E[X1]", "E[W1]", "E[Nq1]", "E[T2]", "E[W2]", "E[Nq2]"}
        else:
            chaves = {"E[T2]", "E[W2]", "E[Nq2]"}

        numero_proporcoes_ok = 0
        for chave in chaves:
            proporcoes[chave] = ((IC_limite_superior[chave] - IC_limite_inferior[chave]) / estatisticas_globais[chave])
            if proporcoes[chave] < 0.1: numero_proporcoes_ok += 1

        print "#########################"
        print "ICs:"
        print "[DADOS]"
        print "\tT1: (" + str(IC_limite_inferior["E[T1]"]) + ", " + str(IC_limite_superior["E[T1]"]) + "). Largura: [" + str(IC_limite_superior["E[T1]"] - IC_limite_inferior["E[T1]"]) + "]"
        if preempcao == False: print "\tproporcao: [" + str(proporcoes["E[T1]"] * 100) + "%]"
        print "\tX1: (" + str(IC_limite_inferior["E[X1]"]) + ", " + str(IC_limite_superior["E[X1]"]) + "). Largura: [" + str(IC_limite_superior["E[X1]"] - IC_limite_inferior["E[X1]"]) + "]"
        if preempcao == False: print "\tproporcao: [" + str(proporcoes["E[X1]"] * 100) + "%]"
        print "\tW1: (" + str(IC_limite_inferior["E[W1]"]) + ", " + str(IC_limite_superior["E[W1]"]) + "). Largura: [" + str(IC_limite_superior["E[W1]"] - IC_limite_inferior["E[W1]"]) + "]"
        if preempcao == False: print "\tproporcao: [" + str(proporcoes["E[W1]"] * 100) + "%]"
        print "\tNq1:(" + str(IC_limite_inferior["E[Nq1]"]) + ", " + str(IC_limite_superior["E[Nq1]"]) + "). Largura: [" + str(IC_limite_superior["E[Nq1]"] - IC_limite_inferior["E[Nq1]"]) + "]"
        if preempcao == False: print "\tproporcao: [" + str(proporcoes["E[Nq1]"] * 100) + "%]"
        print "[VOZ]"
        print "\tT2: (" + str(IC_limite_inferior["E[T2]"]) + ", " + str(IC_limite_superior["E[T2]"]) + "). Largura: [" + str(IC_limite_superior["E[T2]"] - IC_limite_inferior["E[T2]"]) + "]"
        print "\tproporcao: [" + str(proporcoes["E[T2]"] * 100) + "%]"
        print "\tW2: (" + str(IC_limite_inferior["E[W2]"]) + ", " + str(IC_limite_superior["E[W2]"]) + "). Largura: [" + str(IC_limite_superior["E[W2]"] - IC_limite_inferior["E[W2]"]) + "]"
        print "\tproporcao: [" + str(proporcoes["E[W2]"] * 100) + "%]"
        print "\tNq2:(" + str(IC_limite_inferior["E[Nq2]"]) + ", " + str(IC_limite_superior["E[Nq2]"]) + "). Largura: [" + str(IC_limite_superior["E[Nq2]"] - IC_limite_inferior["E[Nq2]"]) + "]"
        print "\tproporcao: [" + str(proporcoes["E[Nq2]"] * 100) + "%]"
        print "\tE[delta]:(" + str(IC_limite_inferior["E[delta]"]) + ", " + str(IC_limite_superior["E[delta]"]) + "). Largura: [" + str(IC_limite_superior["E[delta]"] - IC_limite_inferior["E[delta]"]) + "]"
        print "\tV[delta]:(" + str(IC_limite_inferior["V[delta]"]) + ", " + str(IC_limite_superior["V[delta]"]) + "). Largura: [" + str(IC_limite_superior["V[delta]"] - IC_limite_inferior["V[delta]"]) + "]"
        print "Numero de rodadas: " + str(i)

        if numero_proporcoes_ok == len(chaves):
            print "#########################"
            exit()

    i += 1