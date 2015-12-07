from random import randint
import random
import numpy as np
import collections

# Class: Square
# Helper class designed to make it easy to implement a board with 
# squares that have 2 variables/states: 1) Whether the square is currently covered 
# or uncovered, and 2) whether the square is a bomb (value 9) or if it is not a bomb,
# how many bombs the square is touching (8-0).
#
# Square.location is the loaction of the square in the board, which is a LIST.
# Go from Square to raw location: location = square.location
# Go from raw location to Sqaure: square = board[location]

# Note: Most of the implementation of the MineSweeper class deals directly
# with Sqaure objects. Only the get_neighbors funtion uses the location
class Square(object):
    location = (0, 0)
    isUncovered = False
    value = 0


    def __init__(self, location):
        self.location = location

        
# Class: MineSweeper
# self.board: A list of Squares. Main way for interacting with game. 
#   self.board is initialized at start of game and continually updated with current state of game. 
# self.bomb_number: number of bombs on the board
# self.bomb_value: value stored in a square to indicate it contains a bomb
# self.covered_value: value used for state and label vectors for indicating covered or not
# self.gameEnd: True when # squares uncovered = row*col-bomb_number, or when a bomb is uncovered
# self.frontier: a list of all the covered Squares that have uncovered neighbors in the current game state
class MineSweeper(object):
    board = []  
    frontier = []

    row_size = 0
    column_size = 0

    bomb_number = 0

    bomb_value = 9
    covered_value = 10

    num_uncovered = 0
    gameEnd = False

    score = 0
    gameWon = False

    verbose = False
    
    # Initiliaze game
    #
    # sets up self.board by appending Squares. Adds bombs according to difficulty 
    # and sets the value of each square by calling insert_mines()
    def __init__(self, row=4, column=4, difficulty=1, verbose=False):
        self.row_size = row
        self.column_size = column

        self.board = []
        self.frontier = []

        self.verbose = verbose

        for row in range(row):
            self.board.append([])
            for col in range(column):
                self.board[row].append(Square((row, col)))         
    
        if difficulty == 1:
            if row * column < 10:
                self.bomb_number = 2
            if row*column < 20:
                self.bomb_number = 3
            if row * column < 30:           
                self.bomb_number = 5                        
            elif row * column < 100:
                self.bomb_number = 10           
            else:
                self.bomb_number = 15       
        elif difficulty == 2:
            if row * column < 30:
                self.bomb_number = 10   
            elif row * column < 100:
                self.bomb_number = 15   
            else:
                self.bomb_number = 20
        elif difficulty == 3:   
            if row * column < 30:
                self.bomb_number = 15
            elif row * column < 100:
                self.bomb_number = 20       
            else:
                self.bomb_number = 30
        else:
            raise Exception("Your level input is wrong!")   

        self.insert_mines()

        if verbose:
            print "Playing on %d x %d board with difficulty %d" % \
                (row, column, difficulty)

    # returns a vector of the current state of the board values (not Squares). If 
    # a Square is covered, the state vector state represents this with self.covered_value. 
    # Otherwise the Square is uncovered and the value of the square is used. Note that 
    # self.bomb_value should never appear in the state vector because all bombs should be covered
    # or the game should end.
    def get_state(self):
        state = []
        for row in range(self.row_size):
            for col in range(self.column_size):
                square = self.board[row][col]
                if square.isUncovered == False:
                    state.append(self.covered_value)
                else:
                    state.append(square.value)
        #print state
        return state

    # returns a vector of the state if the board were rotated 90 degrees clockwise. To
    # be used for decreasing state space by eliminating similar board configurations

    def rotate_90_clockwise(self, state):
        rotatedState = []
        for i in range(self.row_size):
            for j in range(self.column_size):
                rotatedState.append(state[self.get_state_index_from_location(self.column_size - j - 1, i)])

    def get_state_index_from_location(self, row, col):
        return row*self.row_size + col

    def get_location_from_state_index(self, index):
        return index / self.row_size, index % self.row_size

    # For the current state of the board, returns a labeling. 
    # Label is the same dimension as State. The numerical value for
    # a correct action given the given state is 1, and all other actions as 0.
    def get_label(self):
        label = []
        for row in range(self.row_size):
            for col in range(self.column_size):
                square = self.board[row][col]
                if square in self.frontier:
                    if square.value != self.bomb_value:
                        # could add some more check to determine if square is 
                        # actually a logical choice... + some probability
                        label.append(1)
                    else:
                        label.append(0)
                else:
                    label.append(0)

        return label

    # self.frontier contains the Squares on the frontier for the current board state.
    # A square is on the fonrtier if it is still covered but it is adjacent to a uncovered
    # square. Keeping track of the current frontier makes it easier to create the label
    # and choose a next move (Any square not in the frontier shouldn't be a valid move)
    def get_frontier(self):
        return self.frontier

    # Recursive function called to update the current state 
    # of self.board whenever a move is made. Uncovers the current square, as well
    # updating self.frontier. The recursive case happens when the square just
    # uncovered was a 0, in which case it is touching no bombs and we can recursively
    # uncover all its neighbors.
    def update_board(self, square):
        # Base case: reached a square that was previously uncovered. So, just return.
        if square.isUncovered == True:
            return

        # We are uncovering a square, so if it was in  self.frontier it can no longer be
        if square in self.frontier:
            self.frontier.remove(square)

        # uncover current square
        square.isUncovered = True
        self.num_uncovered += 1

        # Recursive case: uncover all neighbors
        if square.value == 0:
            # Get the neighbors if the square.value is 0
            for neighbor in self.get_neighbors(square).values():
                self.update_board(neighbor)
        # We are not going to uncover this square, so we need to update self.frontier by
        # adding all the neighbors of the current square if not already in self.frontier
        else:
            for neighbor in self.get_neighbors(square).values():
                # Add neighbors to frontier if not already uncovered and not already in frontier
                if neighbor.isUncovered == False and neighbor not in self.frontier:
                    self.frontier.append(neighbor)

    def get_init_state(self):
        state = []
        for i in range(self.row_size*self.column_size):
            state.append(self.covered_value)

        return state

    # Given a move of the board, returns updated game state
    # move is a integer, not a Square. Makes for an easier interface
    # If a move uncovers a bomb, game is over. Otherwise, update board with given move
    # Note: A move given by a player corresponding to an already uncovered square does nothing
    def get_next_state(self, square):
        if not square.isUncovered:
            if square.value == self.bomb_value:
                self.gameEnd = True
            else:
                self.score += 5
                self.update_board(square)

        # if all non-bomb squares have been uncovered, game is won
        if self.num_uncovered == self.row_size*self.column_size - self.bomb_number:
            self.gameEnd = True
            self.gameWon = True

        if self.verbose:
            print self.get_state()
            print self.get_label()

        return self.get_state()

    # Key function for actually determining the topology of the board (i.e. how we
    # go from a list to a square board). Basically just use the dimensions of the board
    # to get the possible neighbors and append them to list. Then, remove any invalid squares
    # from the list. Also some code to handle cases where the square is on the border
    def get_neighbors(self, square):
        location = square.location
        neighbors = {}
        i = 0
        for row in range(location[0]-1, location[0]+2):
            for col in range(location[1]-1, location[1]+2):
                if row == location[0] and col == location[1]:
                    continue
                if row >= 0 and row < self.row_size and col >= 0 and col < self.column_size:
                    neighbors[i] = self.board[row][col]
                i = i+1
        #print neighbors
        return neighbors
        # allneighborlist = []
        # neighborlist = []
        # #except right corner
        # if (location+1) % self.row_size != 0:
        #     allneighborlist.append(location+1) 
        #     allneighborlist.append(location+self.row_size+1)
        #     allneighborlist.append(location-self.row_size+1)
        # #except left corner 
        # if location % self.row_size != 0: 
        #     allneighborlist.append(location-1)
        #     allneighborlist.append(location+self.row_size-1)             
        #     allneighborlist.append(location-self.row_size-1)
        
        # #all fields
        # allneighborlist.append(location+self.row_size)
        # allneighborlist.append(location-self.row_size)

        # for neighbor in allneighborlist:
        #     if neighbor >= 0 and neighbor < len(self.board):
        #         neighborlist.append(self.board[neighbor])

        # return neighborlist



    #Insert specified number of mines into the area, increase numbers of its neigbours.
    def insert_mines(self):
        bombs = random.sample(range(0, self.row_size*self.column_size), self.bomb_number)
        bomb_positions = [(bomb/self.row_size, bomb % self.row_size) for bomb in bombs]
        
        for bomb in bomb_positions:
            self.board[bomb[0]][bomb[1]].value = self.bomb_value

        for bomb_position in bomb_positions:
            bomb = self.board[bomb_position[0]][bomb_position[1]]
            neigbourlist = self.get_neighbors(bomb)
            
            #increase proper neighbours one
            for neigbour in neigbourlist.values():
                if neigbour.value != self.bomb_value:
                    neigbour.value += 1

    #always choose a corner for the first move. (kind of cheating)
    def first_move(self, corner):
        return {
            0: 0,
            1: self.row_size - 1,
            2: self.row_size*self.column_size - 1 - self.row_size - 1,
            3: self.row_size*self.column_size - 1,
        }.get(corner, 0)

    # User interface: return whether move will lead to a bomb
    def is_bomb(self, square):
        return square.value == self.bomb_value

    def get_square(self, location):
        return self.board[location[0]][location[1]]

