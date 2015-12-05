import csp
import minemap

# /* Copyright (C) 2001 Chris Studholme

# This file is part of a Constraint Satisfaction Problem (CSP) strategy
# for Programmer's Minesweeper (PGMS).

# CSPStrategy is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# */

# /**
#  * Public class CSPStrategy implements minesweeper strategy 
#  * using CSP techniques.
#  *
#  * @version March 2001
#  * @author Chris Studholme
#  */
class CSPStrategy(object):
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
	# * Default constructor initializes the constraints array.
	# */
	def __init__(self):
		# /**
		#  * Private copy of the current game.
		#  */
		self.map

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
	def play(self, m):
		#play(m,m.columns()/2,m.rows()/2);
		#play(m,m.pick(m.columns()),m.pick(m.rows()));
		self.play(m, 0, 0)

	# /**
	#  * Play a hinted game.
	#  * @param m game to play
	#  * @param hint_column x coordinate of hint
	#  * @param hint_row y coordinate of hint 
	#  */
	def play(m, hint_column, hint_row):
		self.map = m

		# initialize SolutionSet statics
		SolutionSet.largest_neqns = 0
		SolutionSet.largest_nvars = 0
		SolutionSet.largest_nsols = 0

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
		for x in range(self.map.columns()):
			for y in range(self.map.rows()):
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
					for i in range(nsubsets):
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
			far = BoardPosition.nonConstrainedCount()
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
					subsets[i] = subsets[nsubsets]
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
				positions = BoardPosition.enumerateUnknown()
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
				if  VERBOSE:
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
				positions = BoardPosition.enumerateCorners()
				category = "corner"
				if positions == None:
					# next check for edges
					positions = BoardPosition.enumerateEdges()
					category = "edge"
				if positions == None:
					# next check for a boundary position
					positions = BoardPosition.enumerateMaxBoundary()
					category = "boundary"
				if positions == None:
					# finally, if all else fails, probe some random position
					positions = BoardPosition.enumerateUnknown()
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
		if VERBOSE and SolutionSet.largest_nvars > 0:
			print("Largest System Solved:  "+
				SolutionSet.largest_neqns+" equations  "+
				SolutionSet.largest_nvars+" variables  "+
				SolutionSet.largest_nsols+" solutions")

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
	def seperateConstraints():
		sets = []
		start = 0
		for end in range(1, self.nconstraints + 1):
			# search for constraints that are coupled with ones in [start,end)
			found = False
			i = end
			while i < self.nconstraints and not found:
				for j in range(start, end):
					if constraints[i].coupledWith(constraints[j]):
						found = True
						if i != end:
							# swap i and end
							tmp = constraints[i]
							constraints[i] = constraints[end]
							constraints[end] = tmp
						break
			# // if none were found, we have a coupled set in [start,end)
			if not found:
				sets.apend(SolutionSet(constraints, start, end - start))
				start = end
			return sets

	# /**
	#  * Repeatedly update and remove known variables from constraints and
	#  * simplify those constraints until no more work can be done.
	#  */
	def simplifyConstraints(self):
		while True:
			done = True;

			# // update state of varilables
			for i in range(self.nconstraints):
				newconstraints = self.constraints[i].updateAndRemoveKnownVariables(self.map)
				if self.newconstraints != None:
					done = False
					for j in range(self.nconstraints):
						self.addConstraint(newconstraints[j])

			if not done:
				continue

			# // check for empty or simplifiable constraints
			for i in range(self.nconstraints):
				# check for empty, eliminate if necessary
				while self.constraints[i].isEmpty() and i < self.nconstraints:
					nconstraints -= 1
					self.constraints[i] = self.constraints[nconstraints]

				# // attempt to simplify using all others
				if i < self.nconstraints:
					for j in range(i+1, self.nconstraints):
						if self.onstraints[i].simplify(self.constraints[j]):
							done = False
						
				if done:
					break