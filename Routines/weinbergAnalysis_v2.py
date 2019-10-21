import logging
import os
import subprocess
import json

from printUtils import *


def getWeinbergAngle(dataDict, threadNumber='0', debug=False):
    '''
            Starts a Wolfram WolframLanguage Session and runs the code in /Documents/Wolfram Mathematica/pyMathTest.m
        with the parameters defined in dataDict.

        Arguments:
            - dataDict  :   Type(Dict) containing all the parameters necesary for the Weinberg analysis.

        Returns:
            - weinbergAngle :   Type(Float) value of the resulting angle

    '''
    targetDir = os.path.expanduser('~') + '/Documents/Wolfram Mathematica/'
    # runCMD2 = 'ls ' + targetDir
    # subprocess.call(runCMD2, shell=True, cwd=targetDir, stdout=FNULL, stderr=subprocess.STDOUT)
    with open(targetDir + 'dataInThreadNb-' + threadNumber + '.json', 'w') as jsonParamFile:
        json.dump(dataDict, jsonParamFile)

    runCMD = 'wolframscript -script weinbergAnalysis.m ' + ' ThreadNb-' + threadNumber  # + ' ThreadNb-' + threadNumber
    if debug is False:
        subprocess.call(runCMD, shell=True, cwd=targetDir, stdout=FNULL, stderr=subprocess.STDOUT)
    else:
        subprocess.call(runCMD, shell=True, cwd=targetDir)

    try:
        with open(targetDir + '/weinbergAngleOutThreadNb-' + threadNumber + '.json', 'r') as jSonInFile:
            weinbergDict = json.load(jSonInFile)
        sinWeinbergAngle = weinbergDict['sin2ThW']
    except Exception as e:
        sinWeinbergAngle = None

    if debug:
        print(delimitator, sinWeinbergAngle, delimitator)

    return sinWeinbergAngle
