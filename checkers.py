import unicodedata
import sys

VERY_VERBOSE = False

class InvalidMoveException(Exception):
	""" Exception raised if someone tries to make an invalid move """
	def __init__(self, _piece, _move, _board):
		"""
		'board' is the board on which the movement took place;
		'move' is the move to which an addition was attempted
		"""
		self.piece = _piece
		self.move = _move
		self.board = _board

	def __str__(self):
		return "InvalidMoveException: (%s, %s) \n%s" % (str(self.piece), str(self.move), str(self.board))

	def __repr__(self):
		return self.__str__()


class CheckersBoard(object):
	""" Represents a Checkers Board

	A Checkers board is a matrix, laid out as follows:

		 A B C D E F G H
	   0 * - * - * - * -
	   1 - * - * - * - *
	   2 * - * - * - * -
	   3 - * - * - * - *
	   4 * - * - * - * -
	   5 - * - * - * - *
	   6 * - * - * - * -
	   7 - * - * - * - *

	Dashes (-) are white spaces
	Asterics (*) are black spaces

	Checkers boards should be immutable to prevent accidental modification
	#"LARGE BLUE CIRCLE"
	"""

	board_symbol_mapping = { 0: u' ',
							 1: unicodedata.lookup("LARGE RED CIRCLE"),  #normal 'white' piece
							 2: unicodedata.lookup("MEDIUM WHITE CIRCLE"), #normal 'black' piece
							 3: unicodedata.lookup("HEAVY LARGE CIRCLE"), #king 'white' piece
							 4: unicodedata.lookup("LARGE CIRCLE"), #king 'black' piece
							 5: unicodedata.lookup("BLACK LARGE SQUARE")} 

	def __init__(self, _boardArray=None, _currentPlayer=1, _drawCounter=100):
		if _boardArray is None:
			# Normal Starting Board
			self.boardArray = ( ( 5, 2, 5, 2, 5, 2, 5, 2 ),
								( 2, 5, 2, 5, 2, 5, 2, 5 ),
								( 5, 2, 5, 2, 5, 2, 5, 2 ),
								( 0, 5, 0, 5, 0, 5, 0, 5 ),
								( 5, 0, 5, 0, 5, 0, 5, 0 ),
								( 1, 5, 1, 5, 1, 5, 1, 5 ),
								( 5, 1, 5, 1, 5, 1, 5, 1 ),
								( 1, 5, 1, 5, 1, 5, 1, 5 ), )
			## TEST BOARDS ##
			# 1 piece each, opposite ends
			# self.boardArray = ( ( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 1, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 2, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ), )
			# King, tripple jump
			# self.boardArray = ( ( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 3, 5, 0, 5, 0 ),
			# 					( 0, 5, 2, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 2, 5, 2, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ), )
			# Player 2, close win
			# self.boardArray = ( ( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 2, 5, 0, 5, 2 ),
			# 					( 2, 5, 0, 5, 2, 5, 1, 5 ),
			# 					( 5, 2, 5, 0, 5, 1, 5, 2 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 4, 5, 0, 5, 0, 5, 0, 5 ), )
			# Almost certain draw
			# self.boardArray = ( ( 5, 3, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ),
			# 					( 5, 1, 5, 0, 5, 0, 5, 0 ),
			# 					( 0, 5, 0, 5, 2, 5, 2, 5 ),
			# 					( 5, 2, 5, 4, 5, 0, 5, 1 ),
			# 					( 4, 5, 4, 5, 0, 5, 4, 5 ), )
			# White victory through opponent moves 
			# self.boardArray = ( ( 5, 0, 5, 0, 5, 0, 5, 0 ),
			# 					( 2, 5, 2, 5, 2, 5, 2, 5 ),
			# 					( 5, 2, 5, 2, 5, 2, 5, 2 ),
			# 					( 1, 5, 1, 5, 1, 5, 1, 5 ),
			# 					( 5, 1, 5, 0, 5, 0, 5, 1 ),
			# 					( 0, 5, 4, 5, 2, 5, 0, 5 ),
			# 					( 5, 1, 5, 1, 5, 2, 5, 0 ),
			# 					( 0, 5, 0, 5, 0, 5, 0, 5 ), )
			# Tricky finish
			self.boardArray = ( ( 5, 3, 5, 0, 5, 0, 5, 0 ),
								( 0, 5, 0, 5, 0, 5, 0, 5 ),
								( 5, 0, 5, 0, 5, 0, 5, 0 ),
								( 2, 5, 4, 5, 0, 5, 2, 5 ),
								( 5, 0, 5, 0, 5, 0, 5, 0 ),
								( 0, 5, 0, 5, 0, 5, 0, 5 ),
								( 5, 2, 5, 0, 5, 0, 5, 2 ),
								( 4, 5, 0, 5, 0, 5, 0, 5 ), )

		else:
			# store an immutable copy
			self.boardArray = tuple( map(tuple, _boardArray) )

		self.currentPlayer = _currentPlayer
		self.boardWidth = 8
		self.boardHeight = 8
		self.drawCounter = _drawCounter  # After this many moves, consider the game a draw


	def getCurrentPlayerId(self):
		return self.currentPlayer


	def getCurrentPlayerPieceIds(self):
		if self.getCurrentPlayerId() == 1:
			return [1,3]
		else:
			return [2,4]


	def getOtherPlayerId(self):
		if self.getCurrentPlayerId() == 1:
			return 2
		else:
			return 1


	def getOtherPlayerPieceIds(self):
		if self.getOtherPlayerId() == 1:
			return [1,3]
		else:
			return [2,4]


	def getBoardArray(self):
		return self.boardArray


	def getCell(self, row, col):
		# return player id in the cell
		# if empty return 0 or 5
		return self.boardArray[row][col]


	def getDrawCounter(self):
		return self.drawCounter


	def kingMe(self, board, verbose=False):
		for col in range(self.boardWidth):
			# Player 1, non-king piece
			if board[0][col] == 1:
				board[0][col] = 3  # switch to king
				
			# Player 2, non-king piece
			if board[7][col] == 2: 
				board[7][col] = 4  # switch to king
			
		return board


	def _getPointFromToken(self, token):
		# Interprets tokens as: (column, Row)
		# Returns traditional: (row, column)
		colstr = "ABCDEFGH"
		row = int(token[1])	
		col = colstr.find(token[0].upper())
		return (row, col)


	def _getTokenFromPoint(self, point):
		# Returns a token on the board from a (row, col) point
		colstr = "ABCDEFGH"
		row, col = point

		if row < 0 or row >= self.boardHeight:
			return "-1-1"
		if col < 0 or col >= self.boardWidth: 
			return "-1-1"

		token = colstr[col]
		token += str(row)

		return token
	

	def _isJump(self, piece, move):
		prow, pcol = self._getPointFromToken(piece)
		mrow, mcol = self._getPointFromToken(move)

		rdelta = abs(mrow - prow)
		cdelta = abs(mcol - pcol)

		if rdelta <= 1 and cdelta <= 1:
			return None

		# Calculate position of jumped piece
		if mrow > prow: # Downward jump
			jumpPieceRow = prow + 1
		else: # Upward jump
			jumpPieceRow = prow - 1

		if mcol > pcol: # Right jump
			jumpPieceCol = pcol + 1
		else: # Left jump
			jumpPieceCol = pcol - 1

		return (jumpPieceRow, jumpPieceCol)


	def moveIsValid(self, piece, move, curBoard):
		if len(piece) != 2 or len(move) != 2:
			if VERY_VERBOSE:
				print("Rule Violation: 0")
			return False

		prow, pcol = self._getPointFromToken(piece)
		mrow, mcol = self._getPointFromToken(move)

		# Outside of the board checks
		if prow < 0 or prow >= self.boardHeight:
			if VERY_VERBOSE:
				print("Rule Violation: 1")
			return False
		if pcol < 0 or pcol >= self.boardWidth:
			if VERY_VERBOSE:
				print("Rule Violation: 2")
			return False	
		if mrow < 0 or mrow >= self.boardHeight:
			if VERY_VERBOSE:
				print("Rule Violation: 3")
			return False
		if mcol < 0 or mcol >= self.boardWidth:
			if VERY_VERBOSE:
				print("Rule Violation: 4")
			return False

		# Player slected a valid piece
		if curBoard[prow][pcol] not in self.getCurrentPlayerPieceIds():
			if VERY_VERBOSE:
				print("Rule Violation: 5")
			return False

		# Move point is not empty
		if curBoard[mrow][mcol] != 0:
			if VERY_VERBOSE:
				print("Rule Violation: 6")
			return False

		# Player 1 non-King pieces can only move down rows
		if curBoard[prow][pcol] == 1:
			if mrow >= prow:
				if VERY_VERBOSE:
					print("Rule Violation: 7")
				return False

		# Player 2 non-King pieces can only move up rows
		if curBoard[prow][pcol] == 2:
			if mrow <= prow:
				if VERY_VERBOSE:
					print("Rule Violation: 8")
				return False

		# Player must jump over an opponent piece
		if self._isJump(piece, move) != None:
			jrow, jcol = self._isJump(piece, move)
			if curBoard[jrow][jcol] not in self.getOtherPlayerPieceIds():
				if VERY_VERBOSE:
					print("Rule Violation: 9")
				return False

		return True


	def doMove(self, piece, moveset):
		# Execute the specified move as the specified player.
		# Return a new board with the result.  
		if len(moveset) == 0:
			raise InvalidMoveException(piece, moveset, self)

		if type(moveset) is not list:
			moveset = moveset.strip().split()

		newBoard = list( map(list, self.getBoardArray()) )

		for move in moveset:
			# Ensure multi-moves are jumps
			if len(moveset) > 1:
				if not self._isJump(piece, move):
					raise InvalidMoveException(piece, move, self)

			# Series of checks to ensure the move is valid
			if not self.moveIsValid(piece, move, newBoard):
				raise InvalidMoveException(piece, move, self)

			prow, pcol = self._getPointFromToken(piece)
			mrow, mcol = self._getPointFromToken(move) 
			pieceId = newBoard[prow][pcol]
			newBoard[prow][pcol] = 0
			newBoard[mrow][mcol] = pieceId

			# Performs a piece capture (jump)
			if self._isJump(piece, move):
				jrow, jcol = self._isJump(piece, move) 
				newBoard[jrow][jcol] = 0

			piece = self._getTokenFromPoint( (mrow, mcol) )

		#Check for new Kings
		newBoard = self.kingMe(newBoard)
		# Make the board immutable again
		newBoard = tuple( map(tuple, newBoard) )

		return CheckersBoard(newBoard, self.getOtherPlayerId(), self.drawCounter-1)


	def isWin(self):
		whitePieces, blackPieces = self.getPieceCount()
		if whitePieces == 0:
			return 2
		if blackPieces == 0:
			return 1
		return 0


	def isDraw(self):
		if self.drawCounter == 0:
			return True
		return False


	def isGameOver(self):
		if self.isWin() != 0:
			return True
		if self.isDraw():
			return True
		return False


	def copy(self):
		return CheckersBoard(self.getBoardArray(), self.getCurrentPlayerId(), self.drawCounter)


	def getPieceConfig(self):
		plist = [0, 0, 0, 0] # red, white, red king, white king

		for i in range(self.boardHeight):
			for j in range(self.boardWidth):
				pid = self.getCell(i, j)
				if pid == 0 or pid == 5:
					continue
				plist[pid-1] += 1

		return plist


	def getPieceCount(self):
		red = 0 
		white = 0 

		for i in range(self.boardHeight):
			for j in range(self.boardWidth):
				pid = self.getCell(i, j)
				if pid in [1, 3]:
					red += 1
				elif pid in [2, 4]:
					white += 1

		return (red, white)


	def getPieceLocations(self, reqToken=False):
		pdict = {1: [], 2: []}

		for i in range(self.boardHeight):
			for j in range(self.boardWidth):
				pid = self.getCell(i, j)
				if pid not in [0, 5]:
					loc = (i, j)
					if reqToken:
						loc = _getTokenFromPoint(loc)
				else:
					continue

				if pid in [1, 3]:
					pdict[1].append(loc)
				elif pid in [2, 4]:
					pdict[2].append(loc)

		return pdict


	def getAllPlayerPieces(self, playerid):
		pieceSet = []
		pid = 0

		if playerid == 1:
			pid = (1,3)
		else:
			pid = (2,4)

		for i in range(self.boardHeight):
			for j in range(self.boardWidth):
				if self.getCell(i, j) in pid:
					pieceSet.append( (i, j) )

		return pieceSet


	def __str__(self):
		""" Return a string representation of this board """
		retVal = [ "  " + '  '.join([str(x) for x in "ABCDEFGH"]) ]
		retVal += [ str(i) + ' ' + '  '.join([self.board_symbol_mapping[x] for x in row]) for i, row in enumerate(self.boardArray) ]
		return '\n' + '\n'.join(retVal) + '\n'


	def __repr__(self):
		""" The string representation of a board in the Python shell """
		return self.__str__()


	def __hash__(self):
		""" Determine the hash key of a board.  The hash key must be the same on any two identical boards. """
		return self.boardArray.__hash__()


	def __eq__(self, other):
		""" Determine whether two boards are equal. """
		return ( self.getBoardArray() == other.getBoardArray() )


