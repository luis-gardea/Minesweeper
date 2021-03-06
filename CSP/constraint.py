import csp
import minemap
import sys

'''
This implementation of a CSP solver implements the approach outlined in 
"Minesweeper as a Constraint Satisfaction Problem" by Chris Studholme, Ph.D from 
the University of Toronto.

@File: constraint.py
@Use: Class to represent a single constraint.  A constraint consists of a bunch
	of boolean variables (0 or 1) summed together on one side of an equal
	sign with an integer constant on the other side.  The number of variables
	will usually be in the range 1 to 8 and thus the constant should also be 
	in this range.  

	Two special cases: if the constant is 0, all variables must be 0; and if 
	the constant equals the number of variables, all variables must be 1.

	Every clear board position will have one constraint associated with it.  
	The method (CSPSquare).newConstraint() should be used to automatically
	construct these constraints.  A constraint is usually "thrown away" once
	all its variables are known (either 0 or 1).
'''

class Constraint(object):

	def __init__(self, constant = 0):
		self.variables = []
		self.nvariables = 0
		self.constant = constant
		self.unassigned = None
		self.current_constant = None
		self.next_unassigned = None

	def add(self, c):
		self.variables.append(c)
		self.nvariables += 1

	def getVariables(self):
		return self.variables

	def getVariableCount(self):
		return self.nvariables

	def setConstant(self, c):
		self.constant = c

	def getConstant(self):
		if self.constant < 0:
			print self.constant
			raise Exception('Bad constant')
		return self.constant

	def isEmpty(self):
		return self.nvariables <= 0

	def updateVariable(self, var):
		self.current_constant = 0
		self.unassigned = 0
		self.next_unassigned = None
		for var in self.variables:
			if var.testAssignment < 0:
				self.next_unassigned = var
				self.unassigned += 1
			elif var.testAssignment >= 1:
				self.current_constant += 1

	def isSatisfied(self):
		if self.current_constant > self.constant:
			return False
		if self.unassigned > 0:
			return True
		return self.current_constant == self.constant

	def suggestUnassignedVariable(self):
		if self.next_unassigned == None:
			return None
		if self.current_constant == self.constant:
	    	# all mines accounted for (only 0's left)
			self.next_unassigned.testAssignment = 0
			return self.next_unassigned
		if self.constant - self.current_constant == self.unassigned: 
	    	# all remaining vars are mines (1's)
			self.next_unassigned.testAssignment = 1
			return self.next_unassigned
		return None

	def updateAndRemoveKnownVariables(self, mapM):
		# first check for previously known values
		
		for i in reversed(range(0,self.nvariables)):
			s = self.variables[i].getState()
			if s >= 0:
				# clear (remove variable)
				self.nvariables -= 1
				self.variables.pop(i)
			elif s == csp.MARKED:
				# marked (remove variable and decrement constant)
				self.nvariables -= 1
				self.variables.pop(i)
				self.constant -= 1

		# if no variables left, return
		if self.nvariables <= 0:
			return None

		# check for all clear or all marked
		result = []
		if self.constant == 0:
	    	# all variables are 0 (no mines)
			for var in self.variables:
				var.probe(mapM)
				result.append(var.newConstraint())
		elif self.constant == self.nvariables:
	    	# all variables are 1 (are mines)
			for var in self.variables:
				var.mark(mapM)
		else: 
			return None

		# empty constraint
		self.nvariables=0
		self.constant=0
		return result

	def simplify(self, other):
		if self.nvariables < other.nvariables:
	    	# Are we a subset of other?  Let other figure it out.
			return other.simplify(self)

		# Is other a subset of us?
		for i in range(len(other.variables)):
			for j in range(len(self.variables)):
				if self.variables[j] == other.variables[i]:
					break
				elif j >= len(self.variables) - 1:
					return False

		# remove other's variables from this
		for i in range(len(other.variables)):
			for j in range(len(self.variables)):
				if self.variables[j] == other.variables[i]:
					self.nvariables -=1
					self.variables.pop(j)
					break
		self.constant -= other.constant
		return True

	def coupledWith(self, other):
		for var in other.variables:
			for var2 in self.variables:
				if var == var2:
					return True
		return False


		