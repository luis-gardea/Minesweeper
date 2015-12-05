import minesweeper








# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions):
        self.actions = actions
        self.featureExtractor = featureExtractor
        self.weights = collections.Counter()
        self.numIters = 0
        self.qMap = {}

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        return qMap[(state, action)]

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        return random.choice(self.actions(state))

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        
        def getV(state):
            return max(self.getQ(state, action) for action in self.actions(state))

        def scaleListOfTuples(mlist, scalar):
            listCopy = mlist
            for i, tup in enumerate(listCopy):
                listCopy[i] = (tup[0], scalar * tup[1])
            return listCopy

        if newState is None:
            return

        featureVector = self.featureExtractor(state, action)
        qOpt = self.getQ(state, action)
        eta = self.getStepSize()

        vOpt = 0
        if newState is not None:
            vOpt = getV(newState)
        discount = self.discount
        scalar = eta*(qOpt - (reward + discount*vOpt))

        delta = scaleListOfTuples(featureVector, scalar)
        for f, v in delta:
            self.weights[f] -= v

