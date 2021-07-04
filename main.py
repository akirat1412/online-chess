import tkinter as tk
from PIL import Image, ImageTk
from game import Game


class App:
    def __init__(self):
        self.game = Game()
        self.piece_images = [[None for _ in range(8)] for _ in range(8)]
        self.root = tk.Tk()
        self.root.title('Chess Online')
        self.root.geometry('800x500+150+150')

        self.board_image = None
        self.selection = None
        self.selection_square = []

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.render_board()
        self.render_pieces()
        self.root.mainloop()

    def render_board(self):
        self.board_image = tk.PhotoImage(file='images/chessboard.png')
        self.canvas.create_image(0, 0, image=self.board_image, anchor='nw')

    def render_selection(self):
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
        selection_square = [event.x // 60, 7 - (event.y // 60)]

        if (self.game.turn == 'white' and selection_square in self.game.white_pieces) or \
           (self.game.turn == 'black' and selection_square in self.game.black_pieces):
            self.selection_square = selection_square
        elif self.selection_square:
            if self.game.is_legal(self.selection_square, selection_square):
                self.game.move(self.selection_square, selection_square)
            self.selection_square = []

        self.render_selection()
        self.render_pieces()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
