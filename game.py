from piece import Piece


class Game:
    def __init__(self):
        self.board = [[Piece() for _ in range(8)] for _ in range(8)]
        self.turn = 'white'

        self.initialize_board()

        # track location of pieces
        self.white_king = [0, 4]
        self.black_king = [7, 4]
        self.white_pieces = [[0, i] for i in range(8)] + [[1, i] for i in range(8)]
        self.black_pieces = [[6, i] for i in range(8)] + [[7, i] for i in range(8)]

    def initialize_board(self):
        # initialize white pieces
        self.board[0][0] = Piece('white', 'rook')
        self.board[0][1] = Piece('white', 'knight')
        self.board[0][2] = Piece('white', 'bishop')
        self.board[0][3] = Piece('white', 'queen')
        self.board[0][4] = Piece('white', 'king')
        self.board[0][5] = Piece('white', 'bishop')
        self.board[0][6] = Piece('white', 'knight')
        self.board[0][7] = Piece('white', 'rook')
        for i in range(8):
            self.board[1][i] = Piece('white', 'pawn')

        # initialize black pieces
        self.board[7][0] = Piece('black', 'rook')
        self.board[7][1] = Piece('black', 'knight')
        self.board[7][2] = Piece('black', 'bishop')
        self.board[7][3] = Piece('black', 'queen')
        self.board[7][4] = Piece('black', 'king')
        self.board[7][5] = Piece('black', 'bishop')
        self.board[7][6] = Piece('black', 'knight')
        self.board[7][7] = Piece('black', 'rook')
        for i in range(8):
            self.board[6][i] = Piece('black', 'pawn')

    def get_all_attacking(self, color):
        attacking = []
        if color == 'white':
            for x, y in self.white_pieces:
                attacking += self.get_attacking(x, y)

    def get_attacking(self, x, y):
        piece = self.board[x][y]
        if piece.type is None:
            return []
        elif piece.type == 'pawn':
            if piece.color == 'white':
                return [[x-1, y+1], [x+1, y+1]]
            else:
                return [[x-1, y-1], [x+1, y-1]]
        elif piece.type == 'knight':
            temp = [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2], [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2]]
            return filter(lambda square: -1 < square[0] < 8 and -1 < square[1] < 8, temp)
        elif piece.type == 'bishop':
            return []
        elif piece.type == 'rook':
            return []
        elif piece.type == 'queen':
            return []
        elif piece.type == 'king':
            return []

        return []

    def get_possible_moves(self, piece):
        return []

    def check_king(self, color):
        return False

    def check_legal(self, piece, move):
        return False
