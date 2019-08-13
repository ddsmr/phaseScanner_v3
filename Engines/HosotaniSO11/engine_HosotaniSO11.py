import os
import json
import subprocess
from time import gmtime, strftime

from Utils.SmartRandomGenerator.smartRand import *
from Utils.printUtils import *




class engineClass:
    '''
    '''


    def __init__(self, phaseSpaceObj):
        '''
        '''

        # configString = 'Configs.configFile_' + modelName
        # import importlib
        # configModule = importlib.import_module(configString)

        self.condDict = phaseSpaceObj.condDict
        self.rndDict = phaseSpaceObj.rndDict
        self.toSetDict = phaseSpaceObj.toSetDict
        self.calc = phaseSpaceObj.calc

        self.targetDir = os.path.expanduser('~') + '/Documents/Hosotani_SO11/Mathematica'

        # import platform
        # sysInfo = platform.linux_distribution()
        # mathScript = 'MathematicaScript'
        # if '16.04' in sysInfo[1]:
        #     mathScript = 'MathematicaScript'
        # elif '18.04' in sysInfo[1]:
        mathScript = 'wolframscript'


        runCMD = mathScript + ' -script SO11_Masses_v6.m'  ### ThreadNb-n where n=1,2, ...
        self.runCMD = runCMD



    # def _generateRandomPointJSON(self, paramsDictMinMax, samplingPDF = 'Uniform' ,  threadNumber ="0", debug = False):
    #     '''
    #     '''
    #     targetDir = self.targetDir
    #     paramsDict = {}
    #
    #     # Use something like self._genSmartRnd(paramsDictMinMax)
    #
    #     smartRndGen = smartRand(paramsDictMinMax, self.condDict, self.rndDict, self.toSetDict)
    #     paramsDict = smartRndGen.genSmartRnd(debug= debug, samplingPDF = samplingPDF)
    #
    #     # for param in paramsDictMinMax.keys():
    #     #     paramsDict[param] = round ( random.uniform(paramsDictMinMax[param]['Min'], paramsDictMinMax[param]['Max'])  , 4)
    #
    #
    #     with open(targetDir + '/dataInThreadNb-' + threadNumber + '.json', 'w') as jsonParamFile:
    #         json.dump(paramsDict, jsonParamFile)
    #
    #     return paramsDict

    # def _runCustomCMD(self, threadNumber = "0", debug = False):
    #     '''
    #     '''
    #
    #     targetDir = self.targetDir
    #     FNULL = open(os.devnull, 'w')
    #
    #     runCMD = self.runCMD + ' ThreadNb-' + threadNumber
    #
    #     if debug == False:
    #         subprocess.call(runCMD , shell = True, cwd = targetDir, stdout = FNULL, stderr=subprocess.STDOUT)
    #     else:
    #         subprocess.call(runCMD , shell = True, cwd = targetDir)
    #
    #     return None

    # def _genValidPoint(self, paramsDictMinMax, threadNumber = "0", debug = False , samplingPDF = 'Uniform'):
    #     '''
    #         CUSTOM USER FUNCTION.
    #     '''
    #     targetDir = self.targetDir
    #
    #     paramsDict = self._generateRandomPointJSON(paramsDictMinMax, threadNumber = threadNumber, samplingPDF = samplingPDF, debug = debug)
    #
    #     self._runCustomCMD(threadNumber)
    #
    #     return paramsDict
    #
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

        if phaseSpaceDict_NOID and phaseSpaceDict_NOID['Triviality'] == 0:



            pointKey = 'Point T' + threadNumber + "-" + str(int(random.uniform(1,1000))) +  strftime("-%d%m%Y%H%M%S", gmtime())

            phaseSpaceDict = {}
            phaseSpaceDict[pointKey] =  paramsDict
            phaseSpaceDict[pointKey].update( phaseSpaceDict_NOID )

            ###########################  Calc initialisation ####################################
            calcParamDict = {}
            for calcParam in self.calc.keys():
                calcParamDict[calcParam] = None

            # phaseSpaceDict[pointKey].update({calcParamDict})
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


        runCMD = self.runCMD + ' ThreadNb-' + threadNumber
        if debug == False:
            subprocess.call(runCMD , shell = True, cwd = targetDir, stdout = FNULL, stderr=subprocess.STDOUT)
        else:
            subprocess.call(runCMD , shell = True, cwd = targetDir)


        time.sleep(0.1)

        return None

    # def _genPointAroundSeed(self, paramsDict, rSigma,  threadNumber='0', debug= False):
    #     '''
    #     '''
    #     smartRndGen = smartRand({}, self.condDict, self.rndDict, self.toSetDict)
    #
    #     randParamDict = smartRndGen.genRandUniform_Rn( paramsDict , rSigma)
    #     self.runPoint(randParamDict, threadNumber = threadNumber, debug = debug)
    #
    #     return randParamDict
