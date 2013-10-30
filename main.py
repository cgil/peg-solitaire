#!/usr/bin/env python
import sys
sys.setrecursionlimit(20000)

"""
	
	8x8 board - represented by 1 dimensional array
	-1 = blocked
	0 = hole
	1 = peg
	example board: 
	-1 -1  1  1  1 -1 -1 -1
	-1 -1  1  1  1 -1 -1 -1
	 1  1  1  1  1  1  1 -1
	 1  1  1  0  1  1  1 -1
	 1  1  1  1  1  1  1 -1
	-1 -1  1  1  1 -1 -1 -1
	-1 -1  1  1  1 -1 -1 -1
	-1 -1 -1 -1 -1 -1 -1 -1

"""
ROWS = COLS = 8
PEG = 1
HOLE = 0
BLOCK = -1
BADMOVES = {}
DEPTHLIMIT = 10000

class Moves(object):
	def __init__(self, moves = []):
		self.moves = moves
	def hash(self):
		movesId = sum(m.hash() for m in self.moves)
		return hash(movesId)
	def pop(self):	
		return self.moves.pop()
	def push(self, move):
		self.moves.append(move)
	def length(self):
		return len(self.moves)
	def __str__(self):
		return "Moves: has %s moves inside" % (self.length())



class Move(object):
	def __init__(self, row1, col1, row2, col2):
		self.start = {"row": row1, "col": col1}
		self.end = {"row": row2, "col": col2}
	def __repr__(self):
		return "<Move start.row:%s start.col:%s end.row:%s end.col:%s>" % (self.start["row"], self.start["col"], self.end["row"], self.end["col"])
	def __str__(self):
		return "Move (row,col): (%s,%s) --> (%s,%s)" % (self.start["row"], self.start["col"], self.end["row"], self.end["col"])
	def hash(self):
		moveId = "start.row:%s start.col:%s end.row:%s end.col:%s" % (self.start["row"], self.start["col"], self.end["row"], self.end["col"])
		return hash(moveId)