def generate_global_data(num_simulations = 10, row=4, column = 4, difficulty= 1, save_data = False):
    X = []
    Y = []

    for i in range(num_simulations):
        game = MineSweeper(row, column, difficulty)

        # Pick the first move to be a corner
        #corner = randint(0, 3)
        #move = game.first_move(corner)

        # Pick first move randomly
        move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
        while game.is_bomb(move):
            move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

        # Update the board with the first move
        state = game.get_next_state(move)
        label = game.get_label()

        # Play game to completion
        while not game.gameEnd:
            # add the new state of the board and the label corresponding to 
            # correct next moves to training data set
            X.append(state)
            Y.append(label)

            # choose a random next move in frontier that does not lead to a game end
            choices = game.get_frontier()
            randomOrdering = random.sample(range(len(choices)), len(choices))
            move = None
            for choice in randomOrdering:
                move = choices[choice]
                if not game.is_bomb(move):
                    break

            # If there are no valid moves in the frontier, choose a random move from the entire board
            if game.is_bomb(move):
                move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
                while game.is_bomb(move) or move.isUncovered:
                    move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

            # move the game one step foward using the selected move
            state = game.get_next_state(move)
            label = game.get_label()

    X = np.array(X, 'float')
    Y = np.array(Y, 'float')

    if save_data:
        # Save numpay array data and labels
        np.save('train_data', X)
        np.save('train_labels', Y)

    return X, Y

