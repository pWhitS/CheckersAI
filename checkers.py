import unicodedata
import sys


class InvalidMoveException(Exception):
	""" Exception raised if someone tries to make an invalid move """
	def __init__(self, _move, _board):
		"""
		'board' is the board on which the movement took place;
		'move' is the move to which an addition was attempted
		"""
		self.move = _move
		self.board = _board

	def __str__(self):
		return "InvalidMoveException: " + str(self.move) + "\n" + str(self._board)

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
	"""

	board_symbol_mapping = { 0: u' ',
							 1: unicodedata.lookup("LARGE RED CIRCLE"),
							 2: unicodedata.lookup("MEDIUM WHITE CIRCLE"),
							 3: unicodedata.lookup("BLACK LARGE SQUARE") }

	def __init__(self, _boardArray=None, _currentPlayer=1):
		if _boardArray is None:
			self.boardArray = ( ( 3, 2, 3, 2, 3, 2, 3, 2 ),
								( 2, 3, 2, 3, 2, 3, 2, 3 ),
								( 3, 2, 3, 2, 3, 2, 3, 2 ),
								( 0, 3, 0, 3, 0, 3, 0, 3 ),
								( 3, 0, 3, 0, 3, 0, 3, 0 ),
								( 1, 3, 1, 3, 1, 3, 1, 3 ),
								( 3, 1, 3, 1, 3, 1, 3, 1 ),
								( 1, 3, 1, 3, 1, 3, 1, 3 ), )
		else:
			# store an immutable copy
			self.boardArray = tuple( map(tuple, _boardArray) )

		self.currentPlayer = _currentPlayer
		self.boardWidth = 8
		self.boardHeight = 8


	def getCurrentPlayerId(self):
		return self.currentPlayer


	def getOtherPlayerId(self):
		if self.getCurrentPlayerId() == 1:
			return 2
		else:
			return 1


	def getBoardArray(self):
		return self.boardArray


	def getCell(self, row, col):
		# return player id in the cell
		# if empty return 0 or 3
		return self.boardArray[row][col]


	def _getGamePiecePoint(self, token):
		# Interprets tokens as: (column, Row)
		# Returns traditional: (row, column)
		colstr = "ABCDEFGH"
		print(token)

		row = int(token[1])	
		col = colstr.find(token[0].upper())
		
		return (row, col)


	def doMove(self, piece, move):
		# Execute the specified move as the specified player.
		# Return a new board with the result.  
		prow, pcol = self._getGamePiecePoint(piece)
		mrow, mcol = self._getGamePiecePoint(move) 

		playerId = self.getCurrentPlayerId() 

		#Series of checks to ensure the move is valid
		if prow < 0 or prow > self.boardHeight:
			raise InvalidMoveException()
		if pcol < 0 or pcol > self.boardWidth:
			raise InvalidMoveException()
		if self.getCell(prow, pcol) != playerId:
			raise InvalidMoveException()

		if mrow < 0 or mrow > self.boardHeight:
			raise InvalidMoveException()
		if mcol < 0 or mcol > self.boardWidth:
			raise InvalidMoveException()

		newBoard = list( map(list, self.getBoardArray()) )
		newBoard[prow][pcol] = 0
		newBoard[mrow][mcol] = playerId

		#Make the board immutable again
		newBoard = tuple( map(tuple, newBoard) )

		return CheckersBoard(newBoard, self.getOtherPlayerId())


	def isWin(self):
		whitePieces, blackPieces, total = self.getPieceCount()

		if whitePieces == 0:
			return 2
		if blackPieces == 0:
			return 1

		return 0


	def copy(self):
		return CheckersBoard(newBoard, self.getCurrentPlayerId())


	def getPieceCount(self):
		black = 0
		white = 0

		for i in range(self.boardWidth):
			for j in range(self.boardHeight):
				pid = self.getCell(i, j)
				if pid == 1:
					white += 1
				elif pid == 2:
					black += 1

		return (white, black, white+black)


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
	pass


if __name__ == "__main__":
	cb = CheckersBoard()
	print(cb)
	print(cb.doMove("A5", "B4"))


