from random import randint
import random

class Square(object):
    isUncovered = False
    value = 0

    def __init__(self):

        
class MineSweeper(object):
    board = []  
    row_size = 0
    column_size = 0
    bomb_number = 0
    bomb_value = 9
    covered_value = 10
    gameEnd = False
    score = 0
    frontier = []

    #Initiliaze game
    def __init__(self, row, column, difficulty):

        self.row_size = row
        self.column_size = column
        for i in range(row*column):
            self.board.append(Square())         
    
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

    def get_state(self, board):
        state = []
        for square_num in self.board:
            if board[square_num].isUncovered == False:
                state.append(self.covered_value)
            else:
                state.append(square.value)

        return state    

    def get_label(self, frontier):
        label = []
        for square_num in range(len(board)):
            if board[square_num] in frontier:
                if board[square_num].value != self.bomb_value:
                    # could add some more check to determine if square is 
                    # actually a logical choice...
                    label.append(1)
                else:
                    label.append(0)
            else:
                label.append(0)

        return label

    def get_frontier(self):
        return frontier

    def update_frontier(self, square):
        if self.board[square].isUncovered = False: return



        if self.board[square].value = 0:
            neighbors = self.get_neighbors(square)

            # Get the neighbors if the cell is empty
            for neighbors in self.get_neighbors(square):
                    # Repeat function for each neighbor that doesn't have a flag
                    if currgrid[r][c] != 'F':
                        showcells(grid, currgrid, r, c)
            else:
                for r, c in getneighbors(grid, rowno, colno):
                    # Add neighbors to frontier if not already uncovered
                    if currgrid[r][c] != ' ':
                        frontier.append((r,c))
        else:
        


    def get_init_state(self):
        state = []
        for i in range(self.row_size*self.column_size):
            state.append(covered_value)

        return state;

    # given a move of the board, returns 
    def update_board(self, move):
        if(self.board[move].isUncovered) == False:
            if self.board[self.row_size * (user_row-1) + (user_column-1)].value == self.bomb_value:
                gameEnd = True
            else:
                self.board[move].isUncovered = True
                score += 5
                update_frontier(move)

        return self.get_state()


    def get_neighbors(self, square):
        neighborlist = []
        #except right corner
        if (square+1) % self.row_size != 0:
            neighborlist.append(square+1) 
            neighborlist.append(square+self.row_size+1)
            neighborlist.append(square-self.row_size+1)
        #except left corner 
        if square % self.row_size != 0: 
            neighborlist.append(square-1)
            neighborlist.append(square+self.row_size-1)             
            neighborlist.append(square-self.row_size-1)
        
        #all fields
        neighborlist.append(square+self.row_size)
        neighborlist.append(square-self.row_size)

        for neighbor in neighborlist:
            if neighbor < 0 or neighbor >= len(self.board):
                neighborlist.remove(neighbor)

        return neighborlist

    #Insert specified number of mines into the area, increase numbers of its neigbours.
    def insert_mines(self):
        bomb_position = random.sample(range(0, len(self.board)-1), self.bomb_number)
        
        for bomb in bomb_position:
            self.board[bomb].value = self.bomb_value

        for locatedBomb in bomb_position:
            neigbourlist = self.get_neighbors(locatedBomb)
            
            #increase proper neighbours one
            for neigbour in neigbourlist:
                if self.board[neigbour].value != self.bomb_value:
                    self.board[neigbour].value += 1

#Testing class
num_games = 1000
X = []
Y = []

print "Welcome to minesweeper game!"
row = 8
column = 8
difficulty= 1
print "Playing %d x %d board on difficulty %d" % row, column, difficulty

for i in range(num_games):
    try:
        game= MineSweeper(row, column, difficulty)
        #state = game.get_init_state()
        move = randint(0, len(game.board)-1)
        while game.gameEnd == False:
            #move the game one step foward using a selected move
            state = game.update_board(move)
            label = game.get_label()

            #add the new state of the board and the label corresponding to 
            #correct next moves to training data set
            X.append(state)
            Y.append(label)

            #choose a random next move that does not lead to a game end
            choices = game.get_frontier()
            move = randint(0, len(choices)-1)
            while choices[move] != game.bomb_value:
                move = randint(0, len(game.board)-1)
            
            


    except Exception as e:
        print e
