import csp
import minemap
import solutionset
import sys

'''
This implementation of a CSP solver implements the approach outlined in 
"Minesweeper as a Constraint Satisfaction Problem" by Chris Studholme, Ph.D from 
the University of Toronto.

@File: cspstrategy.py 
@Use: This class implements the CSP strategy to be used by PGMS
'''

# If True, will print more messages
VERBOSE = False

# Used for a print message
SOLVE_THRESHOLD = 20


class CSPStrategy(object):
	
	def __init__(self):
		# list of constraints remaining
		self.constraints = []

	
	# /**
	#  * Play a non-hinted game.  Starting in a corner seems to be the best
	#  * strategy and since we assume a random map (as opposed to one
	#  * designed to fool us), we always start in the lower left corner.
	#  * @param m game to play
	#  */
	def play1(self, m):
		self.play2(m, 0, 0)

	# /**
	#  * Play a hinted game.
	#  * @param m game to play
	#  * @param hint_column x coordinate of hint
	#  * @param hint_row y coordinate of hint 
	#  */
	def play2(self,m, hint_column, hint_row):
		self.map = m

		# initialize SolutionSet statics
		solutionset.largest_neqns = 0
		solutionset.largest_nvars = 0
		solutionset.largest_nsols = 0

		# initialize board
		cspboard = csp.CSPBoard()
		cspboard.CreateBoard(self.map)


		if VERBOSE:
			print("================ NEW GAME ================")

		# use hint
		if cspboard.board[hint_column][hint_row].probe(self.map) == minemap.BOOM:
			return

		# initialize constraints
		for x in range(self.map.cols):
			for y in range(self.map.rows):
				self.addConstraint(cspboard.board[x][y].newConstraint())

		# main loop
		while not self.map.done():
			# /* Simplify constraints by combining with each other and
			#  * marking or probing _obvious_ mines and cleared areas.
			#  */
			self.simplifyConstraints()
			if self.map.done():
				break

			# /* At this point the constraints are as simple as possible and
			#  * the choice of next move is _not_ obvious.  All solutions to
			#  * the CSP must be found to determine if there are any _safe_
			#  * moves.
			#  */

			# /* Seperate the constraints into coupled subsets, each represented
			#  * by a SolutionSet object.
			#  */
			subsets = self.seperateConstraints()
			nsubsets = len(subsets)

			if nsubsets <= 0:
				# /* This happens when all remaining (unknown) clear positions 
				#  * are seperated (by mines) from the known clear positions.
				#  */
				if VERBOSE:
					print("No problems to solve!")
			else:
				solving_msg = False
				if VERBOSE:
					# determine number of variables in largest subproblem
					nvars = subsets[0].getVariableCount()
					ncnts = subsets[0].getConstraintCount()
					for i in range(1, nsubsets):
						if (subsets[i].getVariableCount() - subsets[i].getConstraintCount()) > nvars - ncnts:
							nvars = subsets[i].getVariableCount()
							ncnts = subsets[i].getConstraintCount()

					if nvars - ncnts >= SOLVE_THRESHOLD:
						solving_msg = True
						if nsubsets == 1:
							print("Solving "+str(ncnts)+" constraint "+
								str(nvars)+" variable system...")
						else:
							print("Solving " + str(nsubsets) + 
								" systems (largest is "+str(ncnts)+" constraints "
									+str(nvars)+" variables)...")

				# /* Solve each of the sub-problems by enumerating all solutions
				#  * to the constraint satisfaction problem.
				#  */
				for i in range(nsubsets):
					subsets[i].enumerateSolutions()
				if solving_msg:
					print(" done.")

			# /* Account for all remaining mines.  It may be found that some
			#  * sub-problems have solutions that require too many or too few
			#  * mines.  In these cases, some solutions will be deleted from
			#  * the SolutionSet.  
			#  *
			#  * The number of mines expected to be found in the unknown
			#  * positions is also calculated.
			#  */
			remaining = self.map.mines_minus_marks()
			far = cspboard.nonConstrainedCount()
			far_max = remaining
			far_expected = float(remaining)
			for i in range(nsubsets):
				nmin = 0
				nmax = far
				for j in range(nsubsets):
					if i != j:
						nmin += subsets[j].getMin()
						nmax += subsets[j].getMax()
				subsets[i].reduceMinMax(remaining - nmax, remaining - nmin)
				far_expected -= subsets[i].expectedMines()
				far_max -= subsets[i].getMin()

			# /* Using far_expected here seems to work better, but sometimes
			#  * yeilds negative probabilities.  far_max doesn't have this
			#  * problem, but doesn't work as well.
			#  */
			far_prob = far_expected/float(far) if far > 0 else 1
			if far_prob < 0.01: far_prob = float(0.01)

			# /* Do any craps shoots.  Even if we survive these, we are no
			#  * better off.
			#  */
			crapshoot = False
			for i in reversed(range(nsubsets)):
				c = subsets[i].doCrapsShoot(self.map)
				if c != None:
					self.addConstraint(c)
					# // throw away subset so we don't do anything with it
					# // again until the constraints are next simplified
					nsubsets -= 1
					subsets.pop(i)
					crapshoot = True
				elif self.map.done():
					break

			if self.map.done():
				break;
			if nsubsets <= 0 and crapshoot:
				continue

			# /* Mark for-sure mines.  These don't make us any better off 
			#  * either.
			#  */
			for i in range(nsubsets):
				subsets[i].markMines(self.map)

			# /* If no mines are left in the unknown positions, probe them all.
			#  * This is very good for us and we go back to simplification
			#  * immediately afterwards.
			#  */
			if far_max <= 0 and far > 0:
				positions = cspboard.enumerateUnknown()
				for position in positions:
					position.probe(self.map)
					self.addConstraint(position.newConstraint())
				continue

			# /* Determine best position to make a probe (a guess).
			#  */
			best_subset = -1
			best_prob = far_prob
			surething = False
			for i in range(nsubsets):
				prob = subsets[i].findBestProbe()
				if prob <= 0:
					surething = True
					self.addConstraint(subsets[i].doBestProbe(self.map))
				elif prob <= best_prob:
					best_prob = prob
					best_subset = i
			if surething:
				continue

			# /* If best guess is a constrained position, probe it.
			#  */
			
			if best_subset >= 0:
				if VERBOSE:
					print("GUESS: "+str(int((1-best_prob)*100))+"% educated ...")
				c = subsets[best_subset].doBestProbe(self.map)
				if c != None:
					self.addConstraint(c)
					if VERBOSE: print(" good.")
				elif VERBOSE: print(" FAILED")

			# /* Otherwise, we probe one of the unknown positions.
			#  */
			else:
				# first check the corners
				positions = cspboard.enumerateCorners()
				category = "corner"
				if positions == None:
					# next check for edges
					positions = cspboard.enumerateEdges()
					category = "edge"
				if positions == None:
					# next check for a boundary position
					positions = cspboard.enumerateMaxBoundary()
					category = "boundary"
				if positions == None:
					# finally, if all else fails, probe some random position
					positions = cspboard.enumerateUnknown()
					category = "far"
				if positions == None:
					print("WHAT!  No boundary or unknown?")

				if VERBOSE:
					print("GUESS: "+str(int((1-best_prob)*100))+"% "+category+" ...")
				i = self.map.pick(len(positions))
				s = positions[i].probe(self.map)
				if s >= 0:
					self.addConstraint(positions[i].newConstraint())
					if VERBOSE:
						print(" ok.")
				elif VERBOSE:
					print(" FAILED!")

		# // miscellaneous stats
		if VERBOSE and solutionset.largest_nvars > 0:
			print("Largest System Solved:  "+
				solutionset.largest_neqns+" equations  "+
				solutionset.largest_nvars+" variables  "+
				solutionset.largest_nsols+" solutions")

	# /**
	#  * Add a constraint to the master list.  If the constraint is null,
	#  * nothing is done.
	#  * @param c a constraint
	# */
	def addConstraint(self, c):
		if c == None:
			return
		self.constraints.append(c)

	# /**
	#  * Seperate the constraints into coupled subsets and create a new
	#  * SolutionSet object for each one.
	#  * @return full array of SolutionSet objects
	#  */
	def seperateConstraints(self):
		sets = []
		start = 0
		for end in range(1, len(self.constraints) + 1):
			# search for constraints that are coupled with ones in [start,end)
			found = False
			for i in range(end,len(self.constraints)):
				if found:
					break
				for j in range(start,end):
					if self.constraints[i].coupledWith(self.constraints[j]):
						found = True
						if i != end:
							tmp = self.constraints[i]
							self.constraints[i] = self.constraints[end]
							self.constraints[end] = tmp
						break
			# if none were found, we have a coupled set in [start,end)
			if not found:
				sets.append(solutionset.SolutionSet(self.constraints, start, end - start))
				start = end
				
		return sets

	# /**
	#  * Repeatedly update and remove known variables from constraints and
	#  * simplify those constraints until no more work can be done.
	#  */
	def simplifyConstraints(self):
		done = False
		while True:
			done = True;
			# // update state of varilables

			for i in range(len(self.constraints)):
				newconstraints = self.constraints[i].updateAndRemoveKnownVariables(self.map)
				if newconstraints != None:
					done = False
					for j in range(len(newconstraints)):
						self.addConstraint(newconstraints[j])

			if not done:
				continue

			# // check for empty or simplifiable constraints
			i = 0
			while i < len(self.constraints):
				# check for empty, eliminate if necessary
				while i < len(self.constraints) and self.constraints[i].isEmpty():
					self.constraints[i] = self.constraints[-1]
					self.constraints.pop()

				# // attempt to simplify using all others
				if i < len(self.constraints):
					for j in range(i+1, len(self.constraints)):
						if self.constraints[i].simplify(self.constraints[j]):
							done = False
				i += 1		
			if done:
				break