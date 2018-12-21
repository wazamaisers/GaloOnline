#Servidor

import socket

UDP_IP = "127.0.0.1"
UDP_RECIEVING_PORT = 5006
UDP_SENDING_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_RECIEVING_PORT))

global users           # lista de users
global portos          # dicionario user -> porto
global estados         # dicionario user -> estado
global lista_espera    # dicionario user -> lista de espera para jogar

users = []
portos = {}
estados = {}
lista_espera={}


def enviar_mensagem(mensagem, porto):
    # Funcao para enviar mensagens para os clientes
    
    sock.sendto(mensagem.encode('UTF-8'), (UDP_IP, porto))


def registar(mensagem_split, users, portos, estados, lista_espera):
    # Funcao para registar um cliente
    
    repetido = False
    
    # Verificacao se ja existe username pedido
    for i in users:
        if (mensagem_split[1] == i):
            repetido = True
            enviar_mensagem("Nome de utilizador em uso",addr[1])
            break
        
    # Caso nao exista adiciona o user a lista e inicializa os dicionarios
    if (repetido != True):          
        users += [mensagem_split[1]]
        portos[mensagem_split[1]] = addr[1]
        estados[mensagem_split[1]] = 'livre'
        lista_espera[mensagem_split[1]] = []
        enviar_mensagem("Registo com sucesso",addr[1])

def listar():
    # Funcao para listar utilizadores
    
    lista_users = ''
    
    # Percorre a lista de users e os dicionarios user -> estado e divide
    # user de estado por '-' e cada par por ':'
    for i in users:
        lista_users = lista_users + i + '-' + estados[i] + ':'
    enviar_mensagem(lista_users,addr[1])


def convidar(mensagem_split, users, estados, lista_espera):
    # Funcao para convidar um jogador para uma partida
    
    existe = 0
    for i in range(len(users)):
        
        # Verifica se o user existe
        if (mensagem_split[1] == users[i]):
            existe = 1
            
            # Verifica se este esta livre para jogar e envia pedido
            if(estados[users[i]]=='livre'):
                enviar_mensagem("Convite enviado",addr[1])
                lista_espera[mensagem_split[1]] += [mensagem_split[2],]
                estados[mensagem_split[2]] = 'ocupado'
            elif (estados[mensagem_split[1]] == 'ocupado'):
                enviar_mensagem("User convidado nao esta dispovinel",addr[1])
    if (existe == 0):
        enviar_mensagem("User convidado nao existe",addr[1]) 
        
        

def ver_pedidos(mensagem_split, users, lista_espera):
    # Funcao para verificar se um determinado jogador foi convidado para uma partida
    for i in range(len(users)):
        
        # Verifica se o user existe
        if (mensagem_split[1] == users[i]):
            
            # Verifica se tem algum convite em espera
            if ((len(lista_espera[mensagem_split[1]])) != 0):
                string_convites = ''
                
                # Se sim envia-os todos para o cliente
                for e in range(len(lista_espera[mensagem_split[1]])):
                    string_convites = string_convites + lista_espera[mensagem_split[1]][e] + ' '
                enviar_mensagem(string_convites,addr[1])
                lista_espera[mensagem_split[1]] = []
                
            else:
                enviar_mensagem("Nao tem pedidos pendentes",addr[1])    


def resposta_pedido(mensagem_split, estados, portos):
    # Funcao para responder a um pedido de jogo
    
    # Se o pedido for aceite envia as inicializacoes do jogo para o cliente
    if(mensagem_split[1] == 'True'):
        mensagem_jogador_convidado = 'jogo O ' + mensagem_split[2] + ' ' + mensagem_split[2]
        mensagem_jogador_convite = 'jogo X ' + mensagem_split[2] + ' ' + mensagem_split[3]
        
        # Coloca o estado de ambos como ocupado
        enviar_mensagem(mensagem_jogador_convite,portos[mensagem_split[2]])
        estados[mensagem_split[2]] = 'ocupado'
        
        enviar_mensagem(mensagem_jogador_convidado,portos[mensagem_split[3]])
        estados[mensagem_split[3]] = 'ocupado'
        
    if(mensagem_split[1] == 'False'):
        enviar_mensagem('O pedido foi rejeitado',portos[mensagem_split[2]])
        estados[mensagem_split[2]] = 'livre'
    
    
def jogada(mensagem, portos):
    # Funcao que faz o encaminhamento de jogadas entre os clientes de um jogo
    
    enviar_mensagem(mensagem,portos[mensagem_split[1]])  


def fim_jogo(mensagem_split, estados, portos):
    # Funcao que e chamada quando um jogo acabou. Envia o resultado para o
    # adversario e coloca ambos os estados dos jogadores a livre
    
    enviar_mensagem(mensagem_split[1],portos[mensagem_split[2]])
    estados[mensagem_split[2]] = 'livre'
    estados[mensagem_split[3]] = 'livre'
    
def termina_ligacao(mensagem_split, users, portos, estados, lista_espera):
    # Funcao que
    
    users.remove(mensagem_split[1])
    del portos[mensagem_split[1]]
    del estados[mensagem_split[1]]
    del lista_espera[mensagem_split[1]]
    

while True:
    #Ciclo infinito de verificacao de mensagens enviadas pelos clientes
    
    data, addr = sock.recvfrom(1024)
    print ("received message:", data.decode('UTF-8'))
    print (addr)
    
    mensagem = data.decode('UTF-8')
    mensagem_split = mensagem.split()
    
    if (mensagem_split[0] == 'registar'):
        registar(mensagem_split, users, portos, estados, lista_espera)
    
    if (mensagem_split[0] == 'listar'):
        listar()
        
    if (mensagem_split[0] == 'convidar'):
        convidar(mensagem_split, users, estados, lista_espera)
    
    if(mensagem_split[0] == 'ver_pedidos'):
        ver_pedidos(mensagem_split, users, lista_espera)
    
    if(mensagem_split[0] == 'resposta_pedido'):
        resposta_pedido(mensagem_split, estados, portos)
        
    if(mensagem_split[0] == 'jogada'):
        jogada(mensagem, portos)
        
    if(mensagem_split[0] == 'fim_jogo'):
        fim_jogo(mensagem_split, estados, portos)
    
    if(mensagem_split[0] == 'termina_ligacao'):
            termina_ligacao(mensagem_split, users, portos, estados, lista_espera)