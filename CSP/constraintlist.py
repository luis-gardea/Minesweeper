import csp
import minemap

'''
This implementation of a CSP solver implements the approach outlined in 
"Minesweeper as a Constraint Satisfaction Problem" by Chris Studholme, Ph.D from 
the University of Toronto.

@File: constraintlist.py
@Use: List of constraints that have a particular variable in them, 
    used by solutionset.py to enumerate solutions 
'''

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
        self.nconstraints += 1
        self.constraints.append(c)


    # /**
    #  * Update all constraints given that variable has a new test assignment.
    #  */
    def updateConstraints(self):
        for i in range(self.nconstraints):
            self.constraints[i].updateVariable(self.variable)

    # /**
    #  * Check if all constraints are satisfied (or at least think they are).
    #  * @return false if any constraint is not satisfied
    #  */
    def checkConstraints(self):
        for i in range(self.nconstraints):
            if not self.constraints[i].isSatisfied():
                return False
        return True

    # /**
    #  * Compare this list to another based on the number of constraints in
    #  * each one's list.
    #  * @param o another ConstraintList instance
    #  * @return 1 if this has fewer constraints than o, -1 if more, 0 if equal
    #  */
    def compareTo(self, o):
        if self.nconstraints < o.nconstraints:
            return 1
        elif self.nconstraints > o.nconstraints:
            return -1
        return 0
