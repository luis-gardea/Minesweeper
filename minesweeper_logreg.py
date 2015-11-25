import minesweeper_generate_data
import numpy as np 
from sklearn import linear_model
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib

#X = np.load('train_data.npy')
#Y = np.load('train_labels.npy')

X_train, Y_train = minesweeper_generate_data.generate_data(50)
logreg = OneVsRestClassifier(linear_model.LogisticRegression())
logreg.fit(X_train, Y_train)
print logreg.score(X_train, Y_train)

X_test, Y_test = minesweeper_generate_data.generate_data(50)
print logreg.score(X_test, Y_test)


#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')