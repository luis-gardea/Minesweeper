import minesweeper_ml
import numpy as np 
from sklearn import linear_model
from random import randint
from sklearn import svm
from sklearn.externals import joblib

verbose = False

rows = 4
cols = 4
bombs = 3
area = 2

# use to load data instead of generate
#X_train = np.load('train_data.npy')
#Y_train = np.load('train_labels.npy')

X_train, Y_train = minesweeper_ml.generate_local_data(200, rows, cols, bombs, area)
clf = linear_model.LogisticRegression(penalty='l1')

# SVM model
# clf = svm.SVC()

clf.fit(X_train, Y_train)

X_test, Y_test = minesweeper_ml.generate_local_data(100, rows, cols, bombs, area)

# use to save model
#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')

##########################################################################################
# Play actual games of minesweeper with network acting as agent
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
		predictions = []
		for square in perimeter:
			x = game.get_area_label(square, area)
			x = np.array(x)
			predictions.append(clf.predict_proba(x)[0][1])

		nmax = predictions.index(max(predictions))
		move = perimeter[nmax]

		# Update board
		state = np.array(game.get_next_state(move))
		num_moves += 1

	if game.gameWon:
		if verbose:
			print 'game won'
		gamesWon += 1

	if verbose:
		print 'game finished'

	total_num_moves += num_moves
	num_moves = 0

print 'Games won:', gamesWon, 'Win rate:', float(gamesWon) / num_games
print 'Average moves: ', float(total_num_moves)/num_games
print 'Train accuracy:', clf.score(X_train, Y_train)
print 'Test accuracy:', clf.score(X_test, Y_test)