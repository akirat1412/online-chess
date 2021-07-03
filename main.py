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
        self.selection_id = -1

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.place(x=10, y=10)
        self.canvas.bind('<Button-1>', self.interact)
        self.render_board()
        self.render_pieces()
        self.root.mainloop()

    def render_board(self):
        self.board_image = tk.PhotoImage(file='images/chessboard.png')
        self.canvas.create_image(0, 0, image=self.board_image, anchor='nw')

    def render_pieces(self):
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
            self.canvas.create_image(30 + 60 * y, 450 - 60 * x, image=self.piece_images[x][y])

    def interact(self, event):
        board_x = (event.x // 60) * 60 + 30
        board_y = (event.y // 60) * 60 + 30
        self.selection = tk.PhotoImage(file='images/selection.png')
        self.selection_id = self.canvas.create_image(board_x, board_y, image=self.selection)
        self.render_pieces()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    App()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
