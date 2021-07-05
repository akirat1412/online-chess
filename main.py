import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
from game import Game


class App:
    def __init__(self):
        self.game = None
        self.in_progress = False
        self.piece_images = [[None for _ in range(8)] for _ in range(8)]
        self.root = tk.Tk()
        self.root.title('Chess Online')
        self.root.geometry('800x500+150+150')

        self.board_image = None
        self.threaten = None
        self.selection = None
        self.selection_square = []

        button_font = tkfont.Font(size=12)
        new_game_button = tk.Button(self.root, text='New Game', bd=1, width=9, height=2, command=self.new_game)
        new_game_button['font'] = button_font
        new_game_button.place(x=600, y=100)

        status_font = tkfont.Font(size=18)
        status_text = tk.Label(self.root, text='hi', font=status_font)
        status_text.place(x=600, y=200)

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.render_board()

        self.root.mainloop()

    def new_game(self):
        self.game = Game()
        self.in_progress = True
        self.render_pieces()

    def render_board(self):
        self.board_image = tk.PhotoImage(file='images/chessboard.png')
        self.canvas.create_image(0, 0, image=self.board_image, anchor='nw')

    def render_indicators(self):
        if self.game.check_square:
            self.threaten = tk.PhotoImage(file='images/threaten.png')
            self.canvas.create_image(self.game.check_square[0] * 60 + 30,
                                     (7 - self.game.check_square[1]) * 60 + 30, image=self.threaten)
        else:
            self.threaten = None

        if self.selection_square:
            self.selection = tk.PhotoImage(file='images/selection.png')
            self.canvas.create_image(self.selection_square[0] * 60 + 30,
                                     (7 - self.selection_square[1]) * 60 + 30, image=self.selection)
        else:
            self.selection = None

    def render_pieces(self):
        self.piece_images = [[None for _ in range(8)] for _ in range(8)]
        for x, y in self.game.white_pieces:
            self.render_piece(x, y)
        for x, y in self.game.black_pieces:
            self.render_piece(x, y)

    def render_piece(self, x, y):
        piece = self.game.board[x][y]
        if piece.color is None:
            return
        else:
            piece_file = 'images/' + piece.color + '_' + piece.piece + '.png'
            self.piece_images[x][y] = ImageTk.PhotoImage(file=piece_file)
            self.canvas.create_image(30 + 60 * x, 450 - 60 * y, image=self.piece_images[x][y])

    def interact(self, event):
        if not self.in_progress:
            return

        selection_square = [event.x // 60, 7 - (event.y // 60)]

        if (self.game.turn == 'white' and selection_square in self.game.white_pieces) or \
           (self.game.turn == 'black' and selection_square in self.game.black_pieces):
            self.selection_square = selection_square
        elif self.selection_square:
            if self.game.is_legal(self.selection_square, selection_square):
                self.game.move(self.selection_square, selection_square)
            self.selection_square = []

        self.render_indicators()
        self.render_pieces()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
