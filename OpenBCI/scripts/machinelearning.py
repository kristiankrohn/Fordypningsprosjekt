from sklearn import datasets, neighbors
import numpy as np
import matplotlib.pyplot as plt
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.cluster import KMeans
from sklearn.externals import joblib #in order to store the svm

DataSet = []
predictSet = []
DataSetLabels = [] #r1 = 0, u1 = 1, l1 = 2, d1 = 3, c1 = 4
convertedDataSet = [[]]
convertedPredictData = [[]]



def main():
    AllData, predictData = readFile()
    arrangeDataset(AllData, predictData)
    clf = createAndTrain()
    saveMachinestate(clf) #if you want to save the state of classifier
    predict(clf)


def readFile():

    file = open('data.txt', 'r')
    pFile = open('temp.txt', 'r')
    AllData = file.read()
    predictData = pFile.read()
    return AllData, predictData

def appendLabel(featuretype):
    global DataSetLabels

    if featuretype == 'r1':
        DataSetLabels.append(0)
    if featuretype == 'u1':
        DataSetLabels.append(1)
    if featuretype == 'l1':
        DataSetLabels.append(2)
    if featuretype == 'd1':
        DataSetLabels.append(3)
    if featuretype == 'c1':
        DataSetLabels.append(4)


def arrangeDataset(AllData, predictData):
    global Dataset, predictSet, convertedDataSet, convertedPredictData

    DataSet = AllData.split(':')
    predictSet = predictData.split(':')

    for i in range(len(DataSet)):
        feature = []
        feature = DataSet[i].split(',')

        featuretype = feature[0]
        feature.pop(0)
        convertedDataSet.append(map(float, feature))
        appendLabel(featuretype)

        #pops the two empty lists at index 0 and end-index
        if i == (len(DataSet) - 1):
            convertedDataSet.pop(0)
            convertedDataSet.pop(len(DataSet) -1)
            #print(convertedDataSet)
    for i in range(len(predictSet)):
            predictionFeature = [] #this is just for trying to predict a given dataset
            predictionFeature = predictSet[i].split(',')
            predictionFeature.pop(0)

            convertedPredictData.append(map(float, predictionFeature))

            #pops the two empty lists at index 0 and end-index
            if i == (len(predictSet) - 1):
                convertedPredictData.pop(0)
                convertedPredictData.pop(len(predictSet) - 1)


def createAndTrain():
    global convertedDataSet, convertedPredictData, DataSetLabels

    X = np.array(convertedDataSet)
    Y = np.array(map(float, DataSetLabels))
    print(Y)

    clf = LinearSVC()
    clf.fit(X,Y)
    return clf


def loadAndTrain():
    global convertedDataSet, DataSetLabels

    X = np.array(convertedDataSet)
    Y = np.array(map(float, DataSetLabels))


    clf = joblib.load('machinestate.pkl')#loads the machine-learning state
    clf.fit(X,Y)
    return clf

def saveMachinestate(clf):
    joblib.dump(clf, 'machinestate.pkl')


def predict(clf):
    global convertedPredictData

    Z = np.array(convertedPredictData)
    print(clf.predict(Z))







#print(convertedPredictData)
#X = np.array(convertedDataSet)

#Y = np.array(map(float, DataSetLabels))

#Z = np.array(convertedPredictData)


#clf = LinearSVC()



#joblib.dump(clf, 'machineStateDataSet.pkl')#saves the machine-learning state



if __name__ == '__main__':
	main()
