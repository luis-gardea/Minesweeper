import csp
import minemap
import sys

class Constraint(object):
	"""docstring for Contraint

	Copyright (C) 2001 Chris Studholme
 
	This file is part of a Constraint Satisfaction Problem (CSP) strategy
	for Programmer's Minesweeper (PGMS).
 
	CSPStrategy is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2, or (at your option)
	any later version.

 	Class to represent a single constraint.  A constraint consists of a bunch
 	of boolean variables (0 or 1) summed together on one side of an equal
 	sign with an integer constant on the other side.  The number of variables
 	will usually be in the range 1 to 8 and thus the constant should also be 
 	in this range.  

	Two special cases: if the constant is 0, all variables must be 0; and if 
	the constant equals the number of variables, all variables must be 1.

	Every clear board position will have one constraint associated with it.  
	The method BoardPosition.newConstraint() should be used to automatically
	construct these constraints.  A constraint is usually "thrown away" once
	all its variables are known (either 0 or 1).

	@see CSPStrategy
	@version March 2001
	@author Chris Studholme
	"""

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
		for i in range(self.nvariables):
			if self.variables[i].testAssignment < 0:
				self.next_unassigned = self.variables[i]
				self.unassigned += 1
			elif self.variables[i].testAssignment >= 1:
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
				# self.variables[i]=self.variables[self.nvariables]
			elif s == csp.MARKED:
				# marked (remove variable and decrement constant)
				self.nvariables -= 1
				self.variables.pop(i)
				# self.variables[i]=self.variables[self.nvariables]
				self.constant -= 1

		# if no variables left, return
		if self.nvariables <= 0:
			return None

		# check for all clear or all marked
		result = []
		if self.constant == 0:
	    	# all variables are 0 (no mines)
			for i in range(self.nvariables):
				self.variables[i].probe(mapM)
				result.append(self.variables[i].newConstraint())
		elif self.constant == self.nvariables:
	    	# all variables are 1 (are mines)
			for i in range(self.nvariables):
				self.variables[i].mark(mapM)
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
		for i in range(other.nvariables):
			for j in range(self.nvariables):
				if self.variables[j] == other.variables[i]:
					break
				elif j >= self.nvariables - 1:
					return False

		# remove other's variables from this
		# for i in range(other.nvariables):
		# 	for j in range(self.nvariables):
		# 		if self.variables[j] == other.variables[i]:
		# 			del variables[j]
	 #    			break
		for i in range(other.nvariables):
			for j in range(self.nvariables):
				if self.variables[j] == other.variables[i]:
					self.nvariables -=1
					self.variables.pop(j)
					# print self.variables.pop
					# sys.exit(0)
					break
		self.constant -= other.constant
		return True

	def coupledWith(self, other):
		for i in range(other.nvariables):
			for j in range(self.nvariables):
				if self.variables[j] == other.variables[i]:
					return True
		return False


		