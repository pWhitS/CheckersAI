from checkers import *
from util import *
from multiprocessing import Pool


VERY_VERBOSE = False

WIN_SCORE = 1000
LOSS_SCORE = -WIN_SCORE
DRAW_SCORE = -900


def piece_type_scorer(cur_player, p1_men, p1_kings, p2_men, p2_kings):
	pt_score = 0
	multiplyer = 2

	if cur_player == 1:
		pt_score += p1_men * multiplyer
		pt_score += p1_kings * (multiplyer * 2)
		pt_score -= p2_men * multiplyer
		pt_score -= p2_kings * (multiplyer * 2)
	else:
		pt_score += p2_men * multiplyer
		pt_score += p2_kings * (multiplyer * 2)
		pt_score -= p1_men * multiplyer
		pt_score -= p1_kings * (multiplyer * 2)

	return pt_score


def positional_scorer(board):
	pscore = 0

	# Prefer pieces in the middle of the board
	matrix_score = [0, 1, 2, 2, 2, 2, 1, 0]
	for row in range(board.boardWidth):
		for col in range(board.boardHeight):
			if board.getCell(row, col) in board.getCurrentPlayerPieceIds():
				pscore += matrix_score[row]
				pscore += matrix_score[col]
			elif board.getCell(row, col) in board.getOtherPlayerPieceIds():
				pscore -= matrix_score[row]
				pscore -= matrix_score[col]

	return pscore


def avaliable_moves(board):
	move_orders = [[-1, 1], [-2, 2]]
	num_valid_moves = 0
	all_pieces = board.getAllPlayerPieces(board.getCurrentPlayerId())

	# Count all possible moves from current position
	for piece in all_pieces:
		prow = piece[0]
		pcol = piece[1]
		for order in move_orders:
			for i in order:
				for j in order:
					candidate_move_token = board._getTokenFromPoint( (prow+i, pcol+j) )
					piece_token = board._getTokenFromPoint( (prow, pcol) )
					try:
						board.doMove(piece_token, candidate_move_token)
					except InvalidMoveException:
						continue
					num_valid_moves += 1

	return num_valid_moves


def basic_evaluate(board):
	score = 0

	p1_men, p2_men, p1_kings, p2_kings = board.getPieceConfig()
	p1_tot = p1_men + p1_kings
	p2_tot = p2_men + p2_kings
	num_possible_moves = avaliable_moves(board)

	if board.isGameOver() or num_possible_moves == 0:
		if board.getCurrentPlayerId() == 1:
			return (LOSS_SCORE - board.getDrawCounter()) + p2_tot
		else:
			return (LOSS_SCORE - board.getDrawCounter()) + p1_tot

	score += num_possible_moves
	score += piece_type_scorer(board.getCurrentPlayerId(), p1_men, p1_kings, p2_tot, p2_kings)
	score += positional_scorer(board)

	return score


@memoize
def basic_eval_memoized(board):
	return basic_evaluate(board)


# Memoization for the top process
memo = MultiMemoize()
def multi_memo_eval_helper(board):
	if board in memo.multicache:
		return memo.multicache[board]
	else:
		val = basic_evaluate(board)
		memo.multicache[board] = val
		return val


def is_terminal(depth, board):
	return (depth <= 0) or board.isGameOver()


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


def get_ordered_moves_helper(board, eval_fn, tree_depth, move_depth=0):
	board_copy = board.copy()
	move_set = get_all_next_moves(board_copy, move_depth)

	# No evaluations have taken place for moves at depth 1
	if tree_depth == 1:
		for piece, move in move_set:
			try:
				yield ((piece, move), board.doMove(piece, move))
			except InvalidMoveException:
				pass
	else:
		board_value_list = []
		for i, play in enumerate(move_set):
			try:
				new_board = board_copy.doMove(play[0], play[1])
				val = eval_fn(new_board)
				board_value_list.append( (val, play, new_board) )
			except InvalidMoveException:
				pass

		board_value_list = sorted(board_value_list, key=lambda b: b[0])
		for bv in board_value_list:
			piece, move = bv[1]
			yield ((piece, move), bv[2])


