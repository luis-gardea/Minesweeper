import csp
import minemap
import solutionset

# /* Copyright (C) 2001 Chris Studholme

# This file is part of a Constraint Satisfaction Problem (CSP) strategy
# for Programmer's Minesweeper (PGMS).

# CSPStrategy is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# */

# /**
#  * Should we print anything to System.out?
#  */
VERBOSE = True

# /**
#  * Threshold for display "solving..." message.  The message is displayed
#  * if the number of variables minus the number of constraints exceeds
#  * this threshold.
#  */
SOLVE_THRESHOLD = 20

# /**
#  * Public class CSPStrategy implements minesweeper strategy 
#  * using CSP techniques.
#  *
#  * @version March 2001
#  * @author Chris Studholme
#  */
class CSPStrategy(object):
	
	# /**
	# * Default constructor initializes the constraints array.
	# */
	def __init__(self):
		# /**
		#  * Master list of outstanding constraints.
		#  */
		self.constraints = []

		# /**
		#  * Number of non-null entries in the constraints array.
		#  */
		self.nconstraints = 0

	# /**
	#  * Play a non-hinted game.  Starting in a corner seems to be the best
	#  * strategy and since we assume a random map (as opposed to one
	#  * designed to fool us), we always start in the lower left corner.
	#  * @param m game to play
	#  */
	def play1(self, m):
		#play(m,m.columns()/2,m.rows()/2);
		#play(m,m.pick(m.columns()),m.pick(m.rows()));
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

		# use hint
		if cspboard.board[hint_column][hint_row].probe(self.map) == minemap.BOOM:
			return

		if VERBOSE:
			print("================ NEW GAME ================")

		# initialize constraints
		self.nconstraints = 0
		for x in range(self.map.cols):
			for y in range(self.map.rows):
				# print x,y, self.nconstraints
				self.addConstraint(cspboard.board[x][y].newConstraint())

		# main loop
		while not self.map.done():
			# /* Simplify constraints by combining with each other and
			#  * marking or probing _obvious_ mines and cleared areas.
			#  */
			# print 'inside while loop'
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
							print("Solving "+ncnts+" constraint "+
								nvars+" variable system...")
						else:
							print("Solving " + nsubsets + 
								" systems (largest is "+
									+ncnts+" constraints "+nvars+
									" variables)...")

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
			far_expected = remaining
			for i in range(nsubsets):
				nmin = 0
				nmax = far
				for j in range(self.nsubsets):
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
			# //float far_prob = far>0 ? far_max/(float)far : 1;
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
					#subsets[i] = subsets[nsubsets]
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
					print("GUESS: "+(int)((1-best_prob)*100)+
						"% educated ...")
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
						print("GUESS: "+(int)((1-best_prob)*100)+"% "+
							category+" ...")
						i = self.map.pick(len(positions))
						s = positions[i].probe(self.map)
						if s >= 0:
							self.addConstraint(positions[i].newConstraint())
							if VERBOSE:
								print(" ok.")
							elif VERBOSE:
								print(" FAILED!")

			#    /*
			#    if (VERBOSE) {
			#    System.out.println("Subproblems: "+nsubsets);
			#    for (int i=0; i<nsubsets; ++i)
			#	  System.out.println("  "+subsets[i].toString());
			#    }
			#    */

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
			# print 'c is none'
			return
		self.constraints.append(c)
		self.nconstraints += 1

	# /**
	#  * Seperate the constraints into coupled subsets and create a new
	#  * SolutionSet object for each one.
	#  * @return full array of SolutionSet objects
	#  */
	def seperateConstraints(self):
		sets = []
		start = 0
		for end in range(1, self.nconstraints + 1):
			# search for constraints that are coupled with ones in [start,end)
			found = False
			i = end
			while i < self.nconstraints and not found:
				for j in range(start, end):
					if self.constraints[i].coupledWith(self.constraints[j]):
						found = True
						if i != end:
							# swap i and end
							tmp = self.constraints[i]
							self.constraints[i] = self.constraints[end]
							self.constraints[end] = tmp
						break
				i += 1
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
			# print 'in simplify constraints'
			# // update state of varilables
			# print self.constraints[0]

			for i in range(self.nconstraints):
				# print 'nvar',self.constraints[i].nvariables
				newconstraints = self.constraints[i].updateAndRemoveKnownVariables(self.map)
				print newconstraints
				if newconstraints != None:
					done = False
					for j in range(len(newconstraints)):
						self.addConstraint(newconstraints[j])

			if not done:
				print 'continuing'
				continue

			# // check for empty or simplifiable constraints
			i = 0
			while i < self.nconstraints:
				# check for empty, eliminate if necessary
				while i < self.nconstraints and self.constraints[i].isEmpty():
					self.constraints[i] = self.constraints[-1]
					self.constraints.pop()
					self.nconstraints -= 1

			# for i in range(self.nconstraints):
			# 	print 'in simplify constraints'
			# 	# check for empty, eliminate if necessary
			# 	while self.constraints[i].isEmpty() and i < self.nconstraints:
			# 		print 'in while'
			# 		self.nconstraints -= 1
			# 		#self.constraints.pop(i)
			# 		self.constraints[i] = self.constraints[self.nconstraints]

				# // attempt to simplify using all others
				if i < self.nconstraints:
					for j in range(i+1, self.nconstraints):
						if self.constraints[i].simplify(self.constraints[j]):
							print 'simplify returns false'
							done = False
				i += 1		
			if done:
				break
			print 'here'
			# sys.exit(0)