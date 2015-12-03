import minesweeper
import numpy as np 
import cv2
from random import randint

##########################################################################################
# Generate game states and labels (training data)
row = 8
col = 8
dif = 1
X_train, Y_train = minesweeper.generate_data(300, row, col, dif)
X_test, Y_test = minesweeper.generate_data(100, row, col, dif)

##########################################################################################
# Set up the network and train it

# The number of elements in an input vector, i.e. the number of nodes
# in the input layer of the network.
ninputs = np.size(X_train, 1)
nhidden = 100
noutput = np.size(Y_train, 1)

# Create an array of desired layer sizes for the neural network
layers = np.array([ninputs, nhidden, noutput])

# Create the neural network
nnet = cv2.ANN_MLP(layers)

# Some parameters for learning.  Step size is the gradient step size
# for backpropogation.
step_size = 0.01

# Momentum can be ignored for this example.
momentum = 0.0

# Max steps of training
nsteps = 10000

# Error threshold for halting training
max_err = 0.0001

# When to stop: whichever comes first, count or error
condition = cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS

# Tuple of termination criteria: first condition, then # steps, then
# error tolerance second and third things are ignored if not implied
# by condition
criteria = (condition, nsteps, max_err)

# params is a dictionary with relevant things for NNet training.
params = dict( term_crit = criteria, 
               train_method = cv2.ANN_MLP_TRAIN_PARAMS_BACKPROP, 
               bp_dw_scale = step_size, 
               bp_moment_scale = momentum )

# Train network
num_iter = nnet.train(X_train, Y_train,
                      None, params=params)

##########################################################################################
# Test network with randomly generated game states

# Compute training error
# Create a matrix of predictions
predictions = np.empty_like(Y_train)

# See how the network did.
nnet.predict(X_test, predictions)

# Compute # correct
num_correct = 0
for i in range(np.size(predictions, 0)):
	prediction = np.argmax(predictions[i])
	if Y_train[i][prediction] == 0:
		num_correct += 1

print 'Train accuracy:', float(num_correct) / np.size(predictions, 0)

# Compute test error
# Create a matrix of predictions
predictions = np.empty_like(Y_test)

# See how the network did.
nnet.predict(X_test, predictions)

# Compute # correct
num_correct = 0
for i in range(np.size(predictions, 0)):
	prediction = np.argmax(predictions[i])
	if Y_test[i][prediction] == 0:
		num_correct += 1

print 'Test accuracy:', float(num_correct) / np.size(predictions, 0)

##########################################################################################
# Play actual games of minesweeper with network acting as agent

gamesWon = 0;
num_games = 5
for i in range(num_games):
	#needs to be same dimensions as training data
	game = minesweeper.MineSweeper(row, col, dif, True)

	# Pick the first move to be a corner
	#corner = randint(0, 3)
	#move = game.first_move(corner)
	move = randint(0, len(game.board)-1)
	while game.board[move].value == game.bomb_value:
		move = randint(0, len(game.board)-1)

    # Update the board with the first move
	state = np.array([game.get_next_state(move)], 'float')

	while not game.gameEnd:
		# Get next move from agent
		predictions = np.empty_like(state)
		nnet.predict(state, predictions)

		move = np.argmax(predictions)
		while game.board[move].isUncovered:
			predictions[move] = -2
			move = np.argmax(predictions)

		print move
		# Update board
		state = np.array([game.get_next_state(move)], 'float')

	if game.gameWon:
		gamesWon += 1

	print 'game finished'

print 'Win rate:', float(gamesWon) / num_games