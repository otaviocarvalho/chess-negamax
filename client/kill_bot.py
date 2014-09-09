import sys
import random

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

# BOT =========================================================================
class KillBot(LiacBot):
    name = 'KillBot'
    ip = '127.0.0.1'
    port = 50100

    def __init__(self):
        # Construtor
        super(KillBot, self).__init__()

    # Move os elementos no tabuleiro
    def on_move(self, state):
        # Pega o estado atual do tabuleiro
        board = Board(state)

        # Gera movimentos possiveis
        moves = board.generate()
        print moves

        # Escolhe o movimento
        chosen_move = []
        chosen_move_eval = -1
        #for i in range(1,10):
        for move in moves:
            #move = random.choice(moves)
            print "move:"
            print move

            move_eval = board.evaluate(move)
            print "eval: "
            print move_eval

            if move_eval > chosen_move_eval:
                print "step move_eval"
                print move_eval
                chosen_move = move
                chosen_move_eval = move_eval

        print "chosen move: "
        print chosen_move
        print "chosen move eval: "
        print chosen_move_eval

        #quit()
        # Aceita input manual se cair em um estado errado
        if state['bad_move']:
            print "bad_move"
            print state['board']
            raw_input()


        # Executa o movimento escolhido
        self.send_move(chosen_move[0], chosen_move[1])
        #self.send_move(move[0], move[1])
        #self.send_move((1, 1), (3, 1)) # Exemplo de movimento manual

    def on_game_over(self, state):
        print 'Game Over.'
        quit()
# =============================================================================

# MODELS ======================================================================
class Board(object):
    def __init__(self, state):
        self.cells = [[None for j in xrange(8)] for i in xrange(8)]
        self.my_pieces = []

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

                i += 1

    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        return self[pos] is None

    def generate(self):
        moves = []
        for piece in self.my_pieces:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            moves.extend(ms)

        return moves

    # Funcao de avaliacao do tabuleiro
    def evaluate(self, move):
        # Teste para dar peso as capturas de peoes
        piece = self.__getitem__(move[0])
        return piece.evaluate(move)


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

    def evaluate(self, move):
        pass

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

        return moves

    def evaluate(self, move):
        print "evaluating pawn move"
        print move

        # Atribui maior valor a captura
        piece = self.board[move[1]]
        if self.is_opponent(piece):
            print "capture"
            return 50;
        else:
            return 1;

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

    def evaluate(self, move):
        print "evaluating rook move"
        print move

        # Atribui maior valor a captura
        piece = self.board[move[1]]
        if self.is_opponent(piece):
            print "capture"
            return 50;
        else:
            return 10;

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

    def evaluate(self, move):
        print "evaluating knight move"
        print move

        # Atribui maior valor a captura
        piece = self.board[move[1]]
        if self.is_opponent(piece):
            print "capture"
            return 50;
        else:
            return 20;

# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200


    bot = KillBot()
    bot.port = port

    bot.start()