def generate_local_data(num_simulations = 10, row=4, column = 4, difficulty= 1, save_data = False):
    X = []
    Y = []

    for i in range(num_simulations):
        game = MineSweeper(row, column, difficulty)

        # Pick the first move to be a corner
        #corner = randint(0, 3)
        #move = game.first_move(corner)

        # Pick first move randomly
        location = (randint(0, game.row_size), randint(0, game.row_size))
        move = game.get_square(location)
        while game.is_bomb(move):
            move = randint(0, len(game.board)-1)

        # Update the board with the first move
        state = game.get_next_state(move)
        label = game.get_label()

        # Play game to completion
        while not game.gameEnd:
            # add the new state of the board and the label corresponding to 
            # correct next moves to training data set
            X.append(state)
            Y.append(label)

            # choose a random next move in frontier that does not lead to a game end
            choices = game.get_frontier()

            randomOrdering = random.sample(range(len(choices)), len(choices))
            move = None
            for choice in randomOrdering:
                move = choices[choice]
                if not game.is_bomb(move):
                    break

            # If there are no valid moves in the frontier, choose a random move from the entire board
            if game.is_bomb(move):
                location = (randint(0, game.row_size), randint(0, game.row_size))
                move = game.get_square(location)
                while game.is_bomb(move) or game.isUncovered(move):
                    move = randint(0, len(game.board)-1)

            # move the game one step foward using the selected move
            state = game.get_next_state(move)
            label = game.get_label()

    X = np.array(X, 'float')
    Y = np.array(Y, 'float')

    if save_data:
        # Save numpay array data and labels
        np.save('train_data', X)
        np.save('train_labels', Y)

    return X, Y

