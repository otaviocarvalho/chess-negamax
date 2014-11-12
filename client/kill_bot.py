import sys
import random
import copy
import resource

from base_client import LiacBot

WHITE = 1
BLACK = -1

INFINITY = 100000000

# BOT =========================================================================
class KillBot(LiacBot):
    name = 'KillBot'
    ip = '127.0.0.1'
    port = 50100
    depth = 1

    def __init__(self):
        # Construtor
        super(KillBot, self).__init__()

    # Move os elementos no tabuleiro
    def on_move(self, state):
        # Pega o estado atual do tabuleiro
        board = Board(state)

        # Minimax
        negamax = Negamax()
        moves = negamax.run(board, -INFINITY, INFINITY, self.depth, color)

        # Escolhe um dos movimento gerados pelo negamax
        chosen_move = random.choice(moves['movement'])

        # Aceita input manual se cair em um estado errado
        if state['bad_move']:
            print "bad_move"
            print state['board']
            raw_input()

        # Executa o movimento escolhido
        self.send_move(chosen_move[0], chosen_move[1])

        # Footprint de memoria utilizada
        print("Used mem:")
        print(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000)

    def on_game_over(self, state):
        print 'Game Over.'
        quit()
# =============================================================================

# MODELS ======================================================================
class Negamax(object):
    def run(self, board, alpha, beta, act_depth, act_color):

        if act_depth == 0 or board.game_over():
            return { 'value': board.evaluate()*act_color, 'movement': None }

        best_move = { 'value': -INFINITY, 'movement': None }

        movements = board.generate()

        if len(movements)==0:
            return best_move

        for b_movement in movements:
            movement = self.run(b_movement, -alpha, -beta, act_depth-1, -act_color)
            movement['value'] = -movement['value']

            if best_move['value'] <= movement['value']:
                if best_move['value'] < movement['value']:
                    best_move = {'value':movement['value'], 'movement':[]}
                best_move['movement'].append((b_movement._from, b_movement._to))

            alpha = max(alpha,movement['value'])
            if alpha >= beta:
                break

        return best_move

class Board(object):
    def __init__(self, state):
        self.value = -1
        self.cells = [[None for j in xrange(8)] for i in xrange(8)]
        self.my_pieces = []
        self.my_opponent_pieces = []

        PIECES = {
            'r': Rook,
            'p': Pawn,
            'n': Knight,
        }

        my_team = state['who_moves']
        c = state['board']
        i = 0

        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if c[i] != '.':
                    cls = PIECES[c[i].lower()]
                    team = BLACK if c[i].lower() == c[i] else WHITE

                    piece = cls(self, team, (row, col))
                    self.cells[row][col] = piece

                    if team == my_team:
                        self.my_pieces.append(piece)
                    else:
                        self.my_opponent_pieces.append(piece)

                i += 1

        # Avalia a si mesmo ao criar uma instancia
        self.value = self.evaluate()

    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        return self[pos] is None

    def update_pieces(self, my_color):
        self.my_pieces = []
        self.my_opponent_pieces = []

        for row in xrange(0, 8):
            for col in xrange(0, 8):
                piece = self.cells[row][col]

                if piece != None:
                    if piece.team == my_color:
                        self.my_pieces.append(piece)
                    else:
                        self.my_opponent_pieces.append(piece)

    def print_board(self):
        for row in xrange(0, 8):
            for col in xrange(0, 8):
                if isinstance(self.cells[row][col], Pawn):
                    if self.cells[row][col].team == BLACK:
                        if col == 7:
                            print "P "
                        else:
                            print "P ",
                    else:
                        if col == 7:
                            print "p "
                        else:
                            print "p ",
                elif isinstance(self.cells[row][col], Rook):
                    if self.cells[row][col].team == BLACK:
                        if col == 7:
                            print "R "
                        else:
                            print "R ",
                    else:
                        if col == 7:
                            print "r "
                        else:
                            print "r ",
                elif isinstance(self.cells[row][col], Knight):
                    if self.cells[row][col].team == BLACK:
                        if col == 7:
                            print "K "
                        else:
                            print "K ",
                    else:
                        if col == 7:
                            print "k "
                        else:
                            print "k ",
                else:
                    if col == 7:
                        print ". "
                    else:
                        print ". ",

    def generate(self):
        moves = []
        for piece in self.my_pieces:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            moves.extend(ms)

        # Gerar tabuleiros a partir de movimentos
        boards = []
        for move in moves:
            new_board = copy.deepcopy(self)
            new_board.cells[move[1][0]][move[1][1]] = new_board.cells[move[0][0]][move[0][1]]
            new_board.cells[move[0][0]][move[0][1]] = None
            new_board._from = (move[0][0], move[0][1])
            new_board._to = (move[1][0], move[1][1])
            boards.append(new_board)

        return boards

    # Funcao de avaliacao do tabuleiro
    def evaluate(self):
        white_pawns = 0
        black_pawns = 0
        white_rooks = 0
        black_rooks = 0
        white_knights = 0
        black_knights = 0

        board_value = 0
        for i in xrange(0, 8):
            for j in xrange(0, 8):
                piece = self.cells[i][j]

                # Verifica se existe uma peca na posicao
                if piece is None:
                    continue
                elif piece.team == BLACK:
                    if isinstance(piece, Pawn):
                        board_value = board_value - i
                        black_pawns += 1
                    if isinstance(piece, Rook):
                        black_rooks += 1
                    if isinstance(piece, Knight):
                        black_knights += 1
                else:
                    if isinstance(piece, Pawn):
                        board_value = board_value + (7-i)
                        white_pawns += 1
                    if isinstance(piece, Rook):
                        white_rooks += 1
                    if isinstance(piece, Knight):
                        white_knights += 1

        # Verifica se alguem venceu
        if white_pawns == 0:
            self.value = INFINITY
        elif black_pawns == 0:
            self.value = -INFINITY

        # Calcula a funcao de avaliacao do tabuleiro
        board_value = board_value + 10*(white_pawns - black_pawns) + 3*(white_knights - black_knights) + 5*(white_rooks - black_rooks)
        self.value = board_value

        return self.value

    # Testa posicao de game over
    def game_over(self):
        # Verifica se alguem venceu
        for i in xrange(8):
            if isinstance(self.cells[0][i], Pawn) and self.cells[0][i].team == BLACK:
                return True
            elif isinstance(self.cells[7][i], Pawn) and self.cells[0][i].team == WHITE:
                return True

        # Verifica se ainda existem peoes
        count_pawns = 0
        for i in xrange(8):
            for j in xrange(8):
                if isinstance(self.cells[i][j], Pawn):
                    count_pawns += 1
        if count_pawns == 0:
            return True

        return False

