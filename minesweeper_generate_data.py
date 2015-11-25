from minesweeper import MineSweeper
from random import randint
import random
import numpy as np

def generate_data(num_simulations = 10, row = 4, column = 4, difficulty= 1, save_data = False):
    X = []
    Y = []
    print "Playing %d games on %d x %d board with difficulty %d" % \
        (num_simulations, row, column, difficulty)

    for i in range(num_simulations):
        game = MineSweeper(row, column, difficulty)

        # Pick the first move randomly. Make sure we don't start off with a bomb
        move = randint(0, len(game.board)-1)
        while game.board[move].value == game.bomb_value:
            move = randint(0, len(game.board)-1)

        # Update the board with the first move
        state = game.get_next_state(move)
        label = game.get_label()

        # Play game to completion
        while game.gameEnd == False:
            # add the new state of the board and the label corresponding to 
            # correct next moves to training data set
            X.append(state)
            Y.append(label)

            # choose a random next move that does not lead to a game end
            choices = game.get_frontier()
            randomOrdering = random.sample(range(len(choices)), len(choices))
            move = None
            for choice in randomOrdering:
                move = choices[choice]
                if game.board[move].value != game.bomb_value:
                    break

            # If there are no valid moves in the frontier, choose a random move from the entire board
            if game.board[move].value == game.bomb_value:
                move = randint(0, len(game.board)-1)
                while game.board[move].value == game.bomb_value or game.board[move].isUncovered:
                    move = randint(0, len(game.board)-1)

            # move the game one step foward using the selected move
            state = game.get_next_state(move)
            label = game.get_label()

    X = np.array(X)
    Y = np.array(Y)
    if save_data:
        # Save data and labels
        np.save('train_data', X)
        np.save('train_labels', Y)

    return X, Y

