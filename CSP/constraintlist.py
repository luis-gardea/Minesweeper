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

    # Construct list with an initial constraint and common variable.
    def __init__(self, constraint, common_var):
        self.constraints = [constraint]
        self.variable = common_var

    # Add a constraint.  The constraint must have variable in it.
    def addConstraint(self, constraint):
        self.constraints.append(constraint)

    # Update all constraints given that variable has a new test assignment.
    def updateConstraints(self):
        for i in range(len(self.constraints)):
            self.constraints[i].updateVariable(self.variable)

    # Check if all constraints are satisfied (or at least think they are).
    # return false if any constraint is not satisfied
    def checkConstraints(self):
        for i in range(len(self.constraints)):
            if not self.constraints[i].isSatisfied():
                return False
        return True

    #  * Compare this list to another based on the number of constraints in
    #  * each one's list.
    def compareTo(self, other):
        if len(self.constraints) < len(other.constraints):
            return 1
        elif len(self.constraints) > len(other.constraints):
            return -1
        return 0
