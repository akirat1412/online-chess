import tkinter as tk
from tkinter import font as tkfont
from PIL import ImageTk
from game import Game
import threading
import socket
import random

MSG_LEN = 4
FORMAT = 'utf-8'
PORT = 5054

SEND_CHALLENGE = '8000'
RECEIVE_CHALLENGE = '8001'
ACCEPT_CHALLENGE = '8002'
ACKNOWLEDGE_CHALLENGE = '8003'
WHITE = '8004'
BLACK = '8005'
RESIGN = '8006'
DRAW = '8007'
DISCONNECT = '8008'


class App:
    def __init__(self):
        self.game = None
        self.in_progress = False
        self.piece_images = None
        self.root = tk.Tk()
        self.root.title('Chess Online')
        self.root.geometry('800x500+150+150')
        self.player = None
        self.load_pieces()

        self.connected = False
        self.connector = None
        self.conn_type = None
        self.client_conn = None
        self.offered = False

        self.board_image = tk.PhotoImage(file='images/chessboard.png')
        self.threaten = tk.PhotoImage(file='images/threaten.png')
        self.selection = tk.PhotoImage(file='images/selection.png')
        self.selection_square = []

        TITLE_TEXT = 'Online Chess'
        TITLE_FONT = tkfont.Font(size=24)
        TITLE_LABEL = tk.Label(self.root, text=TITLE_TEXT, font=TITLE_FONT)
        TITLE_LABEL.place(x=550, y=50)

        self.ip_string_var = tk.StringVar()
        IP_FONT = tkfont.Font(size=12)
        self.ip_entry = tk.Entry(self.root, textvariable=self.ip_string_var, font=IP_FONT)
        self.ip_entry.place(x=530, y=100, height=25, width=140)

        button_font = tkfont.Font(size=12)
        find_match_button = tk.Button(self.root, text='Find Match', bd=1,
                                      command=self.create_client, font=button_font)
        find_match_button.place(x=680, y=100)
        close_connection_button = tk.Button(self.root, text='Stop Search', bd=1,
                                            command=self.stop_search, font=button_font)
        close_connection_button.place(x=680, y=150)
        open_search_button = tk.Button(self.root, text='Open Search', bd=1,
                                       command=self.create_server, font=button_font)
        open_search_button.place(x=565, y=150)
        new_game_button = tk.Button(self.root, text='New Game', bd=1, command=self.offer_game, font=button_font)
        new_game_button.place(x=530, y=250)
        draw_button = tk.Button(self.root, text='Offer Draw', bd=1, command=self.offer_draw, font=button_font)
        draw_button.place(x=680, y=250)
        resign_button = tk.Button(self.root, text='Resign', bd=1, command=self.resign, font=button_font)
        resign_button.place(x=620, y=250)

        self.draw_offer = [False, False]
        self.status_font = tkfont.Font(size=14)
        self.status_text = tk.StringVar()
        self.status_text.set('')
        self.status_label = tk.Label(self.root, textvariable=self.status_text, font=self.status_font)
        self.status_label.place(x=525, y=200)

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.canvas.create_image(0, 0, image=self.board_image, anchor='nw')

        self.root.mainloop()

    # load image files into variables for rendering
    def load_pieces(self):
        self.piece_images = [[], []]
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_pawn.png'))
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_knight.png'))
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_bishop.png'))
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_rook.png'))
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_queen.png'))
        self.piece_images[0].append(ImageTk.PhotoImage(file='images/white_king.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_pawn.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_knight.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_bishop.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_rook.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_queen.png'))
        self.piece_images[1].append(ImageTk.PhotoImage(file='images/black_king.png'))

    # starts a new game
    def new_game(self):
        self.game = Game()
        self.in_progress = True
        self.render_all_pieces()
        self.selection_square = None
        self.status_text.set('')
        self.render_selection()
        self.render_check()

    # when game ends, disconnects both players
    def end_game(self):
        self.in_progress = False
        if self.conn_type == 'server':
            self.client_conn.close()
        self.connected = False
        self.conn_type = None
        self.connector = None
        self.client_conn = None

    # when player selects a piece, renders yellow square behind it
    def render_selection(self):
        self.canvas.delete('selection')
        if self.selection_square:
            if self.player == 'white':
                selection_x = self.selection_square[0]
                selection_y = self.selection_square[1]
            else:
                selection_x = 7 - self.selection_square[0]
                selection_y = 7 - self.selection_square[1]
            self.canvas.create_image(selection_x * 60 + 30,
                                     (7 - selection_y) * 60 + 30, image=self.selection, tags='selection')

    # when a king is in check, renders red square behind it
    def render_check(self):
        self.canvas.delete('check')
        if self.game.check_square:
            if self.player == 'white':
                check_x = self.game.check_square[0]
                check_y = self.game.check_square[1]
            else:
                check_x = 7 - self.game.check_square[0]
                check_y = 7 - self.game.check_square[1]
            self.canvas.create_image(check_x * 60 + 30,
                                     (7 - check_y) * 60 + 30, image=self.threaten, tags='check')

    # updates piece rendering according to what pieces moved/were taken
    def render_moved_pieces(self):
        for x, y in self.game.deleted_squares:
            self.canvas.delete(f'p{x}{y}')
        for x, y in self.game.moved_squares:
            self.render_piece(x, y)
        self.game.deleted_squares = []
        self.game.moved_squares = []

    # renders all pieces at the start of the game
    def render_all_pieces(self):
        self.canvas.delete('piece')
        for x, y in self.game.white_pieces:
            self.render_piece(x, y)
        for x, y in self.game.black_pieces:
            self.render_piece(x, y)

    # helper function that renders a single piece on the given square
    def render_piece(self, x, y):
        piece = self.game.board[x][y]
        x_real = x
        y_real = y
        if self.player == 'black':
            x = 7 - x
            y = 7 - y

        if piece.color == 'white':
            if piece.piece == 'pawn':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][0],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'knight':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][1],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'bishop':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][2],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'rook':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][3],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'queen':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][4],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'king':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[0][5],
                                         tags=('piece', f'p{x_real}{y_real}'))
        elif piece.color == 'black':
            if piece.piece == 'pawn':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][0],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'knight':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][1],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'bishop':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][2],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'rook':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][3],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'queen':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][4],
                                         tags=('piece', f'p{x_real}{y_real}'))
            elif piece.piece == 'king':
                self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[1][5],
                                         tags=('piece', f'p{x_real}{y_real}'))

    # when a player clicks on a square, renders a selection square, moves a piece, etc
    def interact(self, event):
        if not self.in_progress:
            return
        if self.player == 'white':
            selection_square = [event.x // 60, 7 - (event.y // 60)]
        else:
            selection_square = [7 - (event.x // 60), event.y // 60]
        if self.player == self.game.turn and \
                ((self.game.turn == 'white' and selection_square in self.game.white_pieces) or
                 (self.game.turn == 'black' and selection_square in self.game.black_pieces)):
            self.selection_square = selection_square
            self.render_selection()
            self.render_piece(selection_square[0], selection_square[1])
            return
        elif self.selection_square:
            if self.game.is_legal(self.selection_square, selection_square):
                self.send_message(self.selection_square, selection_square, None)
                self.move(self.selection_square, selection_square)
            else:
                self.selection_square = []
                self.render_selection()

    # moves a piece
    def move(self, start, end):
        self.game.move(start, end)
        self.selection_square = []
        self.render_selection()
        self.render_check()
        self.render_moved_pieces()
        self.status_text.set(self.game.status)
        if self.game.status != '':
            self.end_game()

    # when server receives a challenge, can start new game
    def offer_game(self):
        if self.in_progress:
            self.status_text.set('You are already in a game')
        elif not self.connected:
            self.status_text.set('You do not have an opponent')
        elif self.conn_type == 'client':
            self.status_text.set('Waiting for opponent to accept')
        else:
            self.offered = True

    # runs when 'Find Match' is pressed; creates a server to listen for potential matches
    def create_server(self):
        if self.in_progress:
            self.status_text.set('You are already in a game')
            return
        self.conn_type = 'server'
        server_ip = socket.gethostbyname(socket.gethostname())
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector.bind((server_ip, PORT))
        self.connector.listen()
        thread = threading.Thread(target=self.open_connection)
        thread.start()

    # listens for potential matches; when one is found, accepts the connection
    def open_connection(self):
        self.status_text.set('Accepting Matches')
        self.client_conn, _ = self.connector.accept()
        if self.connector:
            self.connected = True
            self.accept_connection()
        else:
            self.conn_type = None
            self.client_conn = None

    # returns message to challenge sender
    def accept_connection(self):
        self.status_text.set('You received a challenge')
        message = self.client_conn.recv(MSG_LEN).decode(FORMAT)
        if message == SEND_CHALLENGE:
            thread = threading.Thread(target=self.receive_message)
            thread.start()
            self.send_message(None, None, RECEIVE_CHALLENGE)
            while self.connected:
                if self.offered:
                    self.offered = False
                    self.send_message(None, None, ACCEPT_CHALLENGE)
                    if random.random() < 0.5:
                        self.player = 'white'
                        self.send_message(None, None, BLACK)
                    else:
                        self.player = 'black'
                        self.send_message(None, None, WHITE)
                    self.new_game()
                    self.status_text.set('Game started')
                    self.render_all_pieces()
                    break

    # causes player to lose the game by resignation
    def resign(self):
        if not self.in_progress:
            self.status_text.set('You are not in a game')
            return
        self.send_message(None, None, RESIGN)
        self.end_game()
        if self.player == 'white':
            self.status_text.set('Black wins by resignation')
        else:
            self.status_text.set('White wins by resignation')

    # offers draw to other player; if other player also offered, ends game in draw
    def offer_draw(self):
        if not self.in_progress:
            self.status_text.set('You are not in a game')
            return
        self.send_message(None, None, DRAW)
        self.draw_offer[0] = True
        if self.draw_offer[1]:
            self.status_text.set('Draw by agreement')
            self.end_game()
        else:
            self.status_text.set('You offered a draw')

    # sends move/other messages to other player
    def send_message(self, start, end, other):
        if other:
            message = other.encode(FORMAT)
        else:
            message = f'{start[0]}{start[1]}{end[0]}{end[1]}'.encode(FORMAT)
        if self.conn_type == 'server':
            self.client_conn.send(message)
        else:
            self.connector.send(message)

    # always running while game is in progress; receives messages from other player
    def receive_message(self):
        while self.connected:
            if self.conn_type == 'server':
                message = self.client_conn.recv(MSG_LEN).decode(FORMAT)
            else:
                message = self.connector.recv(MSG_LEN).decode(FORMAT)
            if not message:
                return
            if message == DISCONNECT:
                self.status_text.set('Your opponent disconnected')
                if self.conn_type == 'server':
                    self.client_conn.close()
                self.connected = False
                self.connector = None
                self.conn_type = None
                self.client_conn = None
            elif message == DRAW:
                self.draw_offer[1] = True
                if self.draw_offer[0]:
                    self.status_text.set('Draw by agreement')
                    self.end_game()
                else:
                    self.status_text.set('You were offered a draw')
            elif message == RESIGN:
                self.end_game()
                if self.player == 'white':
                    self.status_text.set('White wins by resignation')
                else:
                    self.status_text.set('Black wins by resignation')
            else:
                self.move([int(message[0]), int(message[1])], [int(message[2]), int(message[3])])

    # disconnects player as long as they are not in a game
    def stop_search(self):
        if self.in_progress:
            self.status_text.set('You are already in a game')
            return
        elif self.connected:
            self.connected = False
            self.send_message(None, None, DISCONNECT)
            self.status_text.set('You disconnected')
            if self.conn_type == 'server':
                self.client_conn.close()
        else:
            self.status_text.set('You stopped your search')
        self.connector = None
        self.conn_type = None
        self.client_conn = None

    # runs when 'Find Match' is pressed; will try to connect with IP address given; if successful, run connect_to_server
    def create_client(self):
        if self.in_progress:
            self.status_text.set('You are already in a game')
            return
        try:
            self.conn_type = 'client'
            server_ip = socket.gethostbyname(socket.gethostname())
            self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connector.connect((server_ip, PORT))
            thread = threading.Thread(target=self.connect_to_server)
            thread.start()
        except ConnectionRefusedError:
            self.status_text.set('Opponent not found')

    # waits for server to start game
    def connect_to_server(self):
        self.send_message(None, None, SEND_CHALLENGE)
        self.connected = True
        while self.connected:
            message = self.connector.recv(MSG_LEN).decode(FORMAT)
            if message == RECEIVE_CHALLENGE:
                self.status_text.set('Your challenge was received')
            elif message == ACCEPT_CHALLENGE:
                message = self.connector.recv(MSG_LEN).decode(FORMAT)
                if message == WHITE:
                    self.player = 'white'
                else:
                    self.player = 'black'
                self.new_game()
                self.status_text.set('Game started')
                self.receive_message()
            elif message == DISCONNECT:
                self.status_text.set('Your opponent disconnected')
                self.connected = False
                self.connector = None
                self.conn_type = None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
