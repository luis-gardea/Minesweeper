import csp
import minemap
import constraintlist
import cspstrategy
import sys

'''
This implementation of a CSP solver implements the approach outlined in 
"Minesweeper as a Constraint Satisfaction Problem" by Chris Studholme, Ph.D from 
the University of Toronto.

@File: solutionset.py
@Use: Instances of this class are used to enumerate all of the solutions
	to coupled set of Constraint's.  The solutions are found using a
	backtracking algorithm and statistics about the solutions are kept
	and sorted into bins based on the number of mines (1's) required for
	each solution.  Note that individual solutions are not stored.  Instead,
	for each mine rank, the total number of solutions will be tallied along
	with the number of instances of each variable equalling 1 (ie. mine).

	From the stats produced, cases where a variable must be 0 or must
	be 1 can be easily found.  If none of these are found, the probability
	of a particular variables being 0 or 1 can be calculated.

	If it is found that some solutions require either too many 1's or too
	few 1's, those solutions can be removed from the solution set with ease.

	In static space, details about the largest CSP solved thus far are
	maintained.  A CSP's size is considered to be proportional to the
	number of variables (total number of distinct variables) minus the number
	of constraints.  The size and number of solutions found for this CSP
	are recorded for profiling uses. 
'''

class SolutionSet(object):

	def __init__(self, constraints, startIndex = 0, nconstraints = -1):
		if nconstraints == -1:
			nconstraints = len(constraints)

		self.construct(constraints[startIndex:], nconstraints)

	def construct(self, constraints, nconstraints):
		self.constraints = constraints
		self.nconstraints = nconstraints
		self.VERBOSE = cspstrategy.VERBOSE

		self.variables = None
		self.nodes = []
		self.nvariables = 0

		self.min = 0
		self.max = 0
		self.bestProbe = None

		self.largest_nvars = 0
		self.largest_neqns = 0
		self.largest_nsols = 0
		self.VERBOSE = False
	
	 	for i in range(self.nconstraints):
	 		vararray = constraints[i].getVariables()
	 		for j in range(len(vararray)):
	 			found = False
	 			for k in range(self.nvariables):
	 				if self.nodes[k].variable == vararray[j]:
	 					self.nodes[k].addConstraint(constraints[i])
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
		self.nodes = sorted(self.nodes, key = lambda constraintList: constraintList.nconstraints, reverse = True)
		if self.nodes[0].nconstraints < self.nodes[self.nvariables-1].nconstraints:
			raise Exception('WRONG ORDER!!!')

		# create variables array
		self.variables = []
		for i in range(self.nvariables):
			self.variables.append(self.nodes[i].variable)

		# create needed arrays
		self.solutions = [None]*(self.min+1)
		self.mines = []
		for i in range(self.min+1):
			self.mines.append([None]*self.nvariables)

	def getVariableCount(self):
		return self.nvariables

	def getConstraintCount(self):
		return self.nconstraints

	def getMin(self):
		return self.min

	def getMax(self):
		return self.max

	def expectedMines(self):
		total = 0.0
		count = 0.0
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
			for i in reversed(range(self.max, newmax)):
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

	def doCrapsShoot(self, mapM):
		if self.min != self.max:
			return None
		for i in range(self.nvariables):
			if not self.variables[i].neighborsKnownOrInSet(self.variables, self.nvariables):
				return None
		# figure out best choice (and mark for sure mines when found)
		best = -1
		bestcount = self.solutions[self.min]
		for i in range(self.nvariables):
			if self.mines[self.min][i] < bestcount:
				bestcount = self.mines[self.min][i];
				best = i
			elif self.mines[self.min][i] == self.solutions[self.min]:
				# for-sure mine
				self.variables[i].mark(mapM)
		if best < 0:
	    	# must be all mines
			return None
		if bestcount == 0:
	    	# for-sure clear
			self.variables[best].probe(mapM)
		else:
			if self.VERBOSE:
				print("GUESS: " + (100-100*bestcount/self.solutions[self.min]) + "\% CRAPS ...")
			s = self.variables[best].probe(mapM)
			if s < 0:
				if self.VERBOSE: print(" FAILED!")
				return None
			if self.VERBOSE: print(" YEAH!")
		return self.variables[best].newConstraint()

	def markMines(self, mapM):
		total_solutions = 0
		for j in range(self.min, self.max + 1):
			total_solutions += self.solutions[j]
		for i in range(self.nvariables):
			total = 0
			for j in range(self.min, self.max + 1):
				total += self.mines[j][i]
			if total == total_solutions:
				self.variables[i].mark(mapM)

	def enumerateSolutions(self):
		# initialize counters
		for i in range(len(self.solutions)):
			self.solutions[i] = 0
			for j in range(self.nvariables):
				self.mines[i][j] = 0
		# initialize all variables to unset
		for i in range(self.nvariables):
			self.variables[i].testAssignment = -1
		# index to variable used at each level
		variableindex = []
		for i in range(self.nvariables):
			variableindex.append(-1)
		# last choice of variable by constrainedness
		lastchoice = -1
		# initialize constraints
		for i in range(self.nconstraints):
			self.constraints[i].updateVariable(None)
	
		# main loop
		level = 0
		while True:
			if level == self.nvariables:
				# all variables assigned, enumerate solution
				m = 0
				for j in range(self.nvariables):
					m += self.variables[j].testAssignment
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
				for i in range(self.nconstraints):
					if var != None:
						break
					var = self.constraints[i].suggestUnassignedVariable()
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
		if self.nvariables - self.nconstraints > self.largest_nvars - self.largest_neqns:
			self.largest_nvars = self.nvariables
			self.largest_neqns = self.nconstraints
			self.largest_nsols = 0
			for solution in self.solutions:
				self.largest_nsols += solution		