class Board(object):
	def __init__(self, rows, cols, verbal = True):
		board = []
		board.extend([-1,-1,-1,-1,-1,-1,-1,-1])
		board.extend([-1,-1, 1, 1, 1, 1,-1,-1])
		board.extend([-1,-1, 1, 1, 1, 1,-1,-1])
		board.extend([-1,-1, 1, 0, 1, 1,-1,-1])
		board.extend([-1,-1, 1, 1, 1, 1, 1,-1])
		board.extend([-1,-1, 1, 1, 1, 1, 1,-1])
		board.extend([-1,-1, 1, 1, 1, 1, 1,-1])
		board.extend([-1,-1,-1,-1,-1, -1,-1,-1])
		self.board = board
		self.show(verbal)
		if verbal:
			print "Initiated %s x %s board" % (rows, cols)

	def setElem(self, row, col, elem):
		self.board[row*(COLS) + col] = elem

	def getElem(self, row, col):
		return self.board[row*(COLS) + col]

	def show(self, verbal = True):
		if verbal:
			print "-"*40 + "\n"
			print "      ",
			for i in xrange(COLS):
				print "%3s" % (i),
			print "\n\n"
			for i in xrange(len(self.board)):
				if i % COLS == 0:
					print "%3s   " % ((i)/COLS),
				elem = self.board[i] == -1 and "x" or self.board[i]
				print "%3s" % (elem),
				if (i+1) % COLS == 0:
					print "\n"

	def move(self, move, verbal = True):
		if self.isValidMove(move):
			self.setElem(move.end["row"], move.end["col"], PEG)
			self.setElem(move.start["row"], move.start["col"], HOLE)
			midX = move.start["row"] + (move.end["row"] - move.start["row"])/2
			midY = move.start["col"] + (move.end["col"] - move.start["col"])/2
			self.setElem(midX, midY, HOLE)
			self.show(verbal)
			if verbal:
				print "Moved (row, col): (%s,%s) --> (%s,%s) \n" % (move.start["row"], move.start["col"], move.end["row"], move.end["col"])
		else:
			if verbal:
				print "Failed to Move (row, col): (%s,%s) -/-> (%s,%s)" % (move.start["row"], move.start["col"], move.end["row"], move.end["col"])

	def undoMove(self, move, verbal = True):
		midX = move.start["row"] + (move.end["row"] - move.start["row"])/2
		midY = move.start["col"] + (move.end["col"] - move.start["col"])/2
		self.setElem(move.start["row"], move.start["col"], PEG)
		self.setElem(move.end["row"], move.end["col"], HOLE)
		self.setElem(midX, midY, PEG)
		self.show(verbal)
		if verbal:
			print "BACKTRACKING! (row,col): (%s,%s) <-- (%s,%s)" % (move.start["row"], move.start["col"], \
					move.end["row"], move.end["col"])

	def isValidMove(self, move):
		dX = float((move.end["row"] - move.start["row"]))/2
		dY = float((move.end["col"] - move.start["col"]))/2
		midX = move.start["row"] + int(dX)
		midY = move.start["col"] + int(dY)
		dX = abs(dX)
		dY = abs(dY)
		if not (dX == 0 or dX == 1) or not (dY == 0 or dY == 1) or (dX + dY) != 1:
			return False 
		if move.start["row"] < 0 or move.start["row"] >= COLS or move.end["row"] < 0 or move.end["row"] >= COLS:
			return False
		if move.start["col"] < 0 or move.start["col"] >= ROWS or move.end["col"] < 0 or move.end["col"] >= ROWS:
			return False
		if self.getElem(move.start["row"], move.start["col"]) == PEG and self.getElem(move.end["row"], move.end["col"]) == HOLE \
			and self.getElem(midX, midY) == PEG:
			return True
		return False

	def hasWon(self):
		pegs = 0
		for elem in self.board:
			if elem != -1:
				pegs += elem
		return pegs

	def getNextMove(self, moves):
		for row in xrange(ROWS):
			for col in xrange(COLS):
				if self.getElem(row, col) == PEG:
					m = Move(row, col, row, col+2)
					if self.isValidMove(m):
						moves.push(m)
						movesHash = moves.hash()
						moves.pop()
						if movesHash not in BADMOVES:
							return m
					m = Move(row, col, row, col-2)
					if self.isValidMove(m):
						moves.push(m)
						movesHash = moves.hash()
						moves.pop()
						if movesHash not in BADMOVES:
							return m
					m = Move(row, col, row+2, col)
					if self.isValidMove(m):
						moves.push(m)
						movesHash = moves.hash()
						moves.pop()
						if movesHash not in BADMOVES:
							return m
					m = Move(row, col, row-2, col)
					if self.isValidMove(m):
						moves.push(m)
						movesHash = moves.hash()
						moves.pop()
						if movesHash not in BADMOVES:
							return m
		return False

def solvePeg(board):
	sol = solve(board, Moves())
	while sol == -1:
		sol = solve(board, Moves())

	if sol != False:
		checkSolution(Board(ROWS, COLS, False), sol)
	else :
		"No Solution found, sol is False"


def solve(board, moves, k = 0):
	if k > DEPTHLIMIT:
		return -1
	k += 1
	move = board.getNextMove(moves)
	if move == False:
		if moves.length() == 0:
			print "FAILED! No moves left."
			return False
		pegs = board.hasWon()
		if pegs == 1:
			print "YOU WON!"
			return moves
		else:
			BADMOVES[moves.hash()] = 1
			lastMove = moves.pop()
			board.undoMove(lastMove, True)
			return solve(board, moves, k)
			
	board.move(move, True)
	moves.push(move)
	return solve(board, moves, k)

def checkSolution(board, moves):
	for m in moves.moves:
		board.move(m)
	pegs = board.hasWon()
	if pegs == 1:
		board.show()
		print "SOLUTION CHECKS OUT! YOU WON!"
		return True
	else:
		print "SOLUTION IS FALSE!"
		return False



solvePeg(Board(ROWS, COLS, False))


