import random
import math
import operator


class Square():
    
    def __init__(self, mine=False, neighbor_mines=0, hidden=True):
        self.is_mine = mine
        self.neighbor_mines = neighbor_mines
        self.is_hidden = hidden
        
    def reveal(self):
        self.is_hidden = False
        
    def set_mine(self):
        self.is_mine = True
        
    def inc_neighbor_mines(self):
        self.neighbor_mines += 1
    
    # Delete later
    def __str__(self):
        return 'X={0}, Y={1} and hidden={2}'.format(self.is_mine,
                                                    self.neighbor_mines,
                                                    self.is_hidden)

        
# La casilla (0,0) corresponde a la esquina superior izquierda
# Representación de posición: (i,j) ==> i: fila, j: columna
class Board():
    
    # Cada dupla corresponde a los valores que hay que sumar
    # a una posición determinada del tablero para calcular uno
    # de sus 8 posibles vecinos.
    NEIGHBOR_POSITION = (
        (-1, -1), (-1,0), (-1, 1),
        ( 0, -1),         ( 0, 1),
        ( 1, -1), ( 1,0), (1, 1 )
    )
    
    def __init__(self, height, width, num_of_mines):
        self.height = height
        self.width = width
        self.num_of_mines = num_of_mines
        self.squares = [[Square() for j in range(width)] for i in range(height)]
        self.variable_elimination = VariableElimination(
            generateBN(height, width, num_of_mines))
        self.evidences = {}
        self.__place_mines__()
        
    # Coloca las minas en el tablero:
    #   1.- Se genera un número aleatorio distinto
    #       por cada mina.
    #   2.- A cada número aleatorio se le asocia una casilla
    #       mediante "__get_position__()".
    #   3.- Se coloca cada mina en la posición calcu.
    #   4.- Se actualiza "Square::neighbor_mines" de las
    #       casillas vecinas de cada una de las minas
    #       (llamando a "__update_neighbors__()").
    
    def __place_mines__(self):
        mines = random.sample(range(self.width * self.height),
                              self.num_of_mines)
        
        for m in mines:
            mine_position = self.__get_position__(m)
            
            i = mine_position[0]
            j = mine_position[1]
            
            square = self.squares[i][j]
            square.set_mine()
            
            self.__update_neighbors__(i, j)
    
    # Devuelve la posición (i,j) dado un índice "index":
    #                 
    # +---+---+      Ejemplos con tablero 2x2:
    # | 0 | 1 |
    # +---+---+        - index = 0 ==> (0,0)
    # | 2 | 3 |        - index = 2 ==> (1,0)
    # +---+---+
    def __get_position__(self, index):
        i = math.floor(index/self.width)
        j = index - self.width*i
        
        return (i, j)
    
    def __update_neighbors__(self, i, j):
        for n in range(8):
            ni = i + self.NEIGHBOR_POSITION[n][0]
            nj = j + self.NEIGHBOR_POSITION[n][1]
            if not (self.__invalid_position__(ni, nj)):
                neighbor = self.squares[ni][nj]
                neighbor.inc_neighbor_mines()
    
    # Tiene en cuenta los límites del tablero
    def __invalid_position__(self, i, j):
        return (j < 0 
                or j >= self.width 
                or i < 0 
                or i >= self.height
               )
    
    # DEBUGGING
    def print_revealed(self):
        res = ''
        
        for i in range(self.height):
            for j in range(self.width):
                square = self.squares[i][j]
                res += '* ' if square.is_mine else '{} '.format(square.neighbor_mines)
            res += '\n'
        
        return res
    
    # DEBUGGING
    def showSelectedSquare(self, i, j):
        square = self.squares[i][j]
        
        print(square)
    
    # DEBUGGING
    def getSquare(self, i, j):
        return self.squares[i][j]
    
    # P=(i,j): casilla que se encuentra en las coordenadas (i,j)
    # del tablero. Debe mostrar la información de aquellas
    # casillas vecinas hasta que se topa con una cuya Y>=1
    # Flood fill algorithm: https://en.wikipedia.org/wiki/Flood_fill
    def reveal_information(self, i, j):
        if not (self.__invalid_position__(i, j)):        
            square = self.squares[i][j]
            if square.is_mine==False and square.is_hidden==True:
                if square.neighbor_mines==0:
                    square.reveal()
                    self.reveal_information(i+1, j)
                    self.reveal_information(i-1, j)
                    self.reveal_information(i, j+1)
                    self.reveal_information(i, j-1)
                    self.reveal_information(i+1, j+1)
                    self.reveal_information(i+1, j-1)
                    self.reveal_information(i-1, j+1)
                    self.reveal_information(i-1, j-1)
                else:
                    square.reveal()
                
                self.__add_evidence__(i, j)            

    def reveal(self, i, j):
        if not self.__invalid_position__(i, j):
            square = self.squares[i][j]
        
            if square.is_mine:
                print('GAME OVER\n=================')
                print(self.print_revealed())
            else:
                self.reveal_information(i, j)
                print(self.__str__())
                (i, j) = self.__suggest_next_square__()
                self.reveal(i, j)
                 
    def __suggest_next_square__(self):
        prob_X = {}
        hidden = self.__get_hidden_squares__()
        
        if self.__is_end_game__(hidden):
            print('Congratulations!! \n Victory')
            print(self.print_revealed())
            return (-1, -1)
        else: 
            for sq in hidden:
                prob_X[(sq[0],sq[1])] = calcule_prob_X(self.variable_elimination,
                                                       sq[0],
                                                       sq[1],
                                                       self.evidences)
            
            # DEBUGGING: return prob_X
            # En caso de que haya dos valores máximos, 
            # asigna el primero que encontró
            suggested = max(prob_X.items(), key=operator.itemgetter(1))[0]
            
            print('Suggested next square: {}'.format(suggested))
            return suggested
        
    def __is_end_game__(self, hidden):
        return self.num_of_mines==len(hidden)
    
    def __get_hidden_squares__(self):
        hidden = set()
        
        for j in range(self.width):
            for i in range(self.height):
                square = self.squares[i][j]
                if square.is_hidden:
                    hidden.add((i,j))
                    
        return hidden
    
    def __add_evidence__(self, i, j):
        square = self.squares[i][j]
        X = bn_X_name(i, j)
        Y = bn_Y_name(i, j)
        
        self.evidences[X] = int(square.is_mine)
        self.evidences[Y] = square.neighbor_mines
        # DEBUGGING: print('=============================\n{}\n============================='.format(self.evidences))
    
    def __str__(self):
        res = ''
        
        for i in range(self.height):
            for j in range(self.width):
                square = self.squares[i][j]
                res += '_ ' if square.is_hidden else '{} '.format(square.neighbor_mines)
            res += '\n'
        
        return res
    
    def __play_game__(self):
        
        # Al principio de la partida, todas las casillas tienen
        # las mismas posibilidades de contener una mina. Por tanto,
        # el algoritmo debe despejar una cualquiera
        i = random.sample(range(self.height), 1)[0]
        j = random.sample(range(self.width), 1)[0]
        
        print(self.__str__())
        print('Suggested square: ({0}, {1})'.format(i, j))
        
        # Esta función se ejecuta recursivamente hasta que termina la partida
        self.reveal(i, j)
        
        
    