import tkinter as tk
from tkinter import font as tkfont
from PIL import ImageTk
from game import Game
import threading
import socket

MSG_LEN = 4
FORMAT = 'utf-8'
PORT = 5054

SEND_CHALLENGE = '8000'
RECEIVE_CHALLENGE = '8001'
ACCEPT_CHALLENGE = '8002'
ACKNOWLEDGE_CHALLENGE = '8003'
RESIGN = '8004'
DRAW = '8005'
DISCONNECT = '8006'


class App:
    def __init__(self):
        self.game = None
        self.in_progress = False
        self.piece_images = None
        self.root = tk.Tk()
        self.root.title('Chess Online')
        self.root.geometry('800x500+150+150')
        self.player = 'white'
        self.load_pieces()

        self.connector = None
        self.conn_type = None
        self.client_conn = None
        self.searching = False
        self.offered = False

        self.board_image = None
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
        self.ip_entry.place(x=520, y=100, height=25, width=140)

        button_font = tkfont.Font(size=12)
        find_match_button = tk.Button(self.root, text='Find Match', bd=1,
                                      command=self.create_client, font=button_font)
        find_match_button.place(x=670, y=100)
        open_search_button = tk.Button(self.root, text='Open Search', bd=1,
                                       command=self.create_server, font=button_font)
        open_search_button.place(x=555, y=150)
        new_game_button = tk.Button(self.root, text='New Game', bd=1, command=self.offer_game, font=button_font)
        new_game_button.place(x=670, y=150)
        resign_button = tk.Button(self.root, text='Resign', bd=1, font=button_font)
        resign_button.place(x=595, y=250)
        draw_button = tk.Button(self.root, text='Offer Draw', bd=1, font=button_font)
        draw_button.place(x=670, y=250)

        self.status_font = tkfont.Font(size=14)
        self.status_text = tk.StringVar()
        self.status_text.set('')
        self.status_label = tk.Label(self.root, textvariable=self.status_text, font=self.status_font)
        self.status_label.place(x=525, y=200)

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.render_board()

        self.root.mainloop()

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

    def new_game(self):
        self.game = Game()
        self.in_progress = True
        self.render_all_pieces()
        self.selection_square = None
        self.render_indicators()
        self.render_status()

    def render_board(self):
        self.board_image = tk.PhotoImage(file='images/chessboard.png')
        self.canvas.create_image(0, 0, image=self.board_image, anchor='nw')

    def render_indicators(self):
        self.canvas.delete('indicator')
        if self.game.check_square:
            self.canvas.create_image(self.game.check_square[0] * 60 + 30,
                                     (7 - self.game.check_square[1]) * 60 + 30, image=self.threaten, tags='indicator')

        if self.selection_square:
            self.canvas.create_image(self.selection_square[0] * 60 + 30,
                                     (7 - self.selection_square[1]) * 60 + 30, image=self.selection, tags='indicator')

    def render_moved_pieces(self):
        for x, y in self.game.deleted_squares:
            self.canvas.delete(f'p{x}{y}')
        for x, y in self.game.moved_squares:
            self.render_piece(x, y)
        self.game.deleted_squares = []
        self.game.moved_squares = []

    def render_all_pieces(self):
        self.canvas.delete('piece')
        for x, y in self.game.white_pieces:
            self.render_piece(x, y)
        for x, y in self.game.black_pieces:
            self.render_piece(x, y)

    def render_piece(self, x, y):
        piece = self.game.board[x][y]
        if piece.color == 'white':
            if piece.piece == 'pawn':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][0], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'knight':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][1], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'bishop':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][2], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'rook':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][3], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'queen':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][4], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'king':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[0][5], tags=('piece', f'p{x}{y}'))
        elif piece.color == 'black':
            if piece.piece == 'pawn':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][0], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'knight':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][1], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'bishop':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][2], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'rook':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][3], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'queen':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][4], tags=('piece', f'p{x}{y}'))
            elif piece.piece == 'king':
                self.canvas.create_image(30+60*x, 450-60*y, image=self.piece_images[1][5], tags=('piece', f'p{x}{y}'))

    # TODO: show connection statuses
    def render_status(self):
        if self.game:
            self.status_text.set(self.game.status)
        else:
            self.status_text.set('a')

    def interact(self, event):
        if not self.in_progress:
            return

        selection_square = [event.x // 60, 7 - (event.y // 60)]
        if (self.game.turn == 'white' and selection_square in self.game.white_pieces) or \
           (self.game.turn == 'black' and selection_square in self.game.black_pieces):
            self.selection_square = selection_square
            self.render_indicators()
            self.render_piece(selection_square[0], selection_square[1])
            return
        elif self.selection_square:
            if self.game.is_legal(self.selection_square, selection_square):
                if self.conn_type == 'server':
                    self.make_move_as_server(self.selection_square, selection_square)
                else:
                    self.make_move_as_client(self.selection_square, selection_square)
                self.move(self.selection_square, selection_square)
                if self.game.status != '':
                    self.in_progress = False
            else:
                self.selection_square = []
                self.render_indicators()

    def move(self, start, end):
        self.game.move(start, end)
        self.selection_square = []
        self.render_indicators()
        self.render_moved_pieces()
        self.render_status()

    def offer_game(self):
        self.offered = True

    # run when 'Find Match' is pressed; creates a server to listen for potential matches
    def create_server(self):
        self.conn_type = 'server'
        server_ip = socket.gethostbyname(socket.gethostname())
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector.bind((server_ip, PORT))
        self.connector.listen()
        thread = threading.Thread(target=self.open_connection)
        thread.start()

    # listens for potential matches; when one is found, accepts the connection
    def open_connection(self):
        self.searching = True
        self.status_text.set('Accepting Matches')
        while True:
            self.client_conn, _ = self.connector.accept()
            self.accept_connection(self.client_conn)

    # returns message to challenge sender
    def accept_connection(self, conn):
        self.status_text.set('You received a challenge')
        connected = True
        while connected:
            message = conn.recv(MSG_LEN).decode(FORMAT)
            if message == SEND_CHALLENGE:
                conn.send(RECEIVE_CHALLENGE.encode(FORMAT))
                while connected:
                    if self.offered:
                        self.offered = False
                        conn.send(ACCEPT_CHALLENGE.encode(FORMAT))
                        self.new_game()
                        self.status_text.set('Game started')
                        self.render_all_pieces()

    def make_move_as_server(self, start, end):
        print(f'made move from {start} to {end}')
        print(self.client_conn)
        self.client_conn.send(f'{start[0]}{start[1]}{end[0]}{end[1]}'.encode(FORMAT))
        thread = threading.Thread(target=self.wait_as_server)
        thread.start()

    def wait_as_server(self):
        message = self.client_conn.recv(MSG_LEN).decode(FORMAT)
        self.move([int(message[0]), int(message[1])], [int(message[2]), int(message[3])])
        print(message)

    def create_client(self):
        self.conn_type = 'client'
        server_ip = socket.gethostbyname(socket.gethostname())
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector.connect((server_ip, PORT))
        thread = threading.Thread(target=self.connect_to_server)
        thread.start()

    def connect_to_server(self):
        self.connector.send(SEND_CHALLENGE.encode(FORMAT))
        connected = True
        while connected:
            message = self.connector.recv(MSG_LEN).decode(FORMAT)
            if message == RECEIVE_CHALLENGE:
                self.status_text.set('Your challenge was received')
            if message == ACCEPT_CHALLENGE:
                self.new_game()
                self.status_text.set('Game started')
                self.wait_as_client()

    def make_move_as_client(self, start, end):
        print(f'made move from {start} to {end}')
        self.connector.send(f'{start[0]}{start[1]}{end[0]}{end[1]}'.encode(FORMAT))
        thread = threading.Thread(target=self.wait_as_client)
        thread.start()

    def wait_as_client(self):
        print('receiving from server')
        print(self.connector)
        message = self.connector.recv(MSG_LEN).decode(FORMAT)
        self.move([int(message[0]), int(message[1])], [int(message[2]), int(message[3])])
        print(message)
        print('done receiving')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
