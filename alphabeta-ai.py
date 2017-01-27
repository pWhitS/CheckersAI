from checkers import *


def basic_evaluate():
	pass

def is_terminal():
	pass


def get_all_next_moves(board, move_depth):
	board_copy = board.copy()

	first_order = None
	if move_depth == 0:
		first_order = [-1, 1, -2, 2]
	else:
		first_order = [-2, 2]

	move_set = []
	all_pieces = board.getAllPlayerPieces(board.getCurrentPlayerId())

	for piece in all_pieces:
		prow = piece[0]
		pcol = piece[1]
		for i in first_order:
			for j in first_order:
				candidate_move_token = board._getTokenFromPoint( (prow+i, pcol+j) )
				if candidate_move_token == "-1-1":
					continue
				piece_token = board._getTokenFromPoint(piece)
				move_set.append( (piece_token, candidate_move_token) )

	for move in move_set:
		if board._isJump(move[0], move[1]) is None:
			continue

		try:
			board_copy.doMove(move[0], [move[1]])
			move_set = move_set + get_all_next_moves(board_copy, move_depth+1)
			print("MS: ", move_set)
		except InvalidMoveException:
			pass

	return move_set


def minimax(board, depth, eval_fn = basic_evaluate,
			get_next_moves_fn = get_all_next_moves,
			is_terminal_fn = is_terminal,
			verbose = True):
	best_val = None

	print(board)
	print(get_all_next_moves(board, 0))




def alpha_beta_search():
	pass




board = CheckersBoard()
minimax(board, depth=4)




