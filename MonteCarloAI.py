from checkers import *
from util import *
from random import randint
from math import sqrt, log
from time import time

from AlphaBetaAI import *


VERY_VERBOSE = True

class Node():

	def __init__(self, _board, _play, _parent=None, _wins=0, _playouts=0, _nextlist=None):
		self.board = _board
		self.play = _play
		self.currentPlayerId = self.board.getCurrentPlayerId()
		self.wins = _wins
		self.playouts = _playouts
		self.parent = _parent
		if _nextlist is None:
			self.nextlist = []
		else:
			self.nextlist = _nextlist

	def append_leaf(self, node):
		self.nextlist.append(node)

	def copy(self):
		return Node(self.board, self.play, self.parent, self.wins, self.playouts, self.nextlist)

	def ratio(self):
		return str(self.wins) + "/" + str(self.playouts)

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


def is_terminal(node, depth):
	return node.board.isGameOver() or (depth == 0)


def propigate_wins(cur_node):
	cur_node.wins += 1
	while cur_node.parent != None and cur_node.parent.parent != None:
		parent = cur_node.parent
		cur_node = cur_node.parent.parent
		cur_node.wins += 1	

		
def get_ucb_max(cur_node):
	# UCB Formula: 
	# ri + sqrt(((ln P) / pi) * min(0.25, (ri - ri^2 + sqrt(2 * (ln P) / pi))))
	ucb_max = 0
	ucb_cur = 0
	max_node = cur_node.nextlist[0]

	for i, candidate_node in enumerate(cur_node.nextlist):
		ri = candidate_node.wins / float(candidate_node.playouts)
		P = cur_node.playouts # parent of candidate_node
		pi = candidate_node.playouts

		ucb_cur = ri + sqrt(log(P)/pi) * min(0.25, (ri - ri**2 + sqrt(2*log(P) / pi)))
		if ucb_cur > ucb_max:
			ucb_max = ucb_cur
			max_node = candidate_node

	return max_node


def mcts_playout(root_node, get_next_moves_fn, depth=25):
	cur_node = root_node
	cur_node.playouts += 1
	is_forced_loss = False

	while not is_terminal(cur_node, depth) or is_forced_loss:
		# Move has not been extended
		if len(cur_node.nextlist) == 0:
			next_moves = get_next_moves_fn(cur_node.board, 0)

			for play, new_board in playlist_to_generator(cur_node.board, next_moves):
				new_node = Node(new_board, play, cur_node)
				cur_node.append_leaf(new_node)

			# This is a loss for the current player
			if len(cur_node.nextlist) == 0:
				is_forced_loss = True
				break

			midx = randint(0, len(cur_node.nextlist)-1)
			cur_node = cur_node.nextlist[midx]
		else:
			zero_playout_list = []
			for i, n in enumerate(cur_node.nextlist):
				if n.playouts == 0:
					zero_playout_list.append(i)

			if len(zero_playout_list) > 0:
				# Pick at random, if never before extended
				zero_idx = zero_playout_list[randint(0, len(zero_playout_list)-1)]
				cur_node = cur_node.nextlist[zero_idx]
			else: 
				# Use a biased random choice. (UCB1-TUNED Monte-Carlo)
				cur_node = get_ucb_max(cur_node)

		cur_node.playouts += 1
		depth -= 1


	#print(depth)
	#print(root_node)
	winner = cur_node.board.isWin()
	if winner:
		#print("WIN!", "depth:", depth, "- player:", winner)
		#print(cur_node.board)
		propigate_wins(cur_node)

	elif is_forced_loss:
		#print("WIN!", "depth:", depth-1, "player:", cur_node.parent.board.getCurrentPlayerId())
		#print(cur_node.parent.board)
		propigate_wins(cur_node)

	
	

def monte_carlo_search(board, get_next_moves_fn, timeout=10, verbose=True):
	root_node = Node(board, (None, None))

	next_moves = get_next_moves_fn(board, 0)

	end_time = time() + timeout
	latest_root = root_node.copy()
	iters = 0

	while time() < end_time:
		mcts_playout(root_node, get_next_moves_fn)
		latest_root = root_node.copy()
		iters += 1

	if verbose and VERY_VERBOSE:
		print("iters:", iters)
		print(latest_root)
		print(latest_root.nextlist)

	wmax = 0
	wcur = 0
	max_node = root_node.nextlist[0]
	for i, node in enumerate(root_node.nextlist):
		wcur = node.wins
		if wcur > wmax:
			wmax = wcur
			max_node = node

	if verbose:
		print("Iterations:", iters, " -  MCTS-UCT  Move:", str(max_node.play), "- Ratio:", max_node.ratio())

	return max_node.play

	
def double_up(board):
	if sum(board.getPieceCount()) < 8:
		ai_type = randint(0,1)
	else:
		ai_type = 1

	if ai_type == 0:
		print("MCTS")
		return monte_carlo_search(board, get_all_next_moves, timeout=15)
	else:
		print("Alpha-Beta")
		return progressive_deepener(board,
									  search_fn=alpha_beta,
									  eval_fn=basic_eval_memoized,
									  get_next_moves_fn=get_ordered_moves_helper,
									  timeout=5)




if __name__ == "__main__":

	mcts_player = lambda board: monte_carlo_search(board, get_all_next_moves)

	ab_player_pd = lambda board: progressive_deepener(board,
													  search_fn=alpha_beta,
													  eval_fn=basic_eval_memoized,
													  get_next_moves_fn=get_ordered_moves_helper,
													  timeout=5)
	double_player = lambda board: double_up(board)


	run_game(double_player, ab_player_pd)







