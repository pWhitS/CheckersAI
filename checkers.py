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


class CheckersBoard(obejct):
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
                             1: unicodedata.lookup("WHITE SMILING FACE"),
                             2: unicodedata.lookup("BLACK SMILING FACE"),
                             3: unicodedata.lookup("BLACK SQUARE") }

    def __init__(self, _boardArray=None, _currentPlayer=1):
    	if _boardArray is None:
    		self.boardArray = ( ( 3, 0, 3, 0, 3, 0, 3, 0 ),
    					   		( 0, 3, 0, 3, 0, 3, 0, 3 ),
    					   		( 3, 0, 3, 0, 3, 0, 3, 0 ),
    					   		( 0, 3, 0, 3, 0, 3, 0, 3 ),
    					   		( 3, 0, 3, 0, 3, 0, 3, 0 ),
    					   		( 0, 3, 0, 3, 0, 3, 0, 3 ),
    					   		( 3, 0, 3, 0, 3, 0, 3, 0 ),
    					   		( 0, 3, 0, 3, 0, 3, 0, 3 ), )
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


    def doMove(self, piece, move):
    	doMove(self, piece[0], piece[1], move[0], move[1])


    def doMove(self, prow, pcol, mrow, mcol):
    	# Execute the specified move as the specified player.
        # Return a new board with the result.
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
        newBoard[prow][pcol] = 3
        newBoard[mrow][mcol] = playerId

        #Make the board immutable again
        newBoard = tuple( map(tuple, newBoard) )

        return CheckersBoard(newBoard, self.getOtherPlayerId())









