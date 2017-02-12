from checkers import *
from util import *
from math import sqrt


VERY_VERBOSE = False

WIN_SCORE = 1024  # 1000 + (Max piece type score)
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


def euclidean_distance(p1, p2):
	return sqrt( (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 )

# Computer an aggression factor scaled on player advantage
# If no advantage exists, aggression == 0
def aggression_scorer(board, p1_men, p1_kings, p2_men, p2_kings):
	agro_score = 0
	total_pieces = p1_men + p1_kings + p2_men + p2_kings

	if total_pieces >= 12:
		print("0")
		return agro_score # no aggression bonus

	total_p1 = p1_men + p1_kings
	total_p2 = p2_men + p2_kings

	# positive = player1 advantage, negative = player2 advantage
	advantage = total_p1 - total_p2 # total piece advantage
	advantage += p1_kings - p2_kings # king advantage is double counted

	# No aggression for no advantage
	if advantage > 0 and board.getCurrentPlayerId() == 2:
		return agro_score
	if advantage < 0 and board.getCurrentPlayerId() == 1:
		return agro_score
	if advantage == 0:
		return agro_score

	piece_locations = board.getPieceLocations()	
	p1list = piece_locations[1]
	p2list = piece_locations[2]

	aggregate_distance = 0
	for p1 in p1list:
		for p2 in p2list:
			aggregate_distance += euclidean_distance(p1, p2)

	modifier = 1
	if advantage < 0:
		modifier = -1

	# Aggression = Advantage over Average distance
	average_distance = aggregate_distance / (total_p1*total_p2)
	agro_score = modifier * (abs(advantage) / average_distance)

	#print("agro:", round(agro_score))
	return round(agro_score) 


def basic_evaluate(board):
	score = 0

	p1_men, p2_men, p1_kings, p2_kings = board.getPieceConfig()
	num_possible_moves = avaliable_moves(board)

	if board.isGameOver() or (num_possible_moves == 0):
		# Draw counter runs out
		if board.isDraw():
			return DRAW_SCORE

		if board.getCurrentPlayerId() == 1:
			return (LOSS_SCORE - board.getDrawCounter()) + (p2_men + p2_kings)
		else:
			return (LOSS_SCORE - board.getDrawCounter()) + (p1_men + p1_kings)

	score += num_possible_moves
	score += piece_type_scorer(board.getCurrentPlayerId(), p1_men, p1_kings, p2_men, p2_kings)
	score += positional_scorer(board)
	score += aggression_scorer(board, p1_men, p1_kings, p2_men, p2_kings)

	return score


@memoize
def basic_eval_memoized(board):
	return basic_evaluate(board)


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


def get_moves_helper(board, eval_fn, tree_depth, move_depth=0):
	board_copy = board.copy()
	move_set = get_all_next_moves(board_copy, move_depth)

	for piece, move in move_set:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass


# This routine only works with the single process alpha-beta
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


# Recursive Alpha-Beta branching and pruning
def alpha_beta_search(board, depth, eval_fn,
					  parent_alpha, parent_beta,
					  get_next_moves_fn = get_moves_helper,
					  is_terminal_fn = is_terminal):
	# Return board evaluation if end game or max depth is reached
	if is_terminal_fn(depth, board):
		abval = eval_fn(board)
		return (abval, abval)

	alpha = -parent_beta
	beta = -parent_alpha

	for move, new_board in get_next_moves_fn(board, eval_fn, depth):
		if alpha >= beta:
			break

		vals = alpha_beta_search(new_board, depth-1, eval_fn,
								 alpha, beta,
								 get_next_moves_fn,
								 is_terminal_fn)

		new_alpha, new_beta = (-vals[1], -vals[0]) 

		if new_beta > alpha:
			alpha = new_beta
	
	# No avaliable moves. 
	if alpha == NEG_INFINITY:
		alpha = eval_fn(board)  # Evaluate as loss for the current player

	return (alpha, beta)


# Starts the recursive alpha-beta search tree
def alpha_beta(board, depth, eval_fn = basic_evaluate,
					  get_next_moves_fn = get_moves_helper,
					  is_terminal_fn = is_terminal,
					  verbose = True):
	alpha = NEG_INFINITY
	beta = INFINITY
	best_move = None

	for move, new_board in get_next_moves_fn(board, eval_fn, depth):
		if alpha >= beta:
			break
		#print(move)
		vals = alpha_beta_search(new_board, depth-1, eval_fn,
								 alpha, beta,
								 get_next_moves_fn,
								 is_terminal_fn)

		new_alpha, new_beta = (-vals[1], -vals[0])

		if verbose and VERY_VERBOSE:
			print("Potential Move: ", move, "- Score:", new_beta)

		if new_beta > alpha:
			alpha = new_beta
			best_move = (alpha, beta, move, new_board)

	# Player cannot move and must conceed the game. 
	if best_move is None:
		best_move = (LOSS_SCORE, LOSS_SCORE, ("-1-1", "-1-1"), board)

	if verbose and depth < 15:
		print("Depth:", depth, " -  ALPHA-BETA  Move:", str(best_move[2]), "- Rating:", str(best_move[0]))

	return best_move[2]




if __name__ == "__main__":
	#basic_evaluate = memoize(basic_evaluate)

	ab_player = lambda board: alpha_beta(board, depth=3, eval_fn=basic_evaluate)

	ab_player_pd = lambda board: progressive_deepener(board,
													  search_fn=alpha_beta,
													  eval_fn=basic_eval_memoized,
													  get_next_moves_fn=get_ordered_moves_helper,
													  timeout=5)


	#run_game(ab_player, ab_player)
	#run_game(human_player, ab_player_pd)

	#run_game(ab_player_pd, ab_player_pd)

	run_game(human_player, ab_player_pd)






