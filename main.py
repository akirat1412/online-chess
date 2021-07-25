import tkinter as tk
from tkinter import font as tkfont
from PIL import ImageTk
from threading import Thread
import socket
import random
import urllib
from urllib.request import urlopen

from game import Game

MSG_LEN = 4
FORMAT = 'utf-8'
SERVER_PORT = 5050
CLIENT_PORT = SERVER_PORT + 1

INIT = '8000'
START_CONN = '8001'
ACK_CONN = '8002'
START_AS_WHITE = '8004'
START_AS_BLACK = '8005'
RESIGN = '8006'
ACK_RESIGN = '8007'
DRAW = '8008'
ACK_DRAW = '8009'
DISCONNECT = '8010'


class App:
    def __init__(self):
        self.game = None
        self.in_progress = False
        self.root = tk.Tk()
        self.root.title('Chess Online')
        self.root.geometry('800x500+150+150')
        self.player = None
        self.selection_square = []
        self.draw_offer = [False, False]

        self.piece_images = None
        self.load_pieces()
        board_image = tk.PhotoImage(file='images/chessboard.png')
        self.threaten = tk.PhotoImage(file='images/threaten.png')
        self.selection = tk.PhotoImage(file='images/selection.png')

        self.connector = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.searching = False
        self.connected = False
        self.conn_type = None
        self.opponent_addr = None

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.canvas.create_image(0, 0, image=board_image, anchor='nw')

        title_label = tk.Label(self.root, text='Chess Online', font=tkfont.Font(size=24))
        title_label.place(x=550, y=50)
        font_12 = tkfont.Font(size=12)
        ip_label = tk.Label(self.root, text='Your IP is: ', font=font_12)
        ip_label.place(x=550, y=110)
        self.my_ip = urllib.request.urlopen('https://api.ipify.org').read().decode(FORMAT)
        my_ip_string_var = tk.StringVar()
        my_ip_string_var.set(self.my_ip)
        my_ip_entry = tk.Entry(self.root, textvariable=my_ip_string_var, font=font_12)
        my_ip_entry.place(x=630, y=110, width=120)
        self.ip_string_var = tk.StringVar()
        ip_entry = tk.Entry(self.root, textvariable=self.ip_string_var, font=font_12)
        ip_entry.place(x=500, y=152, height=25, width=140)
        find_match_button = tk.Button(self.root, text='Match', bd=1,
                                      command=self.find_match, font=font_12)
        find_match_button.place(x=650, y=150)
        close_connection_button = tk.Button(self.root, text='Cancel', bd=1,
                                            command=self.stop_search, font=font_12)
        close_connection_button.place(x=705, y=150)
        self.draw_button = tk.Button(self.root, text='Offer Draw', bd=1, command=self.offer_draw, font=font_12)
        self.draw_button.place(x=680, y=300)
        resign_button = tk.Button(self.root, text='Resign', bd=1, command=self.resign, font=font_12)
        resign_button.place(x=620, y=300)
        title_label = tk.Label(self.root, text='Images from Wikimedia', font=font_12)
        title_label.place(x=600, y=450)
        self.status_text = tk.StringVar()
        self.status_text.set('')
        status_label = tk.Label(self.root, textvariable=self.status_text, font=tkfont.Font(size=14))
        status_label.place(x=525, y=250)

        # currently using to test everything else
        self.error_text = tk.StringVar()
        self.error_text.set('')
        error_label = tk.Label(self.root, textvariable=self.error_text, font=tkfont.Font(size=14))
        error_label.place(x=525, y=225)

        if random.random() < 0.5:
            self.conn_type = 'server'
            self.opponent_addr = ('192.168.0.4', CLIENT_PORT)
            self.error_text.set('server')
            self.connector.bind(('', SERVER_PORT))
        else:
            self.conn_type = 'client'
            self.opponent_addr = ('192.168.0.4', SERVER_PORT)
            self.error_text.set('client')
            self.connector.bind(('', CLIENT_PORT))

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
        self.render_selection()
        self.render_check()
        if self.player == 'white':
            self.status_text.set('Your turn')
        else:
            self.status_text.set('Your opponent\'s turn')

    # when game ends, disconnects both players
    def end_game(self):
        self.in_progress = False
        self.searching = False
        self.connected = False
        self.conn_type = None
        self.draw_offer = [False, False]
        self.draw_button['text'] = 'Offer Draw'

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
                msg = f'{self.selection_square[0]}{self.selection_square[1]}{selection_square[0]}{selection_square[1]}'
                self.send_message(msg)
                self.move(self.selection_square, selection_square)
                if self.in_progress:
                    self.status_text.set('Your opponent\'s turn')
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

    def find_match(self):
        if self.in_progress:
            self.status_text.set('Already in a game')
        elif self.searching:
            self.status_text.set('Already searching')
        elif self.connected:
            self.status_text.set('Already connected')
        else:
            opp_ip = self.ip_string_var.get()

            # TODO: Uncomment this to test network connection
            # if self.my_ip < opp_ip:
            #     self.conn_type = 'server'
            #     self.opponent_addr = (opp_ip, CLIENT_PORT)
            # else:
            #     self.conn_type = 'client'
            #     self.opponent_addr = (opp_ip, SERVER_PORT)

            Thread(target=self.connect_to_opponent).start()
            Thread(target=self.receive_message).start()

    def connect_to_opponent(self):
        self.searching = True
        self.status_text.set('Searching for opponent')
        while self.searching:
            self.send_message(INIT)

        if self.connected:
            self.send_message(START_CONN)

    # causes player to lose the game by resignation
    def resign(self):
        if not self.in_progress:
            self.status_text.set('You are not in a game')
            return
        self.send_message(RESIGN)
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
        self.send_message(DRAW)
        if not self.draw_offer[0] and not self.draw_offer[1]:
            self.draw_offer[0] = True
            self.status_text.set('You offered a draw')
            self.draw_button['text'] = 'Cancel Draw'
        elif self.draw_offer[0]:
            self.draw_offer[0] = False
            self.status_text.set('You canceled your draw offer')
            self.draw_button['text'] = 'Offer Draw'
        elif self.draw_offer[1]:
            self.status_text.set('Draw by agreement')
            self.end_game()

    # sends move/other messages to other player
    def send_message(self, message):
        print(self.opponent_addr)
        self.connector.sendto(message.encode(FORMAT), self.opponent_addr)
        self.error_text.set(f'sent message {message}')

    # always running while game is in progress; receives messages from other player
    def receive_message(self):
        while self.searching or self.connected:
            data, addr = self.connector.recvfrom(4)
            message = data.decode(FORMAT)

            if not message:
                return
            elif message == INIT:
                if self.searching:
                    self.connected = True
                    self.searching = False
            elif message == START_CONN:
                self.send_message(ACK_CONN)
            elif message == ACK_CONN:
                if random.random() < 0.5:
                    self.player = 'white'
                    self.send_message(START_AS_BLACK)
                else:
                    self.player = 'black'
                    self.send_message(START_AS_WHITE)
                self.new_game()
            elif message == START_AS_WHITE:
                self.player = 'white'
                self.new_game()
            elif message == START_AS_BLACK:
                self.player = 'black'
                self.new_game()
            elif message == DRAW:
                if not self.draw_offer[0] and not self.draw_offer[1]:
                    self.draw_offer[1] = True
                    self.status_text.set('You were offered a draw')
                    self.draw_button['text'] = 'Accept Draw'
                elif self.draw_offer[0]:
                    self.status_text.set('Draw by agreement')
                    # if self.conn_type == 'client':
                    #     self.send_message(ACK_DRAW)
                    self.end_game()
                elif self.draw_offer[1]:
                    self.draw_offer[1] = False
                    self.status_text.set('The draw offer was canceled')
                    self.draw_button['text'] = 'Offer Draw'
            elif message == RESIGN:
                # if self.conn_type == 'client':
                #     self.send_message(ACK_RESIGN)
                self.end_game()
                if self.player == 'white':
                    self.status_text.set('White wins by resignation')
                else:
                    self.status_text.set('Black wins by resignation')
            elif message == ACK_RESIGN:
                self.end_game()
            else:
                self.move([int(message[0]), int(message[1])], [int(message[2]), int(message[3])])
                if self.in_progress:
                    self.status_text.set('Your turn')

    # disconnects player as long as they are not in a game
    def stop_search(self):
        if self.in_progress:
            self.status_text.set('You are already in a game')
        elif self.connected:
            self.status_text.set('You are already connected')
        elif self.searching:

            self.searching = False
            self.connected = False
            self.send_message(DISCONNECT)
            self.status_text.set('You disconnected')
            if self.conn_type == 'server':
                self.connector.close()
        else:
            self.status_text.set('You stopped your search')
        self.conn_type = None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
