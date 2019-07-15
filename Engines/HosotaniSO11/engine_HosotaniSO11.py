from Utils.SmartRandomGenerator.smartRand import *
import json
import subprocess
from time import gmtime, strftime

testdict ={'Woooo':'oooooo!'}

import os

nbrTerminalRows, nbrTerminalCols = os.popen('stty size', 'r').read().split()
nbrTerminalRows = int(nbrTerminalRows)
nbrTerminalCols = int(nbrTerminalCols)
delimitator = '\n' + '▓' * nbrTerminalCols + '\n'
delimitator2 = '\n' + '-' * nbrTerminalCols + '\n'

FNULL = open(os.devnull, 'w')


class engineClass:
    '''
    '''


    def __init__(self, modelName, caseHandle):
        '''
        '''

        configString = 'Configs.configFile_' + modelName
        import importlib
        configModule = importlib.import_module(configString)

        self.condDict = configModule.condDict
        self.rndDict = configModule.rndDict
        self.toSetDict = configModule.toSetDict
        self.targetDir = configModule.engineDir
        self.runCMD = configModule.runCMD
        self.calc = configModule.calcDict



    def _generateRandomPointJSON(self, paramsDictMinMax, samplingPDF = 'Uniform' ,  threadNumber ="0", debug = False):
        '''
        '''
        targetDir = self.targetDir
        paramsDict = {}

        # Use something like self._genSmartRnd(paramsDictMinMax)

        smartRndGen = smartRand(paramsDictMinMax, self.condDict, self.rndDict, self.toSetDict)
        paramsDict = smartRndGen.genSmartRnd(debug= debug, samplingPDF = samplingPDF)

        # for param in paramsDictMinMax.keys():
        #     paramsDict[param] = round ( random.uniform(paramsDictMinMax[param]['Min'], paramsDictMinMax[param]['Max'])  , 4)


        with open(targetDir + '/dataInThreadNb-' + threadNumber + '.json', 'w') as jsonParamFile:
            json.dump(paramsDict, jsonParamFile)

        return paramsDict

    def _runCustomCMD(self, threadNumber = "0"):
        '''
        '''

        targetDir = self.targetDir
        FNULL = open(os.devnull, 'w')

        runCMD = self.runCMD + ' ThreadNb-' + threadNumber
        subprocess.call(runCMD , shell = True, cwd = targetDir, stdout = FNULL, stderr=subprocess.STDOUT)

        return None

    def _genValidPoint(self, paramsDictMinMax, threadNumber = "0", debug = False , samplingPDF = 'Uniform'):
        '''
            CUSTOM USER FUNCTION.
        '''
        targetDir = self.targetDir

        paramsDict = self._generateRandomPointJSON(paramsDictMinMax, threadNumber = threadNumber, samplingPDF = samplingPDF, debug = debug)

        self._runCustomCMD(threadNumber)

        return paramsDict

    def _getRequiredAttributes(self, paramsDict, threadNumber="0"):
        '''
        '''

        targetDir = self.targetDir

        for param in paramsDict.keys():
            # print(param, paramsDict)

            if param != 'c2' and paramsDict[param] < 0:
                # print('+++++++++++++++++++++++++++++++')
                return {}


        try:
            with open(targetDir + '/massesOutThreadNb-' + threadNumber + '.json', 'r') as jSonInFile:
                phaseSpaceDict_NOID = json.load(jSonInFile)
        except Exception as e:
            phaseSpaceDict_NOID = {}
            # print(Fore.RED + '\n Thread Nb-' + str(threadNumber) + ' Failure')
            # print(Fore.YELLOW + str(e))

        if phaseSpaceDict_NOID and phaseSpaceDict_NOID['Triviality']==0 :



            pointKey = 'Point T' + threadNumber + "-" + str(int(random.uniform(1,1000))) +  strftime("-%d%m%Y%H%M%S", gmtime())

            phaseSpaceDict = {}
            phaseSpaceDict[pointKey]= {'Params': paramsDict}
            phaseSpaceDict[pointKey].update( {'Particles': phaseSpaceDict_NOID} )

            ###########################  Calc initialisation ####################################
            calcParamDict = {}
            for calcParam in self.calc.keys():
                calcParamDict[calcParam] = None

            phaseSpaceDict[pointKey].update({'Calc' : calcParamDict})
            #####################################################################################
        # print (phaseSpaceDict)
            return phaseSpaceDict
        else:
            return {}

    def _clean(self, threadNumber):
        '''
        '''
        targetDir = self.targetDir

        FNULL = open(os.devnull, 'w')
        cleanList =[ 'dataInThreadNb-' + str(threadNumber) + '.json' , 'massesOutThreadNb-' + str(threadNumber) + '.json']

        for fileToClean in cleanList:
            subprocess.call('rm -f ' + fileToClean , shell = True, cwd = targetDir)#, stdout=FNULL, stderr=subprocess.STDOUT)

        return None

    def _check0Mass(self, phaseSpaceDict):
        '''
        '''
        if phaseSpaceDict:
            no_0Mass = True
        else:
            return False

        for pointKey in phaseSpaceDict.keys():
            # print (Fore.RED + delimitator2 )
            # print (Fore.BLUE +'Higgs == '+ str(phaseSpaceDict[pointKey]['Particles']['Higgs']) )
            # print (Fore.BLUE +'ΘH == '+ str(phaseSpaceDict[pointKey]['Particles']['ThetaHiggs']) )
            # print (Fore.YELLOW +'W⁺⁻ == '+ str(phaseSpaceDict[pointKey]['Particles']['mWpm'] ) )
            # print (Fore.GREEN + 'mTop == ' +str( phaseSpaceDict[pointKey]['Particles']['mTop']) )
            # print (Fore.RED + delimitator2 )


            if  ( False

                ):

                no_0Mass = False
                # print (no_0Mass, Style.RESET_ALL)

        return no_0Mass

    def runPoint(self, paramsDict, threadNumber='0', debug= False):
        '''
        '''

        targetDir = self.targetDir

        with open(targetDir + '/dataInThreadNb-' + threadNumber + '.json', 'w') as jsonParamFile:
            json.dump(paramsDict, jsonParamFile)

        self._runCustomCMD(threadNumber)
        time.sleep(0.1)

        return None

    def _genPointAroundSeed(self, paramsDict, rSigma,  threadNumber='0', debug= False):
        '''
        '''
        smartRndGen = smartRand({}, self.condDict, self.rndDict, self.toSetDict)

        randParamDict = smartRndGen.genRandUniform_Rn( paramsDict , rSigma)
        self.runPoint(randParamDict, threadNumber = threadNumber, debug = debug)

        return randParamDict