def get_moves_multiproc_helper(board, move_depth=0):
	board_copy = board.copy()
	move_list = get_all_next_moves(board_copy, move_depth)
	yield_list = []
	temp_board = None

	for piece, move in move_list:
		try:
			temp_board = board.doMove(piece, move)
		except InvalidMoveException:
			continue

		yield_list.append( ((piece, move), temp_board) )

	return yield_list


def get_moves_helper(board, eval_fn, tree_depth, move_depth=0):
	board_copy = board.copy()
	move_set = get_all_next_moves(board_copy, move_depth)

	for piece, move in move_set:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass


# Recursive Alpha-Beta branching and pruning
def alpha_beta_search_mp(board, depth, eval_fn,
					     parent_alpha, parent_beta,
					     get_next_moves_fn = get_moves_helper,
					     is_terminal_fn = is_terminal):
	# Use the memoized evaluator for each subprocess
	eval_fn = basic_eval_memoized
	# Return board evaluation if end game or max depth is reached
	if is_terminal_fn(depth, board):
		abval = eval_fn(board)
		return (abval, abval)

	alpha = -parent_beta
	beta = -parent_alpha

	for move, new_board in get_next_moves_fn(board, eval_fn, depth):
		if alpha >= beta:
			break

		vals = alpha_beta_search_mp(new_board, depth-1, eval_fn,
								    alpha, beta,
								 	get_next_moves_fn,
								 	is_terminal_fn)

		new_alpha, new_beta = (-vals[1], -vals[0]) 

		if new_beta > alpha:
			alpha = new_beta
	
	# No avaliable moves. 
	if alpha == NEG_INFINITY:
		alpha = WIN_SCORE  # Evaluate as win for the previous player

	return (alpha, beta)


# Starts the recursive alpha-beta search tree
def alpha_beta_multiproc(board, depth, eval_fn = basic_evaluate,
					 	 get_next_moves_fn = get_moves_helper,
					  	 is_terminal_fn = is_terminal,
					  	 num_procs = 6,
					  	 verbose = True):
	alpha = NEG_INFINITY
	beta = INFINITY
	best_move = None

	# Default num_procs to 2 less than the number of cores
	ab_pool = Pool(processes=num_procs) 
	pool_args = []
	move_list = []

	# Collect the arguments for each process
	for move, new_board in get_next_moves_fn(board, multi_memo_eval_helper, depth):
		temp_arg = (new_board, depth-1, eval_fn, alpha, beta, get_next_moves_fn, is_terminal_fn)
		pool_args.append(temp_arg)
		move_list.append( (move, new_board) ) # Keep track of the moves and boards
	
	# Start the multiprocessor, and store the returned values
	vals_list = ab_pool.starmap(alpha_beta_search_mp, pool_args)
	ab_pool.close()  # Allow the subprocesses to terminate quickly
	ab_pool.join()  # Do not continue until all subprocesses finish
	
	# Find the highest scoring move
	for i, vals in enumerate(vals_list):
		new_alpha, new_beta = (-vals[1], -vals[0])
		new_move = move_list[i][0]
		new_board = move_list[i][1]
		# Cache the new_board score
		memo.multicache[new_board] = new_beta

		if verbose and VERY_VERBOSE:
			print("Potential Move: ", new_move, "- Score:", new_beta)

		if new_beta > alpha:
			alpha = new_beta
			best_move = (alpha, beta, new_move)

	# Player cannot move and must conceed the game. 
	if best_move is None:
		best_move = (LOSS_SCORE, LOSS_SCORE, ("-1-1", "-1-1"))

	if verbose and depth < 15:
		print("Depth:", depth, " -  ALPHA-BETA: Move:", str(best_move[2]), "- Rating:", str(best_move[0]))

	return best_move[2]



if __name__ == "__main__":
	mp_ab_player = lambda board: alpha_beta_multiproc(board, depth=3, eval_fn=basic_evaluate)

	mp_ab_player_pd = lambda board: progressive_deepener(board,
														 search_fn=alpha_beta_multiproc,
													  	 eval_fn=basic_evaluate,
													  	 get_next_moves_fn=get_ordered_moves_helper,
													  	 timeout=15)


	run_game(mp_ab_player, mp_ab_player)


