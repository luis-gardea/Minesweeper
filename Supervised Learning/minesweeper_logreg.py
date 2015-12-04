import minesweeper
import numpy as np 
from sklearn import linear_model
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib

X_train, Y_train = minesweeper.generate_data(500)
logreg = OneVsRestClassifier(linear_model.LogisticRegression())
logreg.fit(X_train, Y_train)
print 'Train accuracy:', logreg.score(X_train, Y_train)

X_test, Y_test = minesweeper.generate_data(100)
print 'Test accuracy:', logreg.score(X_test, Y_test)