import math
import numpy as np
import subprocess

def testRoutine(testDict):

    # print('Testing this function!')
    someMeasure = 0
    for paramName in testDict.keys():
        someMeasure += (testDict[paramName])**2 / np.random.normal(0,1)


    # subprocess.call('MathematicaScript -script testRoutine.m', shell= True)
    # someMeasure= 5 + np.random.uniform(0,1)
    return {'res1':someMeasure, 'res2':someMeasure**2}
