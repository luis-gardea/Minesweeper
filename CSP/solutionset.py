import csp
import minemap
import constraintlist
import cspstrategy
import sys

largest_nvars = 0
largest_neqns = 0
largest_nsols = 0
VERBOSE = False

class SolutionSet(object):
	"""docstring for SolutionSet
/* Copyright (C) 2001 Chris Studholme
 
This file is part of a Constraint Satisfaction Problem (CSP) strategy
for Programmer's Minesweeper (PGMS).
 
CSPStrategy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.
*/
 
/**
 * Instances of this class are used to enumerate all of the solutions
 * to coupled set of Constraint's.  The solutions are found using a
 * backtracking algorithm and statistics about the solutions are kept
 * and sorted into bins based on the number of mines (1's) required for
 * each solution.  Note that individual solutions are not stored.  Instead,
 * for each mine rank, the total number of solutions will be tallied along
 * with the number of instances of each variable equalling 1 (ie. mine).
 *
 * From the stats produced, cases where a variable must be 0 or must
 * be 1 can be easily found.  If none of these are found, the probability
 * of a particular variables being 0 or 1 can be calculated.
 *
 * If it is found that some solutions require either too many 1's or too
 * few 1's, those solutions can be removed from the solution set with ease.
 *
 * In static space, details about the largest CSP solved thus far are
 * maintained.  A CSP's size is considered to be proportional to the
 * number of variables (total number of distinct variables) minus the number
 * of constraints.  The size and number of solutions found for this CSP
 * are recorded for profiling uses. 
 *
 * @see CSPStrategy
 * @version March 2001
 * @author Chris Studholme
 */
	"""

	def __init__(self, constraints, startIndex = 0, nconstraints = -1):
		if nconstraints == -1:
			nconstraints = len(constraints)

		self.construct(constraints[startIndex:], nconstraints)

	def construct(self, constraints, nconstraints):
		self.constraints = constraints
		self.nconstraints = nconstraints
		self.VERBOSE = cspstrategy.VERBOSE

		self.variables = []
		self.nodes = []
		self.nvariables = 0

		self.min = 0
		self.max = 0
		self.bestProbe = None
	
		# tally variables and count maximum mines
		# for constraint in self.constraints:
		# 	vararray = constraint.getVariables()
	 #    	for var in vararray:
		# 		found = False
		# 		for node in self.nodes:
		# 			if node.variable == var:
		# 				node.addConstraint(constraint)
		# 				found = True
		# 				break
		# 		if not found:
		# 			self.nvariables += 1
		#     		self.nodes.append(constraintlist.ConstraintList(constraint, var))
	 #    	self.min += constraint.getConstant()
	 	for i in range(self.nconstraints):
	 		vararray = self.constraints[i].getVariables()
	 		for j in range(len(vararray)):
	 			found = False
	 			for k in range(self.nvariables):
	 				if self.nodes[k].variable == vararray[j]:
	 					self.nodes[k].addConstraint(self.constraints[i])
	 					found = True
	 					break
	 			if not found:
	 				self.nodes.append(constraintlist.ConstraintList(self.constraints[i],vararray[j]))
	 				self.nvariables += 1
	 		self.min += constraints[i].getConstant()
		# Note: we used min here to tally the absolute maximum number of mines
		# expected because this number is a good initial value for the minimum
		# mines variables.

		# sort variables in decending order by number of constraints
		print len(self.nodes),len(constraints), nconstraints, self.nvariables
		sorted(self.nodes, key = lambda constraintList: constraintList.nconstraints, reverse = True)
		if self.nodes[0].nconstraints < self.nodes[self.nvariables-1].nconstraints:
			raise Exception("WRONG ORDER!!!")
		
		# create variables array
		self.variables = []
		for i in range(self.nvariables):
			self.variables.append(self.nodes[i].variable)

		# create needed arrays
		self.solutions = []
		self.mines = []
		for i in range(self.min):
			self.mines.append([])

	def getVariableCount(self):
		return self.nvariables

	def getConstraintCount(self):
		return self.nconstraints

	def getMin(self):
		return self.min

	def getMax(self):
		return self.max

	def expectedMines(self):
		total = 0
		count = 0
		for i in range(self.min, self.max + 1):
			total += i*self.solutions[i]
	    	count += self.solutions[i]
		return total/count

	def reduceMinMax(self, newmin, newmax):
		if newmin > self.min:
			for i in range(self.min, newmin):
				self.solutions[i] = 0
    		self.min = newmin
		if newmax < self.max:
			for i in range(newmax + 1, self.max + 1):
				self.solutions[i] = 0
	    	self.max = newmax
		# NOTE: mines[][] has not been zeroed out (but that's ok)

	def findBestProbe(self):
		total_solutions = 0
		for j in range(self.min, self.max + 1):
			total_solutions += self.solutions[j]
		best = total_solutions
		for i in range(self.nvariables):
			total = 0
			for j in range(self.min, self.max + 1):
				total += self.mines[j][i]
    		if total < best:
				best = total
				self.bestProbe = self.variables[i]
		return best/float(total_solutions)

	def doBestProbe(self, map):
		if self.bestProbe == None:
			self.findBestProbe()
		s = self.bestProbe.probe(map)
		return self.bestProbe.newConstraint() if s >= 0 else None

	def doCrapsShoot(self, map):
		if self.min != self.max:
			return None
		for i in range(nvariables):
			if not self.variables[i].neighboursKnownOrInSet(self.variables, self.nvariables):
				return None
		# figure out best choice (and mark for sure mines when found)
		best = -1
		bestcount = self.solutions[self.min]
		for i in range(self.nvariables):
			if self.mines[self.min][i] < bestcount:
				bestcount = self.mines[self.min][i];
				best=i
			elif self.mines[self.min][i] == self.solutions[self.min]:
				# for-sure mine
				self.variables[i].mark(map)
		if best < 0:
	    	# must be all mines
			return None
		if bestcount == 0:
	    	# for-sure clear
			self.variables[best].probe(map)
		else:
			if VERBOSE:
				print("GUESS: " + (100-100*bestcount/self.solutions[self.min]) + "\% CRAPS ...")
			s = self.variables[best].probe(map)
			if s < 0:
				if VERBOSE: print(" FAILED!")
				return None
			if VERBOSE: print(" YEAH!")
		return self.variables[best].newConstraint()

	def markMines(self, map):
		total_solutions = 0
		for j in range(self.min, self.max + 1):
			total_solutions += self.solutions[j]
		for i in range(self.nvariables):
			total = 0
    		for j in range(self.min, self.max + 1):
				total += self.mines[j][i]
    		if total == total_solutions:
				self.variables[i].mark(map)

	def enumerateSolutions(self):
		# initialize counters
		print 'enumerateSolutions',len(self.solutions),self.nvariables
		''' Hacky shit '''
		if len(self.solutions) != 0:
			for i in range(len(self.solutions)):
				self.solutions[i] = 0
	    		for j in range(self.nvariables):
					self.mines[i][j] = 0
		# initialize all variables to unset
		for i in range(self.nvariables):
			self.variables[i].testAssignment = -1
		# index to variable used at each level
		variableindex = [-1]*self.nvariables
		# last choice of variable by constrainedness
		lastchoice =- 1
		# initialize constraints
		for i in range(self.nconstraints):
			self.constraints[i].updateVariable(None)
	
		# main loop
		level = 0
		while True:
			print 'enumerateSolutions while check',level, self.nvariables, variableindex[level]
			print 'testAssignments', [var.testAssignment for var in self.variables]
			if level == self.nvariables:
				# all variables assigned, enumerate solution
				m = 0
				for j in range(self.nvariables):
					m += self.variables[j].testAssignment
				print 'enumerate Solutions while loop', m
				self.solutions[m] += 1
				if m < self.min: 
					self.min = m
				if m > self.max:
					self.max = m
				for j in range(self.nvariables):
					self.mines[m][j] += self.variables[j].testAssignment
				# go up
				level -= 1
				continue

			if variableindex[level] < 0:
				# pick next variable
				var = None
				i = 0
				while var == None and i < self.nconstraints:
					var = self.constraints[i].suggestUnassignedVariable()
		    		i += 1
				if var != None:
					# find suggested variable
					variableindex[level] = self.nvariables
					variableindex[level] -= 1	
					while var != self.variables[variableindex[level]]:
						variableindex[level] -= 1
					var.testAssignment -= 1 # we re-increment it below
				else:
					# find next most constrained variable
					lastchoice += 1	
					while self.variables[lastchoice].testAssignment >= 0:
						lastchoice += 1
					variableindex[level] = lastchoice

			if self.variables[variableindex[level]].testAssignment > 0:
				# domain exhausted, reset assignment and go up
				if variableindex[level] <= lastchoice:
					lastchoice = variableindex[level] - 1 
				self.variables[variableindex[level]].testAssignment = -1
				self.nodes[variableindex[level]].updateConstraints()
				variableindex[level] = -1
				level -= 1
			else:
				# try next value in domain
				self.variables[variableindex[level]].testAssignment += 1
				# update all constraints that have this variables
				self.nodes[variableindex[level]].updateConstraints()
				# check constraints
				if self.nodes[variableindex[level]].checkConstraints():
			    	# go down if constraints are satisfied
					level += 1

			if level < 0:
				break

		# check if this was the largest system solved
		if self.nvariables - self.nconstraints > largest_nvars - largest_neqns:
			largest_nvars = self.nvariables
			largest_neqns = self.nconstraints
			largest_nsols = 0
			for solution in self.solutions:
				largest_nsols += solution		