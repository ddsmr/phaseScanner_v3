import os
import json
import subprocess

import logging
# import subprocess

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wlexpr  # wl,
from wolframclient.serializers import export


class engineClass:
    '''
    '''

    def __init__(self, phaseSpaceObj):
        '''
        '''
        self.mathScriptPath = os.path.expanduser('~') + '/Documents/Hosotani_SO11/Mathematica/SO11_Masses_v7.m'
        self.session = WolframLanguageSession()

        return None

    def _getRequiredAttributes(self, paramsDict, threadNumber="0", runDict={}, pointKey=''):
        '''
        '''

    def _clean(self, threadNumber):
        '''
        '''

    def _check0Mass(self, phaseSpaceDict):
        '''
        '''
        return True

    def runPoint(self, paramsDict, threadNumber='0', debug=False):
        '''
        '''
        # Set up logging utility
        logFileName = 'SO11_Analysis-' + threadNumber + '.log'
        logging.basicConfig(level=logging.INFO, filename=logFileName)

        # Export the data rules to the Mathematica association filetype
        paramsDict_wl = export(paramsDict, pandas_dataframe_head='association')
        dataRuleExpr = wlexpr(bytes('dataRule=', 'utf-8') + paramsDict_wl)

        try:

            #  Run the Mathematica Weinber Angle Code
            with open(self.mathScriptPath, 'r') as mathIn:
                strMath = mathIn.read()

            analysExpr = wlexpr(strMath)
            self.session.evaluate(dataRuleExpr)

            resOut = self.session.evaluate(analysExpr)
        finally:
            # self.session.terminate()
            print('Results for run: ', resOut)

        return resOut
