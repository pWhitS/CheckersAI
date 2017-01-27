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

	orig_piece = None
	orig_move = None

	for i, m1 in enumerate(move_set_1):
		orig_piece = m1[0]
		orig_move = m1[1]


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
		print("AP:", all_pieces)

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
	move_set_copy = list(move_set) #copy so we can modify move_set in the loop
	for move in move_set_copy:
		if board._isJump(move[0], move[1]) is None:
			move_set.remove(move) #removes non-jump moves from the set of moves
			continue

		try:
			new_board = board_copy.doMove(move[0], [move[1]])
			new_board.currentPlayer = board_copy.currentPlayer
			#move_set = combine_move_sets(move_set, get_all_next_moves(new_board, move_depth+1))
			print("MS:", get_all_next_moves(new_board, move_depth+1))
		except InvalidMoveException:
			move_set.remove(move) #removes invalid moves from the set of moves
			continue
	
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




