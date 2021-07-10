from piece import Piece


class Game:
    def __init__(self):
        self.board = [[Piece() for _ in range(8)] for _ in range(8)]
        self.status = ''
        self.turn = 'white'
        self.en_passant = None
        self.castling = [[True, True], [True, True]]
        self.check_square = []
        self.deleted_squares = []
        self.moved_squares = []

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

    # finds all squares that one side is attacking
    def get_attacking(self, color):
        attacking = []

        if color == 'white':
            attacking_pieces = self.white_pieces
        else:
            attacking_pieces = self.black_pieces

        for x, y in attacking_pieces:
            piece = self.board[x][y]
            if piece.piece == 'pawn':
                if color == 'white':
                    attacking += [[x-1, y+1], [x+1, y+1]]
                else:
                    attacking += [[x-1, y-1], [x+1, y-1]]
            elif piece.piece == 'knight':
                attacking += [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2],
                              [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2]]
            elif piece.piece == 'bishop':
                directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
                attacking += self.get_attacking_helper(x, y, directions)
            elif piece.piece == 'rook':
                directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
                attacking += self.get_attacking_helper(x, y, directions)
            elif piece.piece == 'queen':
                directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
                attacking += self.get_attacking_helper(x, y, directions)
            elif piece.piece == 'king':
                attacking += [[x, y+1], [x+1, y+1], [x+1, y], [x+1, y-1],
                              [x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1]]
        return attacking

    # helper function to find all squares one side is attacking
    def get_attacking_helper(self, x, y, directions):
        attacking = []
        for dir_x, dir_y in directions:
            temp_x = x + dir_x
            temp_y = y + dir_y

            while -1 < temp_x < 8 and -1 < temp_y < 8:
                attacking.append([temp_x, temp_y])
                if self.board[temp_x][temp_y].color is not None:
                    break
                temp_x += dir_x
                temp_y += dir_y
        return attacking

    # checks if a move puts the king in check
    def is_king_safe(self, start, end):
        attacked = []

        if self.turn == 'white':
            attacking_pieces = self.black_pieces
        else:
            attacking_pieces = self.white_pieces

        for x, y in attacking_pieces:
            if end == [x, y]:
                continue
            piece = self.board[x][y]
            if piece.piece == 'pawn':
                if self.turn == 'white':
                    attacked += [[x-1, y-1], [x+1, y-1]]
                else:
                    attacked += [[x-1, y+1], [x+1, y+1]]
            elif piece.piece == 'knight':
                attacked += [[x+1, y+2], [x+2, y+1], [x+2, y-1], [x+1, y-2],
                             [x-1, y-2], [x-2, y-1], [x-2, y+1], [x-1, y+2]]
            elif piece.piece == 'bishop':
                directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions)
            elif piece.piece == 'rook':
                directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions)
            elif piece.piece == 'queen':
                directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
                attacked += self.is_king_safe_helper(x, y, start, end, directions)
            elif piece.piece == 'king':
                attacked += [[x, y+1], [x+1, y+1], [x+1, y], [x+1, y-1],
                             [x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1]]
        if self.turn == 'white':
            if start == self.white_king:
                return end not in attacked
            else:
                return self.white_king not in attacked
        else:
            if start == self.black_king:
                return end not in attacked
            else:
                return self.black_king not in attacked

    # helper function to check if a move puts the king in check
    def is_king_safe_helper(self, x, y, start, end, directions):
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

    # checks if move is legal (valid AND does not put king in check)
    def is_legal(self, start, end):
        return end in self.get_valid_moves(start) and self.is_king_safe(start, end)

    # checks if a move is valid, but not whether it puts king in check
    def get_valid_moves(self, start):
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
                if self.en_passant is not None and y == 4 and (x-1 == self.en_passant or x+1 == self.en_passant) and \
                        self.is_en_passant_safe(x):
                    legal_moves.append([self.en_passant, 5])
            else:
                if self.board[x][y - 1].piece is None:
                    legal_moves.append([x, y - 1])
                    if y == 6 and self.board[x][y - 2].piece is None:
                        legal_moves.append([x, y - 2])
                if x > 0 and self.board[x - 1][y - 1].color == 'white':
                    legal_moves.append([x - 1, y - 1])
                if x < 7 and self.board[x + 1][y - 1].color == 'white':
                    legal_moves.append([x + 1, y - 1])
                if self.en_passant is not None and y == 3 and (x-1 == self.en_passant or x+1 == self.en_passant) and \
                        self.is_en_passant_safe(x):
                    legal_moves.append([self.en_passant, 2])
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

            # castling
            if self.turn == 'white':
                attacked = self.get_attacking('black')
                if self.castling[0][0] and self.board[1][0].color is None and self.board[2][0].color is None and \
                        self.board[3][0].color is None and [3, 0] not in attacked and [4, 0] not in attacked:
                    legal_moves.append([2, 0])
                if self.castling[0][1] and self.board[5][0].color is None and self.board[6][0].color is None and \
                        [4, 0] not in attacked and [5, 0] not in attacked:
                    legal_moves.append([6, 0])
            else:
                attacked = self.get_attacking('white')
                if self.castling[1][0] and self.board[1][7].color is None and self.board[2][7].color is None and \
                        self.board[3][7].color is None and [3, 7] not in attacked and [4, 7] not in attacked:
                    legal_moves.append([2, 7])
                if self.castling[1][1] and self.board[5][7].color is None and self.board[6][7].color is None and \
                        [4, 7] not in attacked and [5, 7] not in attacked:
                    legal_moves.append([6, 7])

        return legal_moves

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

    # checks if taking a pawn en passant leaves your king in check
    def is_en_passant_safe(self, pawn_x):
        attacked = []
        if self.turn == 'white':
            attacking = self.black_pieces
        else:
            attacking = self.white_pieces
        for x, y in attacking:
            piece = self.board[x][y]
            if piece.piece == 'rook':
                directions = [[1, 0], [-1, 0]]
                attacked += self.is_en_passant_safe_helper(pawn_x, x, y, directions)
            elif piece.piece == 'queen':
                directions = [[1, 0], [-1, 0]]
                attacked += self.is_en_passant_safe_helper(pawn_x, x, y, directions)

        if self.turn == 'white':
            return self.white_king not in attacked
        else:
            return self.black_king not in attacked

    # helper function for above
    def is_en_passant_safe_helper(self, pawn_x, x, y, directions):
        attacked = []
        for dir_x, dir_y in directions:
            temp_x = x + dir_x
            temp_y = y + dir_y

            while -1 < temp_x < 8 and -1 < temp_y < 8:
                if [self.en_passant, 4] != [temp_x, temp_y] and [pawn_x, 4] != [temp_x, temp_y] and \
                        self.turn == 'white' and self.board[temp_x][temp_y].color is not None:
                    attacked.append([temp_x, temp_y])
                    break
                elif [self.en_passant, 3] != [temp_x, temp_y] and [pawn_x, 3] != [temp_x, temp_y] and \
                        self.turn == 'black' and self.board[temp_x][temp_y].color is not None:
                    attacked.append([temp_x, temp_y])
                    break
                temp_x += dir_x
                temp_y += dir_y
        return attacked

    def has_legal_moves(self):
        if self.turn == 'white':
            moving = self.white_pieces
        else:
            moving = self.black_pieces

        for square in moving:
            for move in self.get_valid_moves(square):
                if self.is_legal(square, move):
                    return True
        return False

    # moves a piece
    def move(self, start, end):
        start_x = start[0]
        start_y = start[1]
        end_x = end[0]
        end_y = end[1]

        piece = self.board[start_x][start_y]
        self.deleted_squares.append(start)
        self.deleted_squares.append(end)
        self.moved_squares.append(end)

        if piece.piece == 'pawn':
            if (piece.color == 'white' and end_y == 7) or (piece.color == 'black' and end_y == 0):
                piece.piece = 'queen'

            if (piece.color == 'white' and start_y == 1 and end_y == 3) or \
                    (piece.color == 'black' and start_y == 6 and end_y == 4):
                self.en_passant = start_x
            else:
                self.en_passant = None
            if piece.color == 'white' and (start_x - end_x == 1 or start_x - end_x == -1) and \
                    self.board[end_x][end_y].color is None:
                self.board[end_x][end_y-1] = Piece()
                self.black_pieces.remove([end_x, end_y-1])
                self.deleted_squares.append([end_x, end_y-1])
            if piece.color == 'black' and (start_x - end_x == 1 or start_x - end_x == -1) and \
                    self.board[end_x][end_y].color is None:
                self.board[end_x][end_y+1] = Piece()
                self.white_pieces.remove([end_x, end_y+1])
                self.deleted_squares.append([end_x, end_y+1])
        else:
            self.en_passant = None

        if piece.piece == 'king':
            if self.turn == 'white':
                self.white_king = end
                if start_x - end_x == 2:
                    self.board[0][0] = Piece()
                    self.board[3][0] = Piece('white', 'rook')
                    self.castling[0] = [False, False]
                    self.white_pieces.append([3, 0])
                    self.white_pieces.remove([0, 0])
                    self.deleted_squares.append([0, 0])
                    self.moved_squares.append([3, 0])
                elif start_x - end_x == -2:
                    self.board[7][0] = Piece()
                    self.board[5][0] = Piece('white', 'rook')
                    self.castling[0] = [False, False]
                    self.white_pieces.append([5, 0])
                    self.white_pieces.remove([7, 0])
                    self.deleted_squares.append([7, 0])
                    self.moved_squares.append([5, 0])
            else:
                self.black_king = end
                if start_x - end_x == 2:
                    self.board[0][7] = Piece()
                    self.board[3][7] = Piece('black', 'rook')
                    self.castling[1] = [False, False]
                    self.black_pieces.append([3, 7])
                    self.black_pieces.remove([0, 7])
                    self.deleted_squares.append([0, 7])
                    self.moved_squares.append([3, 7])
                elif start_x - end_x == -2:
                    self.board[7][7] = Piece()
                    self.board[5][7] = Piece('black', 'rook')
                    self.castling[1] = [False, False]
                    self.black_pieces.append([5, 7])
                    self.black_pieces.remove([7, 7])
                    self.deleted_squares.append([7, 7])
                    self.moved_squares.append([5, 7])
        self.board[start_x][start_y] = Piece()
        self.board[end_x][end_y] = piece

        if self.turn == 'white':
            self.white_pieces.remove(start)
            self.white_pieces.append(end)
            if end in self.black_pieces:
                self.black_pieces.remove(end)
            self.turn = 'black'

            check = self.is_in_check('black')
            legal_moves = self.has_legal_moves()
            if check:
                self.check_square = self.black_king
                if not legal_moves:
                    self.status = 'White Wins!'
            else:
                self.check_square = []
                if not legal_moves:
                    self.status = 'Draw'
        else:
            self.black_pieces.remove(start)
            self.black_pieces.append(end)
            if end in self.white_pieces:
                self.white_pieces.remove(end)
            self.turn = 'white'

            check = self.is_in_check('white')
            legal_moves = self.has_legal_moves()
            if check:
                self.check_square = self.white_king
                if not legal_moves:
                    self.status = 'Black Wins!'
            else:
                self.check_square = []
                if not legal_moves:
                    self.status = 'Draw'

    def is_in_check(self, color):
        if color == 'white':
            return self.white_king in self.get_attacking('black')
        else:
            return self.black_king in self.get_attacking('white')
