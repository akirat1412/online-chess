from piece import Piece
import copy


class Game:
    def __init__(self):
        self.board = [[Piece() for _ in range(8)] for _ in range(8)]
        self.turn = 'white'
        self.en_passant = None
        self.castling = [[True, True], [True, True]]

        self.initialize_board()

        # track location of pieces
        self.white_king = [4, 0]
        self.black_king = [4, 7]
        self.white_pieces = [[i, 0] for i in range(8)] + [[i, 1] for i in range(8)]
        self.black_pieces = [[i, 6] for i in range(8)] + [[i, 7] for i in range(8)]

    def initialize_board(self):
        # initialize white pieces
        self.board[0][0] = Piece('white', 'rook')
        self.board[1][0] = Piece('white', 'knight')
        self.board[2][0] = Piece('white', 'bishop')
        self.board[3][0] = Piece('white', 'queen')
        self.board[4][0] = Piece('white', 'king')
        self.board[5][0] = Piece('white', 'bishop')
        self.board[6][0] = Piece('white', 'knight')
        self.board[7][0] = Piece('white', 'rook')
        for i in range(8):
            self.board[i][1] = Piece('white', 'pawn')

        # initialize black pieces
        self.board[0][7] = Piece('black', 'rook')
        self.board[1][7] = Piece('black', 'knight')
        self.board[2][7] = Piece('black', 'bishop')
        self.board[3][7] = Piece('black', 'queen')
        self.board[4][7] = Piece('black', 'king')
        self.board[5][7] = Piece('black', 'bishop')
        self.board[6][7] = Piece('black', 'knight')
        self.board[7][7] = Piece('black', 'rook')
        for i in range(8):
            self.board[i][6] = Piece('black', 'pawn')

    # checks all squares that one side is attacking
    def get_all_attacking(self, color):
        attacking = []
        if color == 'white':
            for x, y in self.white_pieces:
                attacking += self.get_attacking(x, y)

    # helper function that checks what squares a piece is attacking
    def get_attacking(self, x, y, color):
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

    def is_king_safe(self, start, end, color):
        attacked = []

        attacking_pieces = []
        if color == 'white':
            attacking_pieces = self.black_pieces
        else:
            attacking_pieces = self.white_pieces

        for x, y in attacking_pieces:
            # TODO: en passant
            if end == [x, y]:
                continue
            piece = self.board[x][y]
            if piece.piece == 'pawn':
                if color == 'white':
                    attacked += [[x-1, y-1], [x+1, y-1]]
                else:
                    attacked += [[x-1, y+1], [x+1, y+1]]
            elif piece.piece == 'knight':
                attacked += [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2],
                             [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2]]
            elif piece.piece == 'bishop':
                directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions, color)
            elif piece.piece == 'rook':
                directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions, color)
            elif piece.piece == 'queen':
                directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions, color)
            elif piece.piece == 'king':
                attacked += [[x, y+1], [x+1, y+1], [x+1, y], [x+1, y-1],
                             [x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1]]
        if color == 'white':
            if start == self.white_king:
                return end not in attacked
            else:
                return self.white_king not in attacked
        else:
            if start == self.black_king:
                return end not in attacked
            else:
                return self.black_king not in attacked

    def is_king_safe_helper(self, x, y, start, end, directions, color):
        attacked = []
        for dir_x, dir_y in directions:
            temp_x = x + dir_x
            temp_y = y + dir_y

            while -1 < temp_x < 8 and -1 < temp_y < 8:
                if end == [temp_x, temp_y] or \
                        (start != [temp_x, temp_y] and self.board[temp_x][temp_y].color is not None):
                    attacked.append([temp_x, temp_y])
                    break
                temp_x += dir_x
                temp_y += dir_y
        return attacked

    # checks if a move is legal
    def is_legal(self, start, end):
        x = start[0]
        y = start[1]
        piece = self.board[x][y]
        legal_moves = []

        if piece.piece == 'pawn':
            if self.turn == 'white':
                if self.board[x][y + 1].piece is None:
                    legal_moves.append([x, y + 1])
                    if y == 1 and self.board[x][y + 2].piece is None:
                        legal_moves.append([x, y + 2])
                if x > 0 and self.board[x - 1][y + 1].color == 'black':
                    legal_moves.append([x - 1, y + 1])
                if x < 7 and self.board[x + 1][y + 1].color == 'black':
                    legal_moves.append([x + 1, y + 1])
            else:
                if self.board[x][y - 1].piece is None:
                    legal_moves.append([x, y - 1])
                    if y == 6 and self.board[x][y - 2].piece is None:
                        legal_moves.append([x, y - 2])
                if x > 0 and self.board[x - 1][y - 1].color == 'white':
                    legal_moves.append([x - 1, y - 1])
                if x < 7 and self.board[x + 1][y - 1].color == 'white':
                    legal_moves.append([x + 1, y - 1])
        elif piece.piece == 'knight':
            temp = [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2],
                    [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2]]
            temp = filter(lambda square: -1 < square[0] < 8 and -1 < square[1] < 8, temp)
            legal_moves = list(filter(lambda square: self.board[square[0]][square[1]].color != self.turn, temp))
        elif piece.piece == 'bishop':
            directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
            legal_moves = self.is_legal_helper(x, y, directions)
        elif piece.piece == 'rook':
            directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
            legal_moves = self.is_legal_helper(x, y, directions)
        elif piece.piece == 'queen':
            directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
            legal_moves = self.is_legal_helper(x, y, directions)
        elif piece.piece == 'king':
            temp = [[x, y+1], [x+1, y+1], [x+1, y], [x+1, y-1],
                    [x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1]]
            temp = filter(lambda square: -1 < square[0] < 8 and -1 < square[1] < 8, temp)
            legal_moves = list(filter(lambda square: self.board[square[0]][square[1]].color != self.turn, temp))
        print(self.is_king_safe(start, end, self.turn))
        return end in legal_moves and self.is_king_safe(start, end, self.turn)

    # helper function that checks if a rook, bishop, queen move is legal
    def is_legal_helper(self, x, y, directions):
        legal_moves = []
        for dir_x, dir_y in directions:
            temp_x = x + dir_x
            temp_y = y + dir_y
            while -1 < temp_x < 8 and -1 < temp_y < 8 and self.board[temp_x][temp_y].color != self.turn:
                legal_moves.append([temp_x, temp_y])
                if self.board[temp_x][temp_y].color is not None:
                    break
                temp_x += dir_x
                temp_y += dir_y
        return legal_moves

    # moves a piece
    # TODO: implement special interactions for castling, promotion, and en passant
    # TODO: check for check and checkmate
    def move(self, start, end):
        start_x = start[0]
        start_y = start[1]
        end_x = end[0]
        end_y = end[1]

        piece = self.board[start_x][start_y]
        if piece.piece == 'king':
            if self.turn == 'white':
                self.white_king = end
            else:
                self.black_king = end
        self.board[start_x][start_y] = Piece()
        self.board[end_x][end_y] = piece
        if self.turn == 'white':
            self.white_pieces.remove(start)
            self.white_pieces.append(end)
            if end in self.black_pieces:
                self.black_pieces.remove(end)
            self.turn = 'black'
        else:
            self.black_pieces.remove(start)
            self.black_pieces.append(end)
            if end in self.white_pieces:
                self.white_pieces.remove(end)
            self.turn = 'white'
