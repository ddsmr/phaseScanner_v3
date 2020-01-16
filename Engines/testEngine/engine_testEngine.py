from Utils.SmartRandomGenerator.smartRand import *
from time import gmtime, strftime

testdict ={'Woooo':'oooooo!'}
globalWaitFact = 0.5



class engineClass:
    '''
    '''


    # def __init__(self, modelName, caseHandle):
    def __init__(self):

        '''
        '''
        # configString = 'Configs.configFile_' + modelName
        # import importlib
        # configModule = importlib.import_module(configString)

        # self.condDict = configModule.condDict
        # self.rndDict = configModule.rndDict
        # self.toSetDict = configModule.toSetDict
        # self.targetDir = configModule.engineDir
        # self.runCMD = configModule.runCMD
        # self.calc = configModule.calcDict

        # self.condDict = phaseSpaceObj.condDict
        # self.rndDict = phaseSpaceObj.rndDict
        # self.toSetDict = phaseSpaceObj.toSetDict
        # # self.targetDir = phaseSpaceObj.engineDir
        # # self.runCMD = phaseSpaceObj.runCMD
        #
        # self.calc = phaseSpaceObj.calc

    # def _genValidPoint(self, paramsDictMinMax, threadNumber = "0", debug = False ):
    #
    #     smartRndGen = smartRand(paramsDictMinMax, self.condDict, self.rndDict, self.toSetDict)
    #     paramsDict = smartRndGen.genSmartRnd(debug= debug)
    #
    #     return paramsDict


    def _genPointAroundSeed(self, paramsDict, rSigma,  threadNumber='0', debug= False):
        '''
        '''
        smartRndGen = smartRand({}, self.condDict, self.rndDict, self.toSetDict)

        randParamDict = smartRndGen.genRandUniform_Rn( paramsDict , rSigma)


        waitTime = globalWaitFact/2 * random.uniform(0, 1)
        # print('Thread Nb ', threadNb+1, ' waiting time of :', waitTime)

        time.sleep( waitTime)
        # self.runPoint(randParamDict, threadNumber = threadNumber, debug = debug)

        return randParamDict


    def _getRequiredAttributes(self, paramsDict, threadNumber="0", runDict={}, pointKey=''):

        waitTime = globalWaitFact * random.uniform(0, 1)
        # print('Thread Nb ', threadNb+1, ' waiting time of :', waitTime)

        time.sleep( waitTime )

        # pointKey = 'Point T' + threadNumber + "-" + str(int(random.uniform(1,1000))) +  strftime("-%d%m%Y%H%M%S", gmtime())

        phaseSpaceDict = {}
        phaseSpaceDict[pointKey] = paramsDict

        mBottomMass = phaseSpaceDict[pointKey]['tanBeta'] * 0.98;
        # for param in paramsDict.items():
        #     mBottomMass = mBottomMass * param[1];

        phaseSpaceDict[pointKey].update( {'mBottom':mBottomMass} )

        ###########################  Calc initialisation ####################################
        calcParamDict = {}
        for calcParam in self.calc.keys():
            calcParamDict[calcParam] = None

        # phaseSpaceDict[pointKey].update({calcParamDict})
        return phaseSpaceDict

    def _check0Mass(self, phaseSpaceDict):
        return True

    def _clean(self, threadNumber="0"):
        return None

    def runPoint(self, mutatedDict, threadNumber = '0' , debug = False):
        waitTime = globalWaitFact * random.uniform(0, 1)
        # print('Thread Nb ', threadNb+1, ' waiting time of :', waitTime)

        time.sleep( waitTime /10)
        return {}
