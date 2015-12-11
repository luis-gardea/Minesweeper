import minesweeper_ml
import numpy as np 
from sklearn import linear_model
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from sklearn import svm
from sklearn.kernel_ridge import KernelRidge
from sklearn.grid_search import GridSearchCV
import sys
from sklearn.svm import SVR
from sklearn import preprocessing

verbose = False

rows = 4
cols = 4
bombs = 6

# use to load data instead of generate
#X_train = np.load('train_data.npy')
#Y_train = np.load('train_labels.npy')

X_train, Y_train = minesweeper_ml.generate_global_data(1200, rows, cols, bombs, True)

# Pain linear regression
# model = linear_model.LinearRegression()

# Linear regression Model norm factor
#model = linear_model.Ridge(alpha = .5)

# Linear regression model with kernel
# model = KernelRidge(alpha=.3, kernel='rbf')

# model = linear_model.MultiTaskElasticNetCV()
model = GridSearchCV(KernelRidge(kernel='rbf', gamma=0.1),
                  param_grid={"alpha": [1e0, 0.1, 1e-2, 1e-3],
                              "gamma": np.logspace(-2, 2, 5)})

model.fit(X_train, Y_train)

X_test, Y_test = minesweeper_ml.generate_global_data(1000, rows, cols, bombs)

#########################################################################################
# Play actual games of minesweeper with network acting as agent

gamesWon = 0
num_games = 1000
games_played = num_games
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
		games_played -= 1

    # Update the board with the first move
	state = np.array(game.get_next_state(move))
	num_moves = 0
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

print 'Win rate:', float(gamesWon) / games_played
print 'Average moves: ', float(total_num_moves)/games_played
print 'Train accuracy:', model.score(X_train, Y_train)
print 'Test accuracy:', model.score(X_test, Y_test)