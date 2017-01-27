from checkers import *


def basic_evaluate(board):
	return 1


def is_terminal(depth, board):
	return (depth <= 0) or board.isGameOver()


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
	
	for piece, move in move_set:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass


def minimax_search(board, depth, eval_fn,
				   get_next_moves_fn = get_all_next_moves,
				   is_terminal_fn = is_terminal):
	if is_terminal_fn(depth, board):
		return eval_fn(board)

	best_val = None

	for move, new_board in get_all_next_moves(board, 0):
		val = -1 * minimax_search(new_board, depth-1, eval_fn,
								  get_next_moves_fn,
								  is_terminal_fn)

		if best_val is None or val > best_val:
			best_val = val

	return val


def minimax(board, depth, eval_fn = basic_evaluate,
			get_next_moves_fn = get_all_next_moves,
			is_terminal_fn = is_terminal,
			verbose = True):
	best_val = None

	for move, new_board in get_all_next_moves(board, 0):
		val = -1 * minimax_search(new_board, depth-1, eval_fn,
								  get_next_moves_fn,
								  is_terminal_fn)

		if best_val is None or val > best_val[0]:
			best_val = (val, move, new_board)

	return best_val[1] #return the move





def alpha_beta_search():
	pass



if __name__ == "__main__":
	basic_player = lambda board: minimax(board, depth=4, eval_fn=basic_evaluate)
	
	run_game(basic_player, human_player)