class Piece(object):
    def __init__(self):
        self.board = None
        self.team = None
        self.position = None
        self.type = None

    def generate(self):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.team != self.team

class Pawn(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def generate(self):
        moves = []
        my_row, my_col = self.position

        d = self.team

        # Movement to 1 forward
        pos = (my_row + d*1, my_col)
        if self.board.is_empty(pos):
            moves.append(pos)

        # Normal capture to right
        pos = (my_row + d*1, my_col+1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        # Normal capture to left
        pos = (my_row + d*1, my_col-1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        # Initial Movement
        #if (my_row == 7 or my_row == 1):
            #pos = (my_row + d*2, my_col)
            #if self.board.is_empty(pos):
                #moves.append(pos)

        # Enpassant

        return moves

class Rook(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _col(self, dir_):
        my_row, my_col = self.position
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]

            if piece is None:
                moves.append(pos)
                continue

            elif piece.team != self.team:
                moves.append(pos)

            break

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen(moves, self._col, 8-my_col) # RIGHT
        self._gen(moves, self._col, -my_col-1) # LEFT
        self._gen(moves, self._row, 8-my_row) # TOP
        self._gen(moves, self._row, -my_row-1) # BOTTOM

        return moves

class Knight(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row, col):
        if not 0 <= row <= 7 or not 0 <= col <= 7:
            return

        piece = self.board[(row, col)]
        if piece is None or self.is_opponent(piece):
            moves.append((row, col))

    def generate(self):
        moves = []
        my_row, my_col = self.position

        self._gen(moves, my_row+1, my_col+2)
        self._gen(moves, my_row+1, my_col-2)
        self._gen(moves, my_row-1, my_col+2)
        self._gen(moves, my_row-1, my_col-2)
        self._gen(moves, my_row+2, my_col+1)
        self._gen(moves, my_row+2, my_col-1)
        self._gen(moves, my_row-2, my_col+1)
        self._gen(moves, my_row-2, my_col-1)

        return moves

# =============================================================================

if __name__ == '__main__':
    color = 1
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = -1
            port = 50200

    bot = KillBot()
    bot.port = port

    if len(sys.argv) > 2:
        if sys.argv[2]:
            bot.depth = int(sys.argv[2])

    bot.start()