# Generates a map containing estimated q values for each (state, action) pair,
# where the action is the location of the next move. Generates this by playing
# random moves from the frontier, and recording whether or not they result in
# finding a mine.
def generate_state_map_by_random_playing(num_total_simulations=100, row=4, col=4, difficulty=1, rewardValue=1):

    qMap = collections.Counter()

    for i in xrange(num_total_simulations):
        game = MineSweeper(row, col, difficulty)

        location = (randint(0, game.row_size-1), randint(0, game.column_size-1))
        nextMove = game.get_square(location)
        currentState = game.get_init_state()
        reward = 0

        while True:
            reward = rewardValue if not game.is_bomb(nextMove) else -1*rewardValue
            #print nextMove.location, "reward: ", reward
            stateAndAction = (tuple(currentState), nextMove.location)
            qMap[stateAndAction] += reward
            #print qMap
            currentState = game.get_next_state(nextMove)

            if game.gameEnd:
                break

            frontier = game.get_frontier()
            nextMove = random.choice(frontier)

    return qMap

# Generates a map containing estimated q values for each (state, action) pair,
# where the action is the location of the next move. Generates this by picking
# a random move from the frontier, then by inputting all correct moves into the 
# map. Picks a random correct move and repeats. Performs better than the alternative
# using random playing, presumably because it gathers more data.
def generate_state_map_using_label(num_total_simulations=100, row=4, col=4, difficulty=1, reward=1):
    qMap = collections.Counter()

    cantWin = 0
    for iterationNo in xrange(num_total_simulations):
        if iterationNo % 1000 == 0:
            print "Iteration number: ", iterationNo
        game = MineSweeper(row, col, difficulty)

        location = (randint(0, game.row_size-1), randint(0, game.column_size-1))
        nextMove = game.get_square(location)
        currentState = game.get_next_state(nextMove)

        while not game.gameEnd:
            label = game.get_label()
            currentState = game.get_state()
            listOfCorrectMoveIndexes = []
            for j in range(len(label)):
                stateAndAction = (tuple(currentState), game.get_location_from_state_index(j))
                if label[j] == 1:
                    qMap[stateAndAction] += reward
                    listOfCorrectMoveIndexes.append(j)

            if not listOfCorrectMoveIndexes:
                cantWin += 1
                break

            index = random.choice(listOfCorrectMoveIndexes)
            randomCorrectLocation = game.get_location_from_state_index(index)
            nextMove = game.get_square(randomCorrectLocation)
            currentState = game.get_next_state(nextMove)

    print "Fraction of games lost due to looking only on frontier", (float(cantWin)/num_total_simulations)
    return qMap

def getNextMove(qMap, game):
    bestMoveLocation = (-1, -1)
    maxQValue = float("-inf")

    possibleMoves = map(lambda x: x.location, game.get_frontier())
    # print possibleMoves
    stateAsTuple = tuple(game.get_state())
    undiscovered = 0
    discovered = 0
    for move in possibleMoves:
        stateAndAction = (stateAsTuple, move)
        if stateAndAction not in qMap:
            #print "Undiscovered state"
            undiscovered += 1
        else:
            discovered += 1

        q = qMap[(stateAsTuple, move)]
        # print "Move: ", move
        # print "Q value: ", q
        # print ""
        if q > maxQValue:
            bestMoveLocation, maxQValue = move, q

    print "Undiscovered pairs: ", undiscovered
    print "Discovered pairs: ", discovered
    print ""
    return game.get_square(bestMoveLocation)
