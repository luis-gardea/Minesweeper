import minesweeper_ml
import numpy as np 
from sklearn import linear_model
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from sklearn import svm
from sklearn.kernel_ridge import KernelRidge
import sys

verbose = False

rows = 4
cols = 4
bombs = 3

# use to load data instead of generate
#X_train = np.load('train_data.npy')
#Y_train = np.load('train_labels.npy')

X_train, Y_train = minesweeper_ml.generate_global_data(200, rows, cols, bombs, True)

# Pain linear regression
# model = linear_model.LinearRegression()

# Linear regression Model norm factor
#model = linear_model.Ridge(alpha = .5)

# Linear regression model with kernel
model = KernelRidge(alpha=0.5, kernel='rbf')

model.fit(X_train, Y_train)

X_test, Y_test = minesweeper_ml.generate_global_data(100, rows, cols, bombs)

#########################################################################################
# Play actual games of minesweeper with network acting as agent

gamesWon = 0
num_games = 250
total_num_moves = 0
for i in range(num_games):
	#needs to be same dimensions as training data
	game = minesweeper_ml.MineSweeper(rows, cols, bombs, True)

	# Pick first move randomly
	# move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
	# while game.is_bomb(move):
	# 	move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

	# Pick the first move to be a corner
	move = game.get_square((0,0))
	if game.gameEnd == True:
		num_games -= 1

    # Update the board with the first move
	state = np.array(game.get_next_state(move))

	while not game.gameEnd:
		# Get next move from agent
		predictions = model.predict(state)
		if verbose:
			print 'predictions'
			temp = predictions
			print np.reshape(np.array(temp), (rows, cols))

		nmax = np.argmax(predictions)
		move = game.get_square((nmax/game.row_size, nmax % game.row_size))
		while move.isUncovered:
			predictions[0][nmax] = -2
			nmax = np.argmax(predictions)
			move = game.get_square((nmax/game.row_size, nmax % game.row_size))

		# Update board
		state = np.array(game.get_next_state(move))
		num_moves += 1
		if verbose:
			print 'move: ', nmax
			temp2 = state
			print 'resulting state: '
			print np.reshape(temp2, (rows, cols))

	if game.gameWon:
		if verbose:
			print 'game won'
		gamesWon += 1

	if verbose:
		print 'game finished'

		
	total_num_moves += num_moves
	num_moves = 0

print 'Win rate:', float(gamesWon) / num_games
print 'Average moves: ', float(total_num_moves)/num_games
print 'Train accuracy:', model.score(X_train, Y_train)
print 'Test accuracy:', model.score(X_test, Y_test)