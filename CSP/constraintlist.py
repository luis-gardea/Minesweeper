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
#  * List of constraints that all have a particular variable in them.  Used
#  * by SolutionSet to help optimize the enumerating of solutions.
#  *
#  * @see CSPStrategy
#  * @version March 2001
#  * @author Chris Studholme
#  */
class ConstraintList(object):
    # /**
    #  * Construct list with an initial constraint and common variable.
    #  * @param c constraint
    #  * @param b common variable
    #  */
    def __init__(self, c, b):
        # /**
        #  * Array of constraints containing the variable.
        #  */
        self.constraints = []
        self.constraints.append(c)

        # /**
        #  * A particular board position (variable).
        #  */
        self.variable = b

        # /**
        #  * Number of (non-null) constraints in array.
        #  */
        self.nconstraints = 1

    # /**
    #  * Add a constraint.  The constraint must have variable in it.
    #  * @param c constraint
    #  */
    def addConstraint(self, c):
	    self.constraints.append(c)

    # /**
    #  * Update all constraints given that variable has a new test assignment.
    #  */
    def updateConstraints(self):
	    for constraint in self.constraints:
	       constraint.updateVariable(self.variable)

    # /**
    #  * Check if all constraints are satisfied (or at least think they are).
    #  * @return false if any constraint is not satisfied
    #  */
    def checkConstraints(self):
	    for constraint in self.constraints:
	        if not constraint.isSatisfied():
		        return False
	    return True

    # /**
    #  * Compare this list to another based on the number of constraints in
    #  * each one's list.
    #  * @param o another ConstraintList instance
    #  * @return 1 if this has fewer constraints than o, -1 if more, 0 if equal
    #  */
    def compareTo(o):
	    if self.nconstraints < o.nconstraints:
	        return 1
	    elif self.nconstraints > o.nconstraints:
	        return -1
	    return 0
