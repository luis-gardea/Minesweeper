from random import randint
import random
import numpy as np

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
    location = 0
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

        for i in range(row*column):
            self.board.append(Square(i))         
    
        if difficulty == 1:
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
    # a Square is covered, the state vecotr state represents this with self.covered_value. 
    # Otherwise the Square is uncovered and the value of the square is used. Note that 
    # self.bomb_value should never appear in the state vector because all bombs should be covered
    # or the game should end.
    def get_state(self):
        state = []
        for square in self.board:
            if square.isUncovered == False:
                state.append(self.covered_value)
            else:
                state.append(square.value)

        return state    

    # For the current state of the board, returns a labeling. 
    # Label is the same dimension as State. The numerical value for
    # a correct action given the given state is 1, and all other actions as 0.
    def get_label(self):
        label = []
        for square in self.board:
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
        frontierLocations = []
        for square in self.frontier:
            frontierLocations.append(square.location)
        return frontierLocations

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
            for neighbor in self.get_neighbors(square):
                self.update_board(neighbor)
        # We are not going to uncover this square, so we need to update self.frontier by
        # adding all the neighbors of the current square if not already in self.frontier
        else:
            for neighbor in self.get_neighbors(square):
                # Add neighbors to frontier if not already uncovered and not already in frontier
                if neighbor.isUncovered == False and neighbor not in self.frontier:
                    self.frontier.append(neighbor)

    def get_init_state(self):
        state = []
        for i in range(self.row_size*self.column_size):
            state.append(covered_value)

        return state

    # Given a move of the board, returns updated game state
    # move is a integer, not a Square. Makes for an easier interface
    # If a move uncovers a bomb, game is over. Otherwise, update board with given move
    # Note: A move given by a player corresponding to an already uncovered square does nothing
    def get_next_state(self, move):
        square = self.board[move]
        if square.isUncovered == False:
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
        allneighborlist = []
        neighborlist = []
        #except right corner
        if (location+1) % self.row_size != 0:
            allneighborlist.append(location+1) 
            allneighborlist.append(location+self.row_size+1)
            allneighborlist.append(location-self.row_size+1)
        #except left corner 
        if location % self.row_size != 0: 
            allneighborlist.append(location-1)
            allneighborlist.append(location+self.row_size-1)             
            allneighborlist.append(location-self.row_size-1)
        
        #all fields
        allneighborlist.append(location+self.row_size)
        allneighborlist.append(location-self.row_size)

        for neighbor in allneighborlist:
            if neighbor >= 0 and neighbor < len(self.board):
                neighborlist.append(self.board[neighbor])

        return neighborlist

    #Insert specified number of mines into the area, increase numbers of its neigbours.
    def insert_mines(self):
        bomb_positions = random.sample(range(0, len(self.board)-1), self.bomb_number)
        
        for bomb in bomb_positions:
            self.board[bomb].value = self.bomb_value

        for bomb_position in bomb_positions:
            bomb = self.board[bomb_position]
            neigbourlist = self.get_neighbors(bomb)
            
            #increase proper neighbours one
            for neigbour in neigbourlist:
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

def generate_data(num_simulations = 10, row=4, column = 4, difficulty= 1, save_data = False):
    X = []
    Y = []

    for i in range(num_simulations):
        game = MineSweeper(row, column, difficulty)

        # Pick the first move to be a corner
        #corner = randint(0, 3)
        #move = game.first_move(corner)
        move = randint(0, len(game.board)-1)
        while game.board[move].value == game.bomb_value:
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

    X = np.array(X, 'float')
    Y = np.array(Y, 'float')

    if save_data:
        # Save numpay array data and labels
        np.save('train_data', X)
        np.save('train_labels', Y)

    return X, Y
