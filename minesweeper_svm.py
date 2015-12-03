import minesweeper
import numpy as np 
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib

#X = np.load('train_data.npy')
#Y = np.load('train_labels.npy')

X_train, Y_train = minesweeper.generate_data(500)
svm = OneVsRestClassifier(svm.SVC())
svm.fit(X_train, Y_train)
print 'Train accuracy:', svm.score(X_train, Y_train)

X_test, Y_test = minesweeper.generate_data(15)
print svm.score(X_test, Y_test)

print Y_test
print 'Test accuracy:', svm.predict(X_test)

#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')