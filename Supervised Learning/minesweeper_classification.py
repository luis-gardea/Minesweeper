import minesweeper_ml
import numpy as np 
from sklearn import linear_model
from random import randint
from sklearn import svm
from sklearn.externals import joblib
from sklearn import svm, grid_search
from sklearn import preprocessing

verbose = True

rows = 4
cols = 4
bombs = 5
area = 4

# use to load data instead of generate
#X_train = np.load('train_data.npy')
#Y_train = np.load('train_labels.npy')

X_train, Y_train = minesweeper_ml.generate_local_data(800, rows, cols, bombs, area)
# clf = linear_model.LogisticRegression()

# SVM model
# clf = svm.SVC(C=3, kernel = 'rbf', max_iter=10000, verbose=True)
X_train = preprocessing.scale(X_train)
clf = grid_search.GridSearchCV(svm.SVC(kernel = 'rbf', max_iter=1000), {'C':[.2, 1, 5, 10]})

clf.fit(X_train, Y_train)

X_test, Y_test = minesweeper_ml.generate_local_data(100, rows, cols, bombs, area)
print 'finished fitting'
# use to save model
#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')

##########################################################################################
# Play actual games of minesweeper with network acting as agent
gamesWon = 0;
num_games = 1000
games_played = num_games
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
	if game.gameEnd: games_played -= 1

	num_moves = 0
	while not game.gameEnd:
		temp2 = state
		print 'make predictions on this state'
		print np.reshape(temp2, (rows, cols))
		# Get next move from agent
		perimeter = game.get_frontier()
		print [square.location for square in perimeter]
		predictions = []
		# predictions1 = []
		move = None
		for square in perimeter:
			x = game.get_area_label(square, area)
			x = np.array(x)
			y =  clf.predict(x)[0]
			print square.location, y
			if y == 1:
				# predictions1.append(clf.predict_proba(x)[0][1])
				move = square
				break
		if move == None:
			games_played -= 1
			break
			move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
			i = 1
			while move in perimeter and move.isUncovered:
				if i == game.row_size*game.column_size-1:
					break
				move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
				i += 1

		# for square in predictions1:
		# 	x = game.get_area_label(square, area)
		# 	x = np.array(x)
		# 	predictions.append(clf.predict_proba(x)[0][1])


		# nmax = predictions.index(max(predictions))
		# move = perimeter[nmax]
		# print move.location

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
print 'Games played: ', games_played
print 'Games won:', gamesWon, 'Win rate:', float(gamesWon) / games_played
print 'Average moves: ', float(total_num_moves)/games_played
print 'Train accuracy:', clf.score(X_train, Y_train)
print 'Test accuracy:', clf.score(X_test, Y_test)