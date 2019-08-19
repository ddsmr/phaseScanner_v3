import os
import json
import subprocess

import logging
# import subprocess

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wlexpr, wl
from wolframclient.serializers import export


class engineClass:
    '''
    '''

    def __init__(self):
        '''
        '''
        self.mathScriptPath = os.path.expanduser('~') + '/Documents/Hosotani_SO11/Mathematica/SO11_Masses_v7.m'
        self.session = WolframLanguageSession()
        self.timeOut = 120

        return None

    def _getRequiredAttributes(self, paramsDict, threadNumber="0", runDict={}, pointKey=''):
        '''
        '''
        phaseSpacePoint = {}
        phaseSpacePoint[pointKey] = runDict
        phaseSpacePoint[pointKey].update(paramsDict)

        return phaseSpacePoint

    def _clean(self, threadNumber):
        '''
        '''
        return None

    def _check0Mass(self, phaseSpaceDict):
        '''
        '''
        pointID = list(phaseSpaceDict.keys())[0]
        validPoint = True

        if (bool(phaseSpaceDict[pointID]) is True):
            if phaseSpaceDict[pointID]['Triviality'] is 0:
                validPoint = True
            else:
                validPoint = False
        else:
            validPoint = False

        return validPoint

    def runPoint(self, paramsDict, threadNumber='0', debug=False):
        '''
        '''
        # Set up logging utility
        logFileName = 'SO11_Analysis-' + threadNumber + '.log'
        logging.basicConfig(level=logging.INFO, filename=logFileName)

        # Export the data rules to the Mathematica association filetype
        paramsDict_wl = export(paramsDict, pandas_dataframe_head='association')
        dataRuleExpr = wlexpr(bytes('dataRule=', 'utf-8') + paramsDict_wl)

        resOut = {}
        try:

            #  Run the Mathematica Weinber Angle Code
            with open(self.mathScriptPath, 'r') as mathIn:
                strMath = mathIn.read()

            analysExpr = wlexpr(strMath)
            self.session.evaluate(dataRuleExpr)

            # print(paramsDict)
            timeConstrEval = wl.TimeConstrained(analysExpr, self.timeOut)
            resOut = self.session.evaluate(timeConstrEval)
            # resOut = self.session.evaluate(analysExpr)
            # resOut = wl.TimeConstrained(self.session.evaluate(analysExpr), 60)
            # print(resOut)
        except Exception as e:
            print(e)
            raise
            # print('-------')
            return {'Triviality': 1}

        # finally:
            # self.session.terminate()
            # print('Results for run: ', resOut)
        try:
            resStatus = resOut.name
        except Exception as e:
            resStatus = None

        if resStatus == '$Aborted' or bool(resOut) is False:
            return {'Triviality': 1}
        else:
            return resOut

    def _terminateSession(self):
        '''
            Terminates the current Wolfram session
        '''
        self.session.terminate()
        return None
