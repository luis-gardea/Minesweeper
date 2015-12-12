import minesweeper_ml
import numpy as np 
import cv2
from random import randint
import sys

##########################################################################################
# Generate game states and labels (training data)
row = 4
col = 4
bombs = 3
area = 2

X_train, Y_train = minesweeper_ml.generate_local_data(1500, row, col, bombs, area, False)
X_test, Y_test = minesweeper_ml.generate_local_data(50, row, col, bombs, area, False)
Y_train = np.reshape(Y_train, (np.size(Y_train, 0), 1))
Y_test = np.reshape(Y_test, (np.size(Y_test, 0), 1))

##########################################################################################
# Set up the network and train it

# The number of elements in an input vector, i.e. the number of nodes
# in the input layer of the network.
ninputs = np.size(X_train, 1)
nhidden = 50
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

# ##########################################################################################
# # Play actual games of minesweeper with network acting as agent

# gamesWon = 0
# num_games = 50
# for i in range(num_games):
# 	#needs to be same dimensions as training data
# 	game = minesweeper_ml.MineSweeper(row, col, bombs, True)

# 	# Pick the first move to be a corner
# 	#corner = randint(0, 3)
# 	#move = game.first_move(corner)
# 	# move = randint(0, len(game.board)-1)
# 	# while game.board[move].value == game.bomb_value:
# 	# 	move = randint(0, len(game.board)-1)
# 	move = game.get_square((0,0))
# 	if game.gameEnd == True: num_games -= 1

#     # Update the board with the first move
# 	state = np.array([game.get_next_state(move)], 'float')

# 	while not game.gameEnd:
# 		# Get next move from agent
# 		predictions = np.empty_like(state)
# 		nnet.predict(state, predictions)
# 		print 'predictions'
# 		temp = predictions
# 		print np.reshape(temp, (row, col))

# 		nmax = np.argmax(predictions)
# 		move = game.get_square((nmax/game.row_size, nmax % game.row_size))
# 		while move.isUncovered:
# 			predictions[0][nmax] = -2
# 			nmax = np.argmax(predictions)
# 			move = game.get_square((nmax/game.row_size, nmax % game.row_size))
# 		print nmax
# 		# Update board
# 		state = np.array([game.get_next_state(move)], 'float')
# 		temp2 = state
# 		print np.reshape(temp2, (row, col))

# 	if game.gameWon:
# 		gamesWon += 1

# 	print 'game finished'

# print 'Win rate:', float(gamesWon) / num_games

##########################################################################################
# Play actual games of minesweeper with network acting as agent
rows = 4
cols = 4
bombs = 3

gamesWon = 0;
num_games = 500
total_num_moves = 0
for i in range(num_games):
	#needs to be same dimensions as training data
	game = minesweeper_ml.MineSweeper(rows, cols, bombs, True)

	# Pick the first move to be a corner
	move = game.get_square((0,0))

	# Pick first move randomly
	# move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
	# while game.is_bomb(move):
	# 	move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

    # Update the board with the first move
	state = np.array(game.get_next_state(move))
	if game.gameEnd: num_games -= 1

	num_moves = 0
	while not game.gameEnd:
		# Get next move from agent
		perimeter = game.get_frontier()
		predictions = np.empty((1, 1))
		for square in perimeter:
			x = game.get_area_label(square, area)
			x = np.array([x], 'float')
			prediction = np.array([0], 'float')
			nnet.predict(x, prediction)

			np.append(predictions, prediction)

		nmax = np.argmax(np.array([predictions]))
		move = perimeter[nmax]

		# Update board
		state = np.array(game.get_next_state(move))
		num_moves += 1

	if game.gameWon:
		gamesWon += 1
	print num_moves
	total_num_moves += num_moves
	num_moves = 0

print 'Games won:', gamesWon, 'Win rate:', float(gamesWon) / num_games
print 'Average moves: ', float(total_num_moves)/num_games