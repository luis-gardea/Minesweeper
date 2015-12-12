import minesweeper
import numpy as np 
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from random import randint

#X = np.load('train_data.npy')
#Y = np.load('train_labels.npy')
rows = 4
cols = 4
bombs = 4

X_train, Y_train = minesweeper.generate_global_data(500, rows, cols, bombs)
svm = OneVsRestClassifier(svm.SVC())
svm.fit(X_train, Y_train)
print 'Train accuracy:', svm.score(X_train, Y_train)

X_test, Y_test = minesweeper.generate_global_data(100, rows, cols, bombs)
print 'Test accuracy:', svm.score(X_test, Y_test)

print Y_test
print svm.predict(X_test)

#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')
#########################################################################################
# Play actual games of minesweeper with network acting as agent

gamesWon = 0
num_games = 5
for i in range(num_games):
	#needs to be same dimensions as training data
	game = minesweeper.MineSweeper(row, col, bombs, True)

	# Pick the first move to be a corner
	#corner = randint(0, 3)
	#move = game.first_move(corner)
	# move = randint(0, len(game.board)-1)
	# while game.board[move].value == game.bomb_value:
	# 	move = randint(0, len(game.board)-1)
	move = game.get_square((0,0))

    # Update the board with the first move
	state = np.array(game.get_next_state(move))

	while not game.gameEnd:
		# Get next move from agent
		predictions = svm.predict(X_test)
		print 'predictions'
		temp = predictions
		print np.reshape(np.array(temp), (row, col))

		nmax = np.argmax(predictions)
		move = game.get_square((nmax/game.row_size, nmax % game.row_size))
		while move.isUncovered:
			predictions[0][nmax] = -2
			nmax = np.argmax(predictions)
			move = game.get_square((nmax/game.row_size, nmax % game.row_size))
		print nmax
		# Update board
		state = np.array(game.get_next_state(move))
		temp2 = state
		print np.reshape(temp2, (row, col))

	if game.gameWon:
		gamesWon += 1

	print 'game finished'

print 'Win rate:', float(gamesWon) / num_games

##########################################################################################
# Play actual games of minesweeper with network acting as agent

# gamesWon = 0;
# num_games = 50
# for i in range(num_games):
# 	#needs to be same dimensions as training data
# 	game = minesweeper.MineSweeper(rows, cols, bombs, True)

# 	# Pick the first move to be a corner
# 	#corner = randint(0, 3)
# 	#move = game.first_move(corner)
# 	move = game.get_square((0,0))
# 	# move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
# 	# while game.is_bomb(move):
# 	# 	move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

#     # Update the board with the first move
# 	state = np.array(game.get_next_state(move))

# 	while not game.gameEnd:
# 		# Get next move from agent
# 		perimeter = game.get_frontier()
# 		predictions = []
# 		for square in perimeter:
# 			x = [11]*8
# 			for index, neighbor in game.get_neighbors(square).iteritems():
# 				x[index] = neighbor.value if neighbor.isUncovered else game.covered_value

# 			x = np.array(x)
# 			predictions.append(svm.predict(x)[0])


# 		nmax = predictions.index(max(predictions))
# 		print [square.location for square in perimeter]
# 		print predictions
# 		move = perimeter[nmax]
# 		print move.location
        
# 		while move.isUncovered:
# 			predictions[nmax] = -2
# 			nmax = predictions.index(max(predictions))
# 			move = perimeter[nmax]

# 		# Update board
# 		state = np.array(game.get_next_state(move))
# 		print np.reshape(state, (rows, cols))

# 	if game.gameWon:
# 		print 'Game won!'
# 		gamesWon += 1

# print 'Games won:', gamesWon, 'Win rate:', float(gamesWon) / num_games