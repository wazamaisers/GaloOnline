#Cliente

import socket

UDP_IP = "127.0.0.1"

UDP_SENDING_PORT = 5006
UDP_RECIEVING_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def print_menu_inicial():
    # Funcao que fornece a interface de menu inicial ao cliente antes de se
    # registar
    
    print('\nMENU INICIAL\n' 
              + '1 - Registar Utilizador\n'
              + '0 - Sair')
    
def print_menu_registado():
    # Funcao que fornece a interface de menu principal ao cliente apos o registo
    
    print('\nMENU PRINCIPAL\n'
              + '1 - Listar Jogadores\n'
              + '2 - Convidar Jogador Para Partida\n'
              + '3 - Convites Para Partida\n'
              + '0 - Sair')
def enviar_mensagem(mensagem, porto):
    # Funcao que envia mensagens para o servidor
    
    sock.sendto(mensagem.encode('UTF-8'), (UDP_IP, porto))
    
    
def drawBoard(board):
    # Funcao que imprime o tabuleiro no ecra

    print('   |   |')
    print(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
    print('   |   |')
    print('Legenda:')
    print('7|8|9\n4|5|6\n1|2|3')
    
def isWinner(bo, le):
    # Dado um tabuleiro (bo) e uma letra (le) retorna true se um jogador tiver ganho
    
    return ((bo[7] == le and bo[8] == le and bo[9] == le) or # topo horizontal
    (bo[4] == le and bo[5] == le and bo[6] == le) or # meio horizontal
    (bo[1] == le and bo[2] == le and bo[3] == le) or # fim horizontal
    (bo[7] == le and bo[4] == le and bo[1] == le) or # esquerda vertical
    (bo[8] == le and bo[5] == le and bo[2] == le) or # meio vertical
    (bo[9] == le and bo[6] == le and bo[3] == le) or # direita vertical
    (bo[7] == le and bo[5] == le and bo[3] == le) or # diagonal 1
    (bo[9] == le and bo[5] == le and bo[1] == le)) # diagonal 2

def isSpaceFree(board, move):
    # Retorna true se uma determinada posicao do tabuleiro estiver vazia
    return board[move] == ' '

def isBoardFull(board):
    # Retorna true se o tabuleiro estiver cheio, e false caso contrario
    for i in range(1, 10):
        if isSpaceFree(board, i):
            return False
    return True


def game(string, turno, board, utilizador, adversario):
    # Funcao de inicio de jogo
    
    # Enquanto nao houver um resultado final
    while ((isWinner(board,'X') or isWinner(board,'O') or isBoardFull(board))==False):
        
        # Verufica se e o turno do jogador
        drawBoard(board)
        if (turno == utilizador):
            
            # Se sim, pede jogada
            n1=input('Faz jogada: ')
            n=eval(n1)
            
            # Verifica se e jogada valida
            if (isSpaceFree(board, n) == True):
                board[n] = string
                enviar_board = ''
                
                # Se sim, prepara tabuleiro para enviar em formato de string
                for i in range(len(board)-1):
                    if (board[i+1] == ' '):
                        enviar_board += ':0'
                    else:
                        enviar_board += ':' + board[i+1]
                jogada = 'jogada ' + adversario + ' ' + enviar_board
                enviar_mensagem(jogada, UDP_SENDING_PORT)
                turno = adversario
            else:
                print('Jogada invalida')
             
        # Se nao e o turno do jogador   
        else:
            print('Espera pela jogada do adversario')
            data, addr = sock.recvfrom(1024)
            jogada_split = data.decode('UTF-8').split()
            if (jogada_split[0] == 'jogada'):
                board_recebido = jogada_split[2].split(':')
                
                # Transforma a string contendo o tabuleiro em lista 
                # e muda o turno para si proprio
                for i in range(len(board_recebido)):
                    if (board_recebido[i] == '0'):
                        board[i] = ' '
                    else:
                        board[i] = board_recebido[i]
                turno = utilizador
            
            
    drawBoard(board)
    
    # Se for detetado um fim de jogo averigua o resultado e envia mensagem 
    # para o servidor contendo a infomacao necessaria para avisar o adversario
    if (turno != utilizador):
        if (isWinner(board,'X') and string == 'X'):
            print('Ganhou')
            enviar_mensagem('fim_jogo Perdeu ' + adversario + ' ' + utilizador, UDP_SENDING_PORT)
        if (isWinner(board,'O') and string == 'O'):
            print('Ganhou')
            enviar_mensagem('fim_jogo Perdeu ' + adversario + ' ' + utilizador, UDP_SENDING_PORT)
        if (isBoardFull(board)):
            print('Empatou')
            enviar_mensagem('fim_jogo Empatou1 ' + adversario + ' ' + utilizador, UDP_SENDING_PORT)
    else:
        data, addr = sock.recvfrom(1024)
        print(data.decode('UTF-8'))

def listar(utilizador):
	# Funcao que serve para pedir a lista ao servidor

    comando = 'listar'
    enviar_mensagem(comando, UDP_SENDING_PORT)
    data, addr = sock.recvfrom(1024)
    lista_users = data.decode('UTF-8').split(':')
    print('Esta e a lista de utilizadores registados:')
    for i in range(len(lista_users)-1):
        lista_user_estado = lista_users[i].split('-')
        print('Utilizador: ' + lista_user_estado[0] + ' || Estado: ' + lista_user_estado[1])
        
def convidar(utilizador):
	# Funcao serve para convidar um utilizador para jogar

    user = 'convidar ' + input('Indica nome de utilizador: ')
    user = user + ' ' + utilizador
    enviar_mensagem(user, UDP_SENDING_PORT)
    print("Convite enviado")
    data, addr = sock.recvfrom(1024)
    resposta_split = data.decode('UTF-8').split()

    # Caso em que utilizador convidado rejeita ou nao existe
    if (resposta_split[0] != 'User'):
        data, addr = sock.recvfrom(1024)
        resposta_split = data.decode('UTF-8').split()
    
    # Caso em que o utilizador convidado aceita, o jogo comeca de imediato
    if (resposta_split[0] == 'jogo'):
        board = ['',' ',' ',' ',' ',' ',' ',' ',' ',' ']
        game(resposta_split[1],resposta_split[2],board,utilizador,resposta_split[3])
    else:
        print(data.decode('UTF-8'))
    
def ver_pedidos(utilizador):
	# Funcao serve para visualizar quem enviou convites para jogo, aceitar/rejeitar convites
	# e jogar, caso se aceite um convite

    comando = 'ver_pedidos ' + utilizador
    enviar_mensagem(comando, UDP_SENDING_PORT)
    data, addr = sock.recvfrom(1024)
    pedidos = data.decode('UTF-8')
    lista_pedidos = pedidos.split()
    if (pedidos == 'Nao tem pedidos pendentes'):
        print(pedidos)
    else:

    	# Se existirem pedidos ou se aceita um e rejeita os restantes
    	# ou se rejeitam todos
        for i in range(len(lista_pedidos)):
            print(str(i+1) + ' - ' + lista_pedidos[i])
        print('0 - Rejeitar todos')
        escolha = '-1'
        while (escolha != '0' and escolha != '-2'):
            escolha = input('Escolhe um dos convites de jogo ')
            if (escolha == '0'):
                for i in range(len(lista_pedidos)):
                    resposta = 'resposta_pedido False ' + lista_pedidos[i]
                    enviar_mensagem(resposta, UDP_SENDING_PORT)                    
            else:

            	# Quando se aceita um pedido ha 3 coisas a fazer
                for i in range(len(lista_pedidos)):

                	# Enviar a resposta positiva para o adversario
                    if (eval(escolha) == i+1):
                        resposta = 'resposta_pedido True ' + lista_pedidos[i] + ' ' + utilizador
                        enviar_mensagem(resposta, UDP_SENDING_PORT)
                        del(lista_pedidos[i])

                        # Enviar a resposta negativa para todos os restantes pedidos que estavam em espera
                        for i in range(len(lista_pedidos)):
                            resposta = 'resposta_pedido False ' + lista_pedidos[i]
                            enviar_mensagem(resposta, UDP_SENDING_PORT)
                        
                        # Comecar o jogo
                        data, addr = sock.recvfrom(1024)
                        print(data.decode('UTF-8'))
                        resposta_split = data.decode('UTF-8').split()
                        board = ['',' ',' ',' ',' ',' ',' ',' ',' ',' ']
                        game(resposta_split[1],resposta_split[2],board,utilizador,resposta_split[3])
                        
                escolha = '-2'    

def registar():
	# Funcao serve para registar um utilizador

    user = input('Indica nome de utilizador: ')
    enviar_mensagem('registar ' + user, UDP_SENDING_PORT)
    data, addr = sock.recvfrom(1024)
    print (data.decode('UTF-8'))
    if (data.decode('UTF-8').split()[0] != 'Nome'):
        menu_registado(user)
	
def termina_ligacao(utilizador):
    enviar_mensagem('termina_ligacao ' + utilizador, UDP_SENDING_PORT)

def menu_registado(utilizador):
	# Menu de opções de um utilizador que ja se registou
    
    n = '-1'
    while(n != '0'):
        
        print_menu_registado()
        n = input('Introduz o numero: ')

        if (n == '1'):
            listar(utilizador)
        
        if (n == '2'):
            convidar(utilizador)
    
        if (n == '3'):
            ver_pedidos(utilizador)
        
        if (n == '0'):
            termina_ligacao(utilizador)

def menu_login():
    # Menu de opções de um utilizador que nao esta registado

    n = '-1'
    while(n != '0'):
        
        print_menu_inicial()
        n = input("Introduz o numero: ")
        
        if (n == '1'):
            registar()
           
    print('Saiu')
    
menu_login()