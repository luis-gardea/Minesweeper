import minesweeper_generate_data
import numpy as np 
from sklearn import svm
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib

#X = np.load('train_data.npy')
#Y = np.load('train_labels.npy')

X_train, Y_train = minesweeper_generate_data.generate_data(100)
svm = OneVsRestClassifier(svm.SVC())
svm.fit(X_train, Y_train)
print svm.score(X_train, Y_train)

X_test, Y_test = minesweeper_generate_data.generate_data(100)
print svm.score(X_test, Y_test)

print Y_test[1:10, :]
print svm.predict(X_test[1:10, :])

#joblib.dump(logreg, 'logreg/logreg.pkl') 
#joblib.dump(svm, 'svm/svm.pkl')