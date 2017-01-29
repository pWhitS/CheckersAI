from checkers import *
from util import *
from multiprocessing import Pool


VERY_VERBOSE = False

WIN_SCORE = 1000
LOSS_SCORE = -WIN_SCORE
DRAW_SCORE = -900

def basic_evaluate(board):
	score = 0
	p1count, p2count = board.getPieceCount()

	if board.isGameOver():
		if board.getCurrentPlayerId() == 1:
			return (LOSS_SCORE + p1count) - p2count
		else:
			return (LOSS_SCORE + p2count) - p1count

	if board.getCurrentPlayerId() == 1:
		score += p1count * 5
		score -= p2count * 6
	else:
		score += p2count * 5
		score -= p1count * 6

	colscore = [1, 2, 2, 4, 4, 2, 2, 1]
	for row in range(board.boardWidth):
		for col in range(board.boardHeight):
			if board.getCell(row, col) in board.getCurrentPlayerPieceIds():
				score += colscore[col]
			elif board.getCell(row, col) in board.getOtherPlayerPieceIds():
				score += colscore[col]

	return score


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



def get_moves_helper(board, move_depth=0):
	move_set = get_all_next_moves(board, move_depth)

	for piece, move in move_set:
		try:
			yield ((piece, move), board.doMove(piece, move))
		except InvalidMoveException:
			pass


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

	for move, new_board in get_next_moves_fn(board):
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
		alpha = WIN_SCORE  # Evaluate as win for the previous player

	return (alpha, beta)


# Starts the recursive alpha-beta search tree
def alpha_beta(board, depth, eval_fn = basic_evaluate,
					  get_next_moves_fn = get_moves_helper,
					  is_terminal_fn = is_terminal,
					  verbose = True):
	alpha = NEG_INFINITY
	beta = INFINITY
	best_move = None

	for move, new_board in get_next_moves_fn(board):
		if alpha >= beta:
			break

		vals = alpha_beta_search(new_board, depth-1, eval_fn,
								 alpha, beta,
								 get_next_moves_fn,
								 is_terminal_fn)

		new_alpha, new_beta = (-vals[1], -vals[0])

		if VERY_VERBOSE:
			print("Potential Move: ", move, "- Score:", new_beta)

		if new_beta > alpha:
			alpha = new_beta
			best_move = (alpha, beta, move, new_board)

	# Player cannot move and must conceed the game. 
	if best_move is None:
		best_move = (LOSS_SCORE, ("-1-1", "-1-1"), board)

	if verbose and depth < 15:
		print("Depth:", depth, " -  ALPHA-BETA: Move:", str(best_move[2]), "- Rating:", str(best_move[0]))

	return best_move[2]



if __name__ == "__main__":
	basic_evaluate = memoize(basic_evaluate)


	ab_player = lambda board: alpha_beta(board, depth=4, eval_fn=basic_evaluate)

	ab_player_pd = lambda board: progressive_deepener(board,
													  search_fn=alpha_beta,
													  eval_fn=basic_evaluate,
													  get_next_moves_fn=get_moves_helper,
													  timeout=25)

	#run_game(basic_player_pd, basic_player_pd)
	#run_game(ab_player_pd, basic_player_pd)

	run_game(ab_player_pd, ab_player_pd)







