from checkers import *
from util import *


class Node():

	def __init__(self, _move, _board):
		self.move = _move
		self.board = _board
		self.wins = 0
		self.losses = 0



def monte_carlo_search(board, get_next_moves_fn, verbose=True):
	pass



if __name__ == "__main__":

	mcts_player = lambda board: monte_carlo_search(board)







