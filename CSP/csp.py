import minesweeper, constraint 

UNKNOWN = -5
CONSTRAINED = -4
MARKED = -3
CLEAR = 0

class CSPSquare(object):
	def __init__(self, x,y, csp):
		self.state = UNKNOWN
		self.csp = csp
		self.board = csp.board
		self.boundary_level = 0
		# x and y coordinates of this position
		self.x = x
		self.y = y
		# neighbors have x values in nx1<=x<nx2 and
		# y values in ny1<=y<ny2
		self.nx1 = x-1 if x>0 else 0
		self.nx2 = x+2 if x < len(csp.board)-1 else x+1
		self.ny1 = y-1 if y > 0 else 0
		self.ny2 = y+2 if y < len(csp.board[0]) else y+1
		# For use by SolutionSet and Constraint
		self.testAssignment = -1

	def __eq__(self,other):
		return self.state==other.state and self.boundary_level == other.boundary_level and self.x == other.x and \
			self.y == other.y and self.testAssignment == other.testAssignment

	def toString(self):
		switch = {UNKNOWN:'U',CONSTRAINED:'C',MARKED:'M'}
		return "(%s,%s,%s)" %  (switch[self.state],self.x,self.y)

	def newConstraint(self):
		if self.state < 0:
			return None
		c = constraint.Constraint()
		constant = self.state
		board = self.board
		for i in range(self.nx1,self.nx2):
			for j in range(self.ny1,self.ny2):
				if board[i][j].state < 0:
					if board[i][j].state == MARKED:
						constant -= 1
					else:
						c.add(board[i][j])
						board[i][j].setState(CONSTRAINED)
		c.setConstant(constant)
		return c

	def neighborsKnownOrInSet(self,variables,nvariables):
		board = self.board 
		for i in range(self.nx1,self.nx2):
			for j in range(self.ny1,self.ny2):
				if board[i][j].state < MARKED:
					found == False
					for k in range(nvariables):
						if board[i][j] == variables[k]:
							found = True
							break
					if not found:
						return False
		return True

	def mark(self,mapM):
		mapM.mark(self.x,self.y)
		self.setState(MARKED)

	def probe(self,mapM):
		result = mapM.probe(self.x,self.y)
		self.setState(result)
		return result

	def getState(self):
		return self.state

	def setState(self,state):
		if state == self.state:
			return
		csp = self.csp
		board = self.board
		if self.state == UNKNOWN:
			csp.unknown -= 1
		elif self.state == CONSTRAINED:
			csp.constrained -= 1
		elif self.state == MARKED:
			csp.mine -= 1
		else:
			csp.clear -= 1

		self.state = state
		if state == UNKNOWN:
			csp.unknown += 1
		elif state == CONSTRAINED:
			csp.constrained += 1
			self.boundary_level = 0
			for i in range(self.nx1,self.nx2):
				for j in range(self.ny1,self.ny2):
					if board[i][j].state == UNKNOWN:
						board[i][j].boundary_level += 1
		elif state == MARKED:
			csp.mine += 1
			self.boundary_level=0
			for i in range(self.nx1,self.nx2):
				for j in range(self.ny1,self.ny2):
					if board[i][j].state == UNKNOWN:
						board[i][j].boundary_level -= 1
		else:
			self.boundary_level = 0
			if state >= 0:
				csp.clear += 1
		

class CSPBoard(object):
	def __init__(self):
		self.mine = 0
		self.unknown = 0
		self.constrained = 0
		self.clear = 0
		self.board = None

	def CreateBoard(self,board):
		self.board = []
		for x in range(len(board)):
			self.board.append([])
			for y in range(len(board[0])):
				self.board[x].append(CSPSquare(x,y,self))
				self.unknown += 1

	def nonConstrainedCount(self):
		return self.unknown

	def enumerateBoundary(self,level):
		result = []
		count = 0
		board = self.board
		for x in range(len(board)):
			for y in range(len(board[0])):
				if (board[x][y].state == UNKNOWN and board[x][y].boundary_level == level):
					count += 1
					result.append(board[x][y])
		# Could return None or [] depending on use
		if count == 0:
			return None
		return result

	def enumerateMaxBoundary(self):
		maxN = 0
		board = self.board
		for x in range(len(board)):
			for y in range(len(board[0])):
				if (board[x][y].state == UNKNOWN and board.boundary_level > maxN):
					maxN = board[x][y].boundary_level
		if maxN == 0:
			return None
		return self.enumerateBoundary(maxN)

	def enumerateMinBoundary(self):
		minN = 1000
		board = self.board
		for x in range(len(board)):
			for y in range(len(board[0])):
				# Try with boundary level >= 0 later...
				if (board[x][y].state==UNKNOWN and board[x][y].boundary_level>0 and board[x][y].boundary_level<minN):
					minN = board[x][y].boundary_level
		if minN == 1000:
			return None
		return self.enumerateBoundary(minN)

	def enumerateFar(self):
		result = self.enumerateBoundary(0)
		return result if result!=None else self.enumerateMinBoundary()

	def enumerateUnknown(self):
		if self.unknown:
			return None
		result = []
		count = 0
		board = self.board
		for x in range(len(board)):
			for y in range(len(board[0])):
				if(board[x][y].state == UNKNOWN):
					count+=1
					result.append(board[x][y])
		return result

	def enumerateEdges(self):
		v = []
		board = self.board
		for x in range(1,len(board)-1):
			if board[x][0].state<CONSTRAINED:
				v.append(board[x][0])
			if board[x][len(board[x]-1)].state<CONSTRAINED:
				v.append(board[x][len(board[x])-1])
		for y in range(1,len(board[0])-1):
			if board[0][y].state < CONSTRAINED:
				v.append(board[0][y])
			if board[len(board)-1][y].state < CONSTRAINED:
				v.append(board[len(board)-1][y])
		if len(v)==0:
			return None
		return v 

	def enumerateCorners(self):
		result = []
		board = self.board
		maxX = len(board)-1
		maxY = len(board[0])-1
		if board[0][0].state < CONSTRAINED:
			result.append(board[0][0])
		if board[0][maxY].state < CONSTRAINED:
			result.append(board[0][maxY])
		if board[maxX][0].state < CONSTRAINED:
			result.append(board[maxX][0])
		if board[maxX][maxY].state < CONSTRAINED:
			result.append(board[maxX][maxY])
		if len(result)==0:
			return None
		return result




