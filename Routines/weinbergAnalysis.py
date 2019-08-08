import logging
import os
import subprocess


from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr
from wolframclient.serializers import export



def getWeinbergAngle( dataDict , threadNumber = '0'):
    '''
    '''

    weinbergAnalysisPath = os.path.expanduser('~') + '/Documents/Wolfram Mathematica/pyMathTest.m'


    ### Export the data rules to the Mathematica association filetype
    dataDict_wl = export(dataDict, pandas_dataframe_head='association')
    dataRuleExpr = wlexpr(bytes('dataRule=', 'utf-8') + dataDict_wl)


    # set the root level to INFO
    logFileName = 'exampleThrNb-' + threadNumber + '.log'
    logging.basicConfig(level=logging.INFO, filename=logFileName)

    session = WolframLanguageSession()

    try:

        ### Run the Mathematica Weinber Angle Code
        with open(weinbergAnalysisPath, 'r') as mathIn:
            strMath = mathIn.read()


        weinbergExpr = wlexpr( strMath )
        session.evaluate(dataRuleExpr)
        weinbergAngle = session.evaluate( weinbergExpr)
    finally:
        session.terminate()
        # print('Weinberg Angle value: ', weinbergAngle)
        # subprocess.call('rm ' +)


    return weinbergAngle
