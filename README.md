# Minesweeper 

##This is the code that was utilized for the CS 221/229 project, in which machine learning and AI methods were applied to solve the game of Minesweeper.
##Several approaches were used involving logistic regression, linear regression, reinforcement learning/QLearning, and CSPs.

###CSP method:
Enter the CSP directory
	
	cd CSP/

To run the nongraphical version, run the command (with optional flags)
	
	python pgms.py [-r <num rows>] [-c <num cols>] [-m <num mines>] [-n <num games>] [-i for intermediate game] [-e for expert game] [-b for beginner game] [-S <num sets>] [-v verbose] [-noreal can lose on first try]

To run the graphical version, run the command (also with optional flags)
	
	python gui.py [-r <num rows>] [-c <num cols>] [-m <num mines>] [-i for intermediate game] [-e for expert game] [-b for beginner game] [-S <num sets>] [-v verbose] [-noreal can lose on first try]

Once the GUI is up, clicking play will play a game and show the final result. Dark gray signifies tiles that had 0 mines. Lighter gray signifies other values for a square. Purple tiles signify a mine that was marked as a mine. Whenever a game is lost, all of the mines on the board are shown, these are the red tiles. Clicking on QUIT will quit the program.