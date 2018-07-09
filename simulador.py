import random as rd
import numpy.random

# ********************************************************************
# Declaracao de variaveis globais
# ********************************************************************

preempcao = True
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
ro1 = 0.1

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
        self.tempo_entrou_na_fila = 0

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
def printa_fila(t, capacidade, n_fila, n_servidor, rotulo):
    if modo_debug:
        linha = ""
        asteriscos = ""
        for j in range(0, capacidade-n_fila): linha += "_"
        for j in range(0, n_fila): asteriscos += "x"
        servidor = ""
        if n_servidor==1: servidor = "x"
        else: servidor = "_"
        print "t = "+str(t)+"\t"+linha+asteriscos+"|"+servidor+" ("+rotulo+")"

# Imprime na tela os valores correntes dos indices das filas
def printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz):
    if modo_debug:
        print "inicio_fila_dados: " + str(inicio_fila_dados)
        print "fim_fila_dados: " + str(fim_fila_dados)
        print "n_fila_dados: " + str(n_fila_dados)
        print "inicio_fila_voz: " + str(inicio_fila_voz)
        print "fim_fila_voz: " + str(fim_fila_voz)
        print "n_fila_voz: " + str(n_fila_voz)

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
def simulacao(total_pacotes_dados, n_pacotes_fase_transiente):
    # Valida os parametros
    if total_pacotes_dados <= 0:
        print "Erro: Numero de fregueses menor que um"
        return None
    if n_pacotes_fase_transiente <= 0:
        print "Erro: Numero de fregueses ate o fim da fase transiente menor que um"
        return None
    if n_pacotes_fase_transiente >= total_pacotes_dados:
        print "Erro: Numero de fregueses ate o fim da fase transiente menor ou igual ao numero total de fregueses"
        return None

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
    "V(deltak)":0
    }

    # CRIACAO DE UM VETOR CONTENDO TODAS AS CHEGADAS QUE OCORRERAO DO FUTURO
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
    # Tempo que ocorreu a ultima iteracao do simulador. Usado para calcular E[Nq1] e E[Nq2] pelo metodo das areas
    t_anterior = 0
    # Numero de pacotes de dados ja criados. Usado para conhecer o progresso da simulacao
    n_pacotes_criados = 0
    # Numero de pacotes de voz criados fora da fase transiente
    n_pacotes_voz_criados_fora_da_fase_transiente = 0
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

    # Gera a chegada do primeiro pacote de dados
    # Como o sistema acaba de abrir, esse pacote ira passar direto pela fila e ira para o servidor
    # Mas, mesmo assim, precisa primeiro inserir ele na fila, pois ele pode ser interrompido e ter que voltar pra fila
    fila_dados.append(chegadas[n_pacotes_criados])
    fim_fila_dados += 1 # Entrou na fila
    fila_dados[fim_fila_dados].tempo_entrou_na_fila = t
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
        # Verifica se a fase transiente ja passou
        if fase_transiente == True and n_pacotes_criados >= n_pacotes_fase_transiente: fase_transiente = False

        # raw_input ("Press enter to continue...")

        # Descobre qual eh o proximo evento que deve ser tratado
        # Se o menor tempo eh o termino do servico de algum pacote do servidor, ou o tempo de alguma chegada
        proximos_eventos = []
        # Pega o tempo das proximas chegadas de pacotes de voz
        for i in range(0, n_canais): proximos_eventos.append([canais[i].tempo_prox_chegada, "pacote_voz", i])
        # Pega o tempo da proxima chegada de pacote de dados
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
                        # Atualiza o nosso E[deltak]
                        estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                        canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                    if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                    else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
                # Oficialmente, um pacote de voz acaba de entrar no servidor.
                printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - servico")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                # Se nao ha preempcao, o pacote de voz ira para a fila invariavelmente.
                if preempcao == False:
                    fila_voz.append(pacote_voz(t))
                    if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                    fim_fila_voz += 1
                    n_fila_voz += 1
                    # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                    printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - fila")
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
                                # Atualiza o nosso E[deltak]
                                estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                                canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                            if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                            else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
                        # Chuta ele do servidor
                        inicio_fila_dados -= 1
                        n_fila_dados += 1
                        # Anotamos o tempo em que o pacote de dados voltou para a fila apos ser chutado do servidor
                        # Isso eh necessario para gerar a estatistica de E[W1]
                        fila_dados[inicio_fila_dados].tempo_entrou_na_fila = t
                        del servidor[0]
                        servidor.append(pacote_voz(t))
                        if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                        servidor[0].tempo_entrou_em_servico = t
                        # Oficialmente, um pacote de voz acaba de entrar no servidor.
                        printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - preempcao")
                        printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
                    else:
                        fila_voz.append(pacote_voz(t))
                        if fase_transiente == False: n_pacotes_voz_criados_fora_da_fase_transiente += 1
                        fim_fila_voz += 1
                        n_fila_voz += 1
                        # Oficialmente, um pacote de voz acaba de entrar na fila de voz.
                        printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - fila")
                        printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

            canais[indice_canal].quantos_pacotes_faltam_nesse_periodo_atividade -= 1

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
                # Para gerar a estatistica de E[W1], precisamos anotar o tempo em que esse pacote entrou na fila separadamente
                # do tempo em que ele chegou, pois esse pacote pode ser interrompido.
                fila_dados[fim_fila_dados].tempo_entrou_na_fila = t
                # Oficialmente, um pacote de dados acaba de entrar na fila de dados.
                printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - fila")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

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
                        # Atualiza o nosso E[deltak]
                        estatisticas["E[deltak]"] += (t - canais[indice_canal].tempo_inicio_servico_ultimo_pacote)
                        canais[indice_canal].numero_intervalos_entre_inicios_servico += 1
                    if canais[indice_canal].esta_em_atividade: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = t
                    else: canais[indice_canal].tempo_inicio_servico_ultimo_pacote = -1
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
                # Verifica se deve gerar as estatisticas sobre o pacote
                if fase_transiente == False:
                    # Atualiza o nosso E[W1k]
                    estatisticas["E[W1k]"] += (servidor[0].tempo_entrou_em_servico - servidor[0].tempo_entrou_na_fila)
                # Oficialmente, um pacote de dados acaba de entrar em servico
                printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - servico")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)
            else:
                # As duas filas estao vazias
                printa_fila(t, 20, n_fila_dados, n_servidor, "DADOS - vazia")
                printa_fila(t, 20, n_fila_voz, n_servidor, "VOZ - vazia")
                printa_numeros(inicio_fila_dados, fim_fila_dados, n_fila_dados, inicio_fila_voz, fim_fila_voz, n_fila_voz)

        # Atualiza os nossos E[Nq1k] e E[Nq2k] pelo metodo das areas
        if fase_transiente == False:
            delta_tempo = t - t_anterior
            estatisticas["E[Nq1k]"] += (n_fila_dados * delta_tempo)
            estatisticas["E[Nq2k]"] += (n_fila_voz * delta_tempo)

    # Fim - while
    # Termina de calcular os nossos E[T1k], E[T2k], E[X1k], E[W1k], E[Nq1k], E[Nq2k] e E[deltak]
    estatisticas["E[T1k]"] = estatisticas["E[T1k]"] / (n_pacotes_criados - n_pacotes_fase_transiente)
    estatisticas["E[T2k]"] = estatisticas["E[T2k]"] / n_pacotes_voz_criados_fora_da_fase_transiente
    estatisticas["E[X1k]"] = estatisticas["E[X1k]"] / (n_pacotes_criados - n_pacotes_fase_transiente)
    estatisticas["E[W1k]"] = estatisticas["E[W1k]"] / (n_pacotes_criados - n_pacotes_fase_transiente)
    estatisticas["E[W2k]"] = estatisticas["E[W2k]"] / n_pacotes_voz_criados_fora_da_fase_transiente
    estatisticas["E[Nq1k]"] = estatisticas["E[Nq1k]"] / t
    estatisticas["E[Nq2k]"] = estatisticas["E[Nq2k]"] / t
    total_intervalos = 0
    for i in range(0, n_canais): total_intervalos += canais[i].numero_intervalos_entre_inicios_servico
    estatisticas["E[deltak]"] = estatisticas["E[deltak]"] / total_intervalos

    return estatisticas

