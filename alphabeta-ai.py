from checkers import *


def basic_evaluate():
	pass

def is_terminal():
	pass

# ('D2', 'B4')  
# ('B4', 'D6 F4')
def combine_move_sets(move_set_1, move_set_2):
	if not move_set_2:
		return []

	# print("ms1: ", move_set_1)
	# print("ms2: ", move_set_2)

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
				new_move = "%s %s" % (ms1_move, ms2_move)
				new_move = (ms1_piece, new_move)
				new_move_set.append(new_move)

	#print("NMS:", new_move_set)
	return new_move_set


def get_all_next_moves(board, move_depth):
	board_copy = board.copy()

	first_order = [] # Single space moves don't apply for multiple jumps
	second_order = [-2, 2]
	# Allow single space moves for the first move
	if move_depth == 0: 
		first_order = [-1, 1]

	move_orders = [first_order, second_order]
	move_set = []
	all_pieces = board.getAllPlayerPieces(board.getCurrentPlayerId())
	if move_depth > 0:
		print("AP:", move_depth, all_pieces)

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
			new_board = board_copy.doMove(move[0], [move[1]])
			new_board.currentPlayer = board_copy.currentPlayer
			move_set = combine_move_sets(list(move_set), get_all_next_moves(new_board, move_depth+1))
		except InvalidMoveException:
			continue
	
	return move_set


def minimax(board, depth, eval_fn = basic_evaluate,
			get_next_moves_fn = get_all_next_moves,
			is_terminal_fn = is_terminal,
			verbose = True):
	best_val = None

	print(board)
	print("-->", get_all_next_moves(board, 0))

	for move in get_all_next_moves(board, 0):
		piece = move[0]
		move_set = move[1]
		new_board = None

		try:
			new_board = board.doMove(piece, move_set)
		except InvalidMoveException:
			pass

		print(new_board)





def alpha_beta_search():
	pass




board = CheckersBoard()
minimax(board, depth=4)




