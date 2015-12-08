from random import randint
import random
import numpy as np
import sys
import mines

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
    def __init__(self, location):
        self.location = location
        self.isUncovered = False
        self.value = 0
        self.isMarked = False

        
# Class: MineSweeper
# self.board: A list of Squares. Main way for interacting with game. 
#   self.board is initialized at start of game and continually updated with current state of game. 
# self.bomb_number: number of bombs on the board
# self.bomb_value: value stored in a square to indicate it contains a bomb
# self.covered_value: value used for state and label vectors for indicating covered or not
# self.gameEnd: True when # squares uncovered = row*col-bomb_number, or when a bomb is uncovered
# self.frontier: a list of all the covered Squares that have uncovered neighbors in the current game state
class MineSweeper(object):
    # Initiliaze game
    #
    # sets up self.board by appending Squares. Adds bombs according to difficulty 
    # and sets the value of each square by calling insert_mines()
    def __init__(self, row=4, column=4, nbombs=5, verbose=False):
        self.row_size = row
        self.column_size = column

        self.board = []
        self.frontier = []

        self.verbose = verbose

        self.bomb_number = nbombs

        self.bomb_value = -1
        self.covered_value = -2
        self.maked_value = -3
        self.offboard_value = -4

        self.num_uncovered = 0
        self.gameEnd = False

        self.score = 0
        self.gameWon = False

        spaces = set((x,y) for x in range(self.row_size) for y in range(self.column_size))
        self.solver = mines.Solver(spaces)
        info = mines.Information(frozenset(spaces), self.bomb_number)
        self.solver.add_information(info)

        for row in range(self.row_size):
            self.board.append([])
            for col in range(self.column_size):
                self.board[row].append(Square((row, col)))

        self.insert_mines()

        if verbose:
            print "Playing on %d x %d board with %d bombs" % \
                (self.row_size, self.column_size, nbombs)

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
                if square.isMarked:
                    state.append(self.marked_value)
                elif square.isUncovered == False:
                    state.append(self.covered_value)
                else:
                    state.append(square.value)
        return state    

    # For the current state of the board, returns a labeling. 
    # Label is the same dimension as State. The numerical value for
    # a correct action given the given state is 1, and all other actions as 0.
    def get_label(self):
        label = [-1 for x in range(self.row_size) for y in range(self.column_size)]
        try:
            self.solver.solve()
        except mines.UnsolveableException:
            print "This configuration has no solutions."
            sys.exit(0)
        forsure = self.solver.solved_spaces
        for loc, value in forsure.iteritems():
            pos = loc[0]*self.row_size + loc[1]
            label[pos] = 1 - value
        probabilities, total = self.solver.get_probabilities()
        for loc, prob in probabilities.iteritems():
            pos = loc[0]*self.row_size + loc[1]
            label[pos] = 1.0 - float(prob)/total

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
        self.solver.add_known_value(square.location, 0)
        self.num_uncovered += 1

        # Recursive case: uncover all neighbors
        if square.value == 0:
            # Get the neighbors if the square.value is 0
            for neighbor in self.get_neighbors(square).values():
                self.update_board(neighbor)
        # We are not going to uncover this square, so we need to update self.frontier by
        # adding all the neighbors of the current square if not already in self.frontier
        else:
            nset = set([])
            for neighbor in self.get_neighbors(square).values():
                # Add neighbors to frontier if not already uncovered and not already in frontier
                if neighbor.isUncovered == False and neighbor not in self.frontier:
                    self.frontier.append(neighbor)
                if neighbor.isUncovered == False:
                    nset.add(neighbor.location)
            info = mines.Information(frozenset(nset), square.value)
            self.solver.add_information(info)

    def get_init_state(self):
        state = []
        for i in range(self.row_size*self.column_size):
            state.append(covered_value)

        return state

    def get_area_label(self, square, n):
        location = square.location
        label = [self.offboard_value]*((2*n+1)**2 - 1)
        i = 0
        for row in range(location[0]-n, location[0]+n+1):
            for col in range(location[1]-n, location[1]+n+1):
                if row == location[0] and col == location[1]:
                    continue
                if row >= 0 and row < self.row_size and col >= 0 and col < self.column_size:
                    neighbor = self.get_square((row, col))

                    label[i] = neighbor.value if neighbor.isUncovered else self.covered_value
                i = i+1

        return label

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
                print 'game won'
            return self.get_state()

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
        return neighbors

    #Insert specified number of mines into the area, increase numbers of its neigbours.
    def insert_mines(self):
        bombs = random.sample(range(0, self.row_size*self.column_size-1), self.bomb_number)
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

    # User interface: return whether move will lead to a bomb
    def is_bomb(self, square):
        return square.value == self.bomb_value

    def get_square(self, location):
        return self.board[location[0]][location[1]]



def generate_global_data(num_simulations = 10, row=4, column = 4, nbombs= 1, save_data = False):
    X = []
    Y = []

    for i in range(num_simulations):
        game = MineSweeper(row, column, nbombs)

        # Pick the first move to be a corner
        #corner = randint(0, 3)
        #move = game.first_move(corner)

        # Pick first move randomly
        # move = game.get_square((0,0))
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
            if state not in X:
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




def generate_local_data(num_simulations = 10, row=4, column = 4, nbombs= 1, n = 1, save_data = False):
    X = []
    Y = []

    for i in range(num_simulations):
        game = MineSweeper(row, column, nbombs)

        # Pick the first move to be a corner
        #corner = randint(0, 3)
        #move = game.first_move(corner)

        # Pick first move randomly
        # move = game.get_square((0,0))
        move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))
        while game.is_bomb(move):
            move = game.get_square((randint(0, game.row_size-1), randint(0, game.column_size-1)))

        # Update the board with the first move
        state = game.get_next_state(move)

        # Play game to completion
        while not game.gameEnd:
            if state not in X:
                choices = game.get_frontier()
                label = game.get_label()
                for choice in choices:
                    x = game.get_area_label(choice, n)
                    X.append(x)
                    if label[choice.location[0]*game.row_size +choice.location[1]] == 1:
                        Y.append(1)
                    else:
                        Y.append(0)
                    # Y.append(0 if game.is_bomb(choice) else 1)          

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

    X = np.array(X, "float")
    Y = np.array(Y, 'float')

    if save_data:
        # Save numpay array data and labels
        np.save('train_data', X)
        np.save('train_labels', Y)

    return X, Y