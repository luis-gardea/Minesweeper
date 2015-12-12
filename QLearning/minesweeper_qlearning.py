import minesweeper
from random import randint

numLearningIterations = 5000000
numPlayingIterations = 10000
numRows = 4
numCols = 4
difficulty = 1

#qMap = minesweeper.generate_state_map_by_random_playing(numLearningIterations, numRows, numCols, difficulty)

qMap = minesweeper.generate_state_map_using_label(numLearningIterations, numRows, numCols, difficulty)

# This prints out the qMap in a more readable manner
def print_map_by_state(qValueMap):

	otherMap = {}
	
	for state, action in qMap:
		if state in otherMap:
			otherMap[state].append(action)
		else:
			otherMap[state] = [action]

	for state in otherMap:
		print state
		for action in otherMap[state]:
			pair = (state, action)
			print "        ", action, ": ", str(qMap[pair])

# Simulate the game play and determine error rate

avgPercentTilesCleared = 0.0
numWins = 0
numGames = 0

for i in xrange(numPlayingIterations):
	print "Game: ", i
	numTilesCleared = 0
	game = minesweeper.MineSweeper(numRows, numCols, difficulty)
	randomLocation = (randint(0, game.row_size-1), randint(0, game.column_size-1))
	firstMove =  game.get_square(randomLocation)

	while game.is_bomb(firstMove):
		randomLocation = (randint(0, game.row_size-1), randint(0, game.column_size-1))
		firstMove =  game.get_square(randomLocation)		

	currentState = game.get_next_state(firstMove)

	while not game.gameEnd:
		numTilesCleared += 1
		nextMove = minesweeper.getNextMove(qMap, game)
		game.get_next_state(nextMove)
			
	#print "cleared %d tiles" % numTilesCleared
	if game.gameWon:
		numWins += 1

	avgPercentTilesCleared = avgPercentTilesCleared * (float(numGames)/(numGames + 1)) + \
								 (float(numTilesCleared)/(numRows * numCols))/(numGames + 1)

	numGames += 1


#print numWins
successRate = (float(numWins)/numGames)*100
print "Played %d games, winning %f%% of the time." % (numPlayingIterations, successRate)
print "Cleared an average of %f%% of the board." % (avgPercentTilesCleared*100)
