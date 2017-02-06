from checkers import *
from util import *
from random import randint


class Node():

	def __init__(self, _board, _play, _parent=None):
		self.board = _board
		self.play = _play
		self.currentPlayerId = self.board.getCurrentPlayerId()
		self.wins = 0
		self.playouts = 0
		self.parent = _parent
		self.nextlist = []

	def append_leaf(self, node):
		self.nextlist.append(node)

	def __str__(self):
		rstr = "\n"
		rstr += "Player: " + str(self.currentPlayerId) + " - Play: " + str(self.play) + " - "
		rstr += "Ratio: " + str(self.wins) + "/" + str(self.playouts)
		return rstr

	def __repr__(self):
		return self.__str__()


def combine_move_sets(move_set_1, move_set_2):
	if not move_set_2:
		return []

	ms1_piece, ms1_move = None, None
	ms2_piece, ms2_move = None, None
	new_move_set = list(move_set_1)
	new_move = None

	for i, m1 in enumerate(move_set_1):
		ms1_piece = m1[0]
		ms1_move = m1[1]
		for j, m2 in enumerate(move_set_2):
			ms2_piece = m2[0]
			ms2_move = m2[1]

			if ms1_move == ms2_piece:
				new_jump = "%s %s" % (ms1_move, ms2_move)
				new_move = (ms1_piece, new_jump)
				new_move_set.append(new_move)

	return new_move_set


def get_all_next_moves(board, move_depth, recursive=True):
	first_order = [] # Single space moves don't apply for multiple jumps
	second_order = [-2, 2]
	# Allow single space moves only for the first move
	if move_depth == 0: 
		first_order = [-1, 1]

	move_orders = [first_order, second_order]
	move_set = []
	all_pieces = board.getAllPlayerPieces(board.getCurrentPlayerId())

	# Get all possible move positions from current position (unfiltered)
	for piece in all_pieces:
		prow = piece[0]
		pcol = piece[1]
		for order in move_orders:
			for i in order:
				for j in order:
					candidate_move_token = board._getTokenFromPoint( (prow+i, pcol+j) )
					if candidate_move_token == "-1-1":
						continue
					piece_token = board._getTokenFromPoint(piece)
					move_set.append( (piece_token, candidate_move_token) )

	# Check for multiple jumps
	for move in move_set:
		if board._isJump(move[0], move[1]) is None:
			continue

		try:
			new_board = board.doMove(move[0], [move[1]])
			new_board.currentPlayer = board.currentPlayer
			if recursive:
				move_set = combine_move_sets(list(move_set), get_all_next_moves(new_board, move_depth+1))
		except InvalidMoveException:
			continue
	
	return move_set


def get_moves_helper(board, tree_depth, move_depth=0):
	board_copy = board.copy()
	move_set = get_all_next_moves(board_copy, move_depth)

	for piece, move in move_set:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass


def playlist_to_generator(board, play_list):
	for piece, move in play_list:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass	


def is_terminal(node, num_moves):
	return node.board.isGameOver() or (num_moves == 0)


def propigate_wins(cur_node):

	while cur_node.parent != None and cur_node.parent.parent != None:
		parent = cur_node.parent
		cur_node = cur_node.parent.parent		
		


def mcts_playout(root_node, get_next_moves_fn):
	cur_node = root_node
	cur_node.playouts += 1
	depth = 0
	next_moves = get_next_moves_fn(cur_node.board, 0)

	while not is_terminal(cur_node, len(next_moves)):
		# Move has not been extended
		if len(cur_node.nextlist) == 0:
			for play, new_board in playlist_to_generator(cur_node.board, next_moves):
				new_node = Node(new_board, play, cur_node)
				cur_node.append_leaf(new_node)

			midx = randint(0, len(cur_node.nextlist)-1)
			cur_node = cur_node.nextlist[midx]

			next_moves = get_next_moves_fn(cur_node.board, 0)
		else:
			cur_node = cur_node.nextlist[randint(0, len(cur_node.nextlist)-1)]

			# zero_playout_list = []
			# for i, n in enumerate(cur_node.nextlist):
			# 	if n.playouts == 0:
			# 		zero_playout_list.append(i)

			# if len(zero_playout_list) > 0:
			# 	zero_idx = zero_playout_list[randint(0, len(zero_playout_list)-1)]
			# 	cur_node = cur_node.nextlist[zero_idx]
			# else:
			# 	# use biased random to chose node
			# 	pass

		cur_node.playouts += 1
		depth += 1

	print(cur_node.board)
	#if cur_node.board.isWin():
	propigate_wins(cur_node)
	print(cur_node)
	print(depth)

	
	

def monte_carlo_search(board, get_next_moves_fn, iter=10000, verbose=True):
	root_node = Node(board, (None, None))

	next_moves = get_next_moves_fn(board, 0)

	mcts_playout(root_node, get_next_moves_fn)
	print(root_node)
		

	



if __name__ == "__main__":

	mcts_player = lambda board: monte_carlo_search(board, get_all_next_moves)

	run_game(mcts_player, human_player)