class CheckersRunner(object):

	def __init__(self, player1_callback, player2_callback, _board=CheckersBoard()):
		self.board = _board
		self.player1_callback = player1_callback
		self.player2_callback = player2_callback


	def get_board(self):
		return self.board


	def run_game(self, verbose=True):
		player1 = (self.player1_callback, 1, self.board.board_symbol_mapping[1])
		player2 = (self.player2_callback, 2, self.board.board_symbol_mapping[2])

		is_player_win = False

		while not is_player_win and not self.board.isDraw():
			for callback, pid, symbol in (player1, player2):
				if verbose:
					print("\nPlayer %s's %s  Turn" % (pid, str(symbol)))
					print("Draw Counter:", self.board.drawCounter)
					print(str(self.board))

				is_still_moving = True

				while is_still_moving:
					try:
						new_move = callback(self.board.copy())
						print("\nPlayer %s %s  - Move: %s" % (pid, str(symbol), new_move))  

						game_piece, game_move = new_move
						if game_move == "-1-1":
							is_player_win = int("-%s" % (str(pid)))
						else:							
							self.board = self.board.doMove(game_piece, game_move)

						is_still_moving = False
					except InvalidMoveException as e:
						print(str(e))
						print("Illegal move attempted.  Please try again.")
						continue

				if self.board.isGameOver():
					is_player_win = self.board.isWin()
					break
				elif is_player_win < 0:
					break

		if (not is_player_win) and self.board.isDraw():
			print("It's a draw! No winner is declared.")
			print(str(self.board))
			return 0
		elif is_player_win < 0:
			print("Player %s concedes the match." % str(is_player_win)[1]) 
			print(str(self.board))
		else:
			is_player_win = self.board.isWin()
			print("win:", is_player_win)
			print(str(self.board))
			print(self.board.drawCounter)



def human_player(board):
	# A callback that asks the user what to do
	target_piece = None
	target_move = None

	while type(target_piece) != str and type(target_move) != str:
		target_piece = input("Pick a piece to move (A7): --> ")
		target_move = input("Pick a location to move (B6): --> ")
		try:
			target_piece = str(target_piece)
			target_move = str(target_move)
		except ValueError:
			print("Please specify a correctly formatted piece and move.")

	return (target_piece, target_move)


def run_game(player1, player2, board=CheckersBoard()):
	game = CheckersRunner(player1, player2, board)
	return game.run_game()


if __name__ == "__main__":
	# cb = CheckersBoard()
	# print(cb)
	# print(cb.doMove("A5", ["C3"]))

	run_game(human_player, human_player)