# ********************************************************************
# Programa principal
# ********************************************************************

numero_rodadas = 3
numero_fregueses = 10000
fase_transiente = 2000

# Estatisticas globais sao as que dizem respeito a todas as rodadas de simulacao
estatisticas_globais = {
    "E[T1]":0,
    "E[W1]":0,
    "E[X1]":0,
    "E[Nq1]":0,
    "E[T2]":0,
    "E[W2]":0,
    "E[Nq2]":0,
    "E[delta]":0,
    "V(delta)":0
    }

for i in range(0, numero_rodadas):
    # Executa uma rodada de simulacao
    estatisticas_rodada = simulacao(numero_fregueses, fase_transiente)
    print "grupo 1:"
    print "E[T1k] ---------->  " + str(estatisticas_rodada["E[T1k]"])
    print "E[X1k] ---------->  " + str(estatisticas_rodada["E[X1k]"])
    print "E[W1k] ---------->  " + str(estatisticas_rodada["E[W1k]"])
    print "E[Nq1k]---------->  " + str(estatisticas_rodada["E[Nq1k]"])
    print "grupo 2:"
    print "E[T2k] ---------->  " + str(estatisticas_rodada["E[T2k]"])
    print "E[X2k] ---------->  " + str(tempo_servico_pacote_voz)
    print "E[W2k] ---------->  " + str(estatisticas_rodada["E[W2k]"])
    print "E[Nq2k]---------->  " + str(estatisticas_rodada["E[Nq2k]"])
    print "E[deltak]-------->  " + str(estatisticas_rodada["E[deltak]"])
    print "~~~~~~~~~~~~~"

    # Atualiza as estatisticas globais
    estatisticas_globais["E[T1]"] += estatisticas_rodada["E[T1k]"]
    estatisticas_globais["E[W1]"] += estatisticas_rodada["E[W1k]"]
    estatisticas_globais["E[X1]"] += estatisticas_rodada["E[X1k]"]
    estatisticas_globais["E[T2]"] += estatisticas_rodada["E[T2k]"]
    estatisticas_globais["E[W2]"] += estatisticas_rodada["E[W2k]"]
    estatisticas_globais["E[Nq1]"] += estatisticas_rodada["E[Nq1k]"]
    estatisticas_globais["E[Nq2]"] += estatisticas_rodada["E[Nq2k]"]
    estatisticas_globais["E[delta]"] += estatisticas_rodada["E[deltak]"]

# Termina de calcular as estatisticas globais
for chave in estatisticas_globais:
    estatisticas_globais[chave] = estatisticas_globais[chave] / numero_rodadas

print "ESTATISTICAS GLOBAIS:"
print "grupo 1:"
print "E[T1] ---------->  " + str(estatisticas_globais["E[T1]"])
print "E[X1] ---------->  " + str(estatisticas_globais["E[X1]"])
print "E[W1] ---------->  " + str(estatisticas_globais["E[W1]"])
print "E[Nq1]---------->  " + str(estatisticas_globais["E[Nq1]"])
print "grupo 2:"
print "E[T2] ---------->  " + str(estatisticas_globais["E[T2]"])
print "E[W2] ---------->  " + str(estatisticas_globais["E[W2]"])
print "E[Nq2]---------->  " + str(estatisticas_globais["E[Nq2]"])
print "E[delta]-------->  " + str(estatisticas_globais["E[delta]"])