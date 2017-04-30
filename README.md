# Minesweeper 

## This is the code that was utilized for the CS 221/229 project, in which machine learning and AI methods were applied to solve the game of Minesweeper.
## Several approaches were used involving logistic regression, linear regression, reinforcement learning/QLearning, and CSPs.

### Supervised Learning methods:
Enter the Supervised directory
	
	cd Supervised/

To run the logistic regression classifier, run the command

	python logreg_classification.py

To run the SVM  classifier, run the command

	python SVM_classification.py

To run the regression predictor, run the command

	python regression.py

Tuneable parameters within the files: 

	rows
	cols
	bombs
	train_games (how many games of Minesweeper to use during training)
	area (for classification only. Controls how much of the board to use as features for the classifiers)

### Q-Learning method:
Enter the Q-Learning directory

	cd Qlearning/

Run the following command:

	python minesweeper_qlearning.py [-r <num rows>] [-c <num cols>] [-l <num training games>] [-p <num testing games>] [-q print state map]

Default values are 4x4 board, with 100,000 training games and 10,000 testing games.

### CSP method:
Enter the CSP directory
	
	cd CSP/

To run the nongraphical version, run the command (with optional flags)
	
	python pgms.py [-r <num rows>] [-c <num cols>] [-m <num mines>] [-n <num games>] [-i for intermediate game] [-e for expert game] [-b for beginner game] [-S <num sets>] [-v verbose] [-noreal can lose on first try]

To run the graphical version, run the command (also with optional flags)
	
	python gui.py [-r <num rows>] [-c <num cols>] [-m <num mines>] [-i for intermediate game] [-e for expert game] [-b for beginner game] [-S <num sets>] [-v verbose] [-noreal can lose on first try]

Once the GUI is up, clicking play will play a game and show the final result. Dark gray signifies tiles that had 0 mines. Lighter gray signifies other values for a square. Purple tiles signify a mine that was marked as a mine. Whenever a game is lost, all of the mines on the board are shown, these are the red tiles. Clicking on QUIT will quit the program.