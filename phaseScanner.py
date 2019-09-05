import os
import subprocess
import json
import re
import importlib
import pickle
import csv
from multiprocessing import Process, Queue, Pipe
from time import gmtime, strftime
from datetime import date, datetime


from halo import Halo
from tqdm import tqdm
from shapely.geometry.polygon import Polygon
# from shapely.geometry import Point


from Utils.printUtils import *
from Utils.SmartRandomGenerator.smartRand import *
from Utils.metaLogging import *
from Utils.constrEval import *
from Utils.multiThreadAlg import *
# from Utils.dictplotting import *


def getLatestFocusDir(psObject):
    '''
        Given a psObject the function will get the latest focus directory from the Results directory.
    '''
    try:
        # focusDate = ''
        dirEntries = os.listdir(psObject.resultDir + 'Dicts/')

        listOfDirs = []
        for dirEntry in dirEntries:
            if 'Focus' in dirEntry and ('.' not in dirEntry):
                listOfDirs.append(dirEntry.replace('Focus_', ''))

        focusDate_DateTime = checkListForLatestDate(listOfDirs)
        focusDateTime_str = convertDateTimeToStr(focusDate_DateTime)

    except Exception as e:
        print(e)
        raise
    # print(focusDate)
    # exit()

    focusDir = 'Dicts/Focus-' + focusDateTime_str + '/'
    return focusDir


def genRndDict(paramDict):
    '''
        Given a parameter Dictionary , the function will generate the default
        random picker with Succes as the 1st stage, e.g. :

        rndDict = OrderedDict ([('Check-0', {'ToPick': ['Lambda', 'Kappa',
                                                        'tanBeta'],
                                           'ToCheck': [],
                                           'ToSet' : [],
                                           'Pass' : 'Success',
                                           'Fail' : 'Check-0'}
                                  )
                                ])
    '''
    from collections import OrderedDict

    rndDict = OrderedDict([('Check-0', {'ToPick': list(paramDict.keys()),
                                        'ToCheck': [],
                                        'ToSet': [],
                                        'Pass': 'Success',
                                        'Fail': 'Check-0'})])
    return rndDict


def chunkList(listToChunk, noOfLits, threadNBSort=False):
    '''
        Chunks a list into n  = noOfLits smaller lists. Used in the genetic algorithm.

        Arguments:
            - listToChunk       ::   List user wants to split (chunk) into noOfLits lists.
            - noOfLits          ::   Number of lists to be split into

        Returns:
            - listOfLists = [ [...], [...], ...   ]
    '''
    index = 0
    listOfLists = []

    for i in range(noOfLits):
        listOfLists.append([])

    # pp(listOfLists)
    if threadNBSort is True:
        for i in range(len(listToChunk)):
            # print(i // (len(listToChunk) // noOfLits))
            listOfLists[i // (len(listToChunk) // noOfLits)].append(listToChunk[i])
        return listOfLists
        # exit()

    lenLtC = len(listToChunk)
    for index in range(len(listToChunk)):

        listOfLists[index % noOfLits].append(listToChunk[index])

    for memberListIdx in range(len(listOfLists)):
        if (len(listOfLists[memberListIdx]) == 0):
            listOfLists[memberListIdx] = listOfLists[int(random.uniform(0, memberListIdx))]

    return listOfLists


def fixJsonWAppend(jsonDir, specFile=''):
    '''
            Give a FOCUS Directory jSonDir, the function will use regEx to fix the append issue for the json files
        produced in the Generational algorithm.
    '''
    p = re.compile(r'}{')
    toReplace = r','

    # 'SO11Hosotani_DummyCase/Dicts/Focus_15_04_2019/'
    # jsonDir = 'Results/SO11Hosotani_DummyCase/Dicts/Focus_06_05_2019/'

    for jsonDict in os.listdir(jsonDir):

        if ('.json' in jsonDict) and ('Focus' not in jsonDict) and (specFile in jsonDict):
            try:
                with open(jsonDir + jsonDict, 'r') as inFile:
                    jsonContent = inFile.readline()
                    correctedJSON = p.sub(toReplace, jsonContent)

                    nbJson = jsonDict.split('ThreadNb')[1]
                    currTime = strftime("-%d-%m-%Y_%H:%M:%S", gmtime())

                    fileName = 'Fixed_' + jsonDict
                    # fileName = 'Focus_Fixed' + currTime + '_FixedJson-ThreadNb' + nbJson
                    newJson = open(jsonDir + fileName, 'w')
                    newJson.write(correctedJSON)
                    newJson.close()

                    # Remove the old file if the new Json is fixed
                try:
                    with open(jsonDir + fileName, 'r') as inFile:
                        fixedDict = json.load(inFile)

                    subprocess.call('rm ' + jsonDict, shell=True, cwd=jsonDir)
                    print()
                    printCentered(' Fixed ' + jsonDict + ' ', fillerChar='=')
                except Exception as e:
                    print('Failed to Fix Json ', jsonDict)
                    print(e)

            except Exception as e:
                print('Failed to open ', jsonDict, ' with Exception ', e)

    return None


def writeGenStat(resultsDirDicts, threadNumber, listOfStats, listOfStatsNames):
    with open(resultsDirDicts + 'GenStatus_ThreadNb' + threadNumber + '.dat', 'a') as outFile:

        outFile.write(''.join(attrName + str(attr) + '   ||  '
                              for attrName, attr in zip(listOfStatsNames, listOfStats)) + '\n')
    return None


def checkListForLatestDate(dateList):
    '''
        Given a list of dates function will check all FOLDERS and return the string corresponding to the latest date.
    '''
    listOfDates = []

    for strDate in dateList:
        # print(strDate)
        splitDateStr_aux = strDate.split('_')
        splitDateStr = splitDateStr_aux[0].split('-')
        # print(splitDateStr)

        newDate = datetime(int(splitDateStr[3]), int(splitDateStr[1]), int(splitDateStr[2]),
                           hour=int(splitDateStr_aux[1]), minute=int(splitDateStr_aux[2]),
                           second=int(splitDateStr_aux[3]))

        listOfDates.append(newDate)
    # pp(listOfDates)

    return max(listOfDates)


def convertDateTimeToStr(dateTime):
    '''
        Given a datetime object it will output a string of the form MM-DD-YYYY_HH_MM_SS .
    '''
    monthStr = '0' + str(dateTime.month)
    dayStr = '0' + str(dateTime.day)
    hourStr = '0' + str(dateTime.hour)
    minStr = '0' + str(dateTime.minute)
    secStr = '0' + str(dateTime.second)

    dateStr = monthStr[-2:] + '-' + dayStr[-2:] + '-' + str(dateTime.year) + '_'
    timeStr = hourStr[-2:] + '_' + minStr[-2:] + '_' + secStr[-2:]

    # dateStr = monthStr[-2:] + '-' + dayStr[-2:] + '-' + str(dateTime.year) + '_' + hourStr[-2:] + '_' + \
    # minStr[-2:] + '_' + secStr[-2:]

    return dateStr + timeStr


class phaseScannerModel:
    '''
            Class that initialises a phaseScannerModel model and then is used to to the various things specified
        in the documentation.

        Pre-requirements:
            - Generating engine for the points with it's required functionalities.

    '''

    def __init__(self, modelName, caseHandle, micrOmegasName='', userDescription="", writeToLogFile=False):
        '''
            Init stage for the modelFS class.

            Attributes:
                - modelName             ::      Name of the specified model that we want to work with.
                - caseHandle            ::      Casehandle that specifies which case the model will be dealing with.
                                                !!! NOTE : if there's just one case pass dummy case handle e.g.
                                                'DummyCase'.

                - generatingEngine      ::      Engine that will generate the required attributes. Should be the same
                                                name as the .py file in Engines/

                - userDescription       ::      Description user passes to further help with identification.
                - writeToLogFile        ::      Set to True to write to log file.
        '''
        print('\n')
        printCentered(' ⦿ Started Initialising Model  ', fillerChar='░', color=Fore.BLUE)
        configString = 'Configs.configFile_' + modelName

        try:
            configModule = importlib.import_module(configString)
        except Exception as e:
            print(e)
            raise

        self.genEngine = configModule.genEngine
        self.engineVersion = configModule.engVers
        engineString = 'Engines.' + self.genEngine + ".engine_" + self.genEngine

        try:
            engineModule = importlib.import_module(engineString)
        except Exception as e:
            print(e)
            raise

        # ############## Engine class ###################
        self.engineClass = engineModule.engineClass
        # self.engine
        # ############## Model Bits ###################
        self.modelName = modelName
        self.case = caseHandle
        self.name = modelName + caseHandle
        if micrOmegasName != '':
            self.micrOmegasName = modelName

        # ############## Data bits ####################
        # self.targetDir = configModule.engineDir
        # self.runCMD = configModule.runCMD
        self.description = userDescription

        # ############# Smart Random Bits ############
        try:
            self.rndDict = configModule.rndDict
            self.condDict = configModule.condDict
            self.toSetDict = configModule.toSetDict

        except Exception as e:
            self.condDict = {}
            self.toSetDict = {}
            self.rndDict = genRndDict(configModule.paramDict)
            print(Fore.YELLOW, delimitator2, e, '\nWARNING: Created default random parameter selection.',
                  Style.RESET_ALL)

        # ###### Result and Log directories #########
        if ('Utils' in os.getcwd()):
            self.resultDir = '../Results/' + modelName + '_' + caseHandle.replace(" ", '') + '/'
            self.logDir = '../Logs/' + modelName + '_' + caseHandle.replace(" ", '') + '/'
        else:
            self.resultDir = 'Results/' + modelName + '_' + caseHandle.replace(" ", '') + '/'
            self.logDir = 'Logs/' + modelName + '_' + caseHandle.replace(" ", '') + '/'

        for dirToMake in [self.resultDir, self.logDir]:
            subprocess.call('mkdir ' + dirToMake, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

        # ###### Params, Particles , Rules, Calcs ###########
        self.params = configModule.paramDict
        self.rules = configModule.replacementRules[caseHandle]

        self.modelAttrs = configModule.attrDict
        self.calc = configModule.calcDict

        # ### Param Ranges and sigmas ##############
        self.paramBounds = configModule.dictMinMax

        #   Set a the default plotting specified in the config. If none is available, generate one from the keys,
        # similarly for the default plotting atributes.
        try:
            self.defaultPlot = configModule.defaultPlot
        except Exception as e:

            self.defaultPlot = {'xAxis': random.choice(list(self.params.keys())),
                                'yAxis': random.choice(list(self.params.keys())),
                                'colorAxis': random.choice(list(self.modelAttrs.keys()))}
            print(Fore.YELLOW + delimitator2 + str(e) + '\nWARNING: Setting default plot.' + Style.RESET_ALL)

        try:
            self.plotFormatting = configModule.plotFormatting
        except Exception as e:
            print(Fore.YELLOW + delimitator2 + str(e) + '\nWARNING: Setting default plotting attrs.' + Style.RESET_ALL)
            self.plotFormatting = {
                 'failPlot': {'alpha': 0.5, 'lw': 0, 's': 100},
                 'passPlot': {'alpha': 1,   'lw': 0.6, 's': 240},
                 'fontSize': 40
                  # 'failPlot' : {'alpha':0.1, 'lw' :0, 's':30},
                  # 'passPlot' : {'alpha':1,   'lw' : 0.17, 's':140}
                  # 'fontSize' : 30
            }

        # #### Classification & All dicts #################
        classDict = {}
        self.classList = ['Param', 'Attr', 'Calc']
        for params, paramType in zip([self.params.keys(), self.modelAttrs.keys(), self.calc.keys()], self.classList):
            for param in params:
                classDict[param] = paramType
        self.classDict = classDict

        self.allDicts = {}
        for dict in [self.params, self.modelAttrs,  self.calc]:
            if dict:
                self.allDicts.update(dict)

        # #### Constraint list #################################
        self.noneAttr = []
        try:
            self.noneAttr = configModule.noneAttr
        except Exception as e:
            self.noneAttr = []
        finally:
            # self.noneAttr.append('ChiSquared')
            for attr in self.calc.keys():
                try:
                    if (self.calc[attr]['Calc']['Type'] == 'ChiSquared'
                            or self.calc[attr]['Calc']['Type'] == 'ExternalCalc'):

                        self.noneAttr.append(attr)
                except Exception as e:
                    print(e)
                    pass

        constrDict = {}
        constrList = []

        cutList = []
        cutDict = {}

        polygCuts = []

        for attr in self.allDicts.keys():
            # for attr in self.allDicts[attrType].keys():
            if self.allDicts[attr]['Constraint']['Type'] == 'ParamMatch':
                constrList.append('ParamMatch-' + attr)
                constrDict[attr] = 'ParamMatch-' + attr

            elif self.allDicts[attr]['Constraint']['Type'] == 'CheckBounded':
                constrList.append('CheckBounded-' + attr)
                constrDict[attr] = 'CheckBounded-' + attr

            elif self.allDicts[attr]['Constraint']['Type'] in ['HardCutLess', 'HardCutMore']:
                cutList.append(attr)
                cutDict[attr] = self.allDicts[attr]['Constraint']['Type']

            elif self.allDicts[attr]['Constraint']['Type'] == 'CombinedCut':
                cutList.append(attr)
                cutList.append(self.allDicts[attr]['Constraint']['ToCheck']['ToCheck'])
                cutDict[attr] = self.allDicts[attr]['Constraint']['ToCheck']['ToCheck']

            elif self.allDicts[attr]['Constraint']['Type'] == 'PolygonCut':
                cutList.append(attr)
                polygCuts.append(attr)
                cutDict[attr] = self.allDicts[attr]['Constraint']['Type']

            elif self.allDicts[attr]['Constraint']['Type'] == 'Constrained':
                cutDict[attr] = self.allDicts[attr]['Constraint']['ToCheck']

        self.constrList = constrList
        self.constrDict = constrDict

        self.cutList = cutList
        self.cutDict = cutDict

        # ############## Set up exclusion polygon if available ##############

        cutDict_Poly = {}
        try:
            for attrToCut in polygCuts:
                plotDataName = 'Configs/ExperimentalCuts/plotCut_' + attrToCut + '.csv'

                polygonList = []
                with open(plotDataName, 'r') as fileIn:
                    csvReader = csv.reader(fileIn)

                    for rawRow in csvReader:
                        xCoord, yCoord = float(rawRow[0]), float(rawRow[1])
                        polygonList.append((xCoord, yCoord))

                cutDict_Poly.update({attrToCut: Polygon(polygonList)})
        except Exception as e:
            print(e)
            pass
        #######################################################################################
        self.polygCuts = cutDict_Poly

        self.session = 'Session' + strftime("-%d-%m-%Y_%H_%M_%S", gmtime()) + '-RID' + str(int(random.uniform(1, 1000)))
        if (writeToLogFile is True):
            writeToLogFile_InitModel(self)

        # ######## SubClasses ###########
        self.generatingEngine = self.engineClass()
        self.modelConstr = constrEval(self)

        self.calcRoutines = {}
        for calcParam in self.calc.keys():
            if self.calc[calcParam]['Calc']['Type'] == 'ExternalCalc':
                routineStr = 'Routines.' + self.calc[calcParam]['Calc']['Routine']
                routineModule = importlib.import_module(routineStr)

                self.calcRoutines[calcParam] = routineModule

        print('\n')
        printCentered('  ✔ Done Initialising Model  ', fillerChar='░', color=Fore.GREEN)

    def loadResults(self, nbOfPoints='All', targetDir='Dicts/', specFile='', ignoreIntegrCheck=False):
        '''
            Loads all the json result dictionaries as a full dictionary.

            Attributes:
            -   nbOfPoints  ::  OPTIONAL, Type=Int. Specify number to number of points to be returned from the loading
                session.
            -   targetDir   ::  OPTIONAL, Type=Str. Specify directory w.r.t. the result dir of the model.
            -   specFile    ::  OPTIONAL, Type=Str. Specify specific file within the directory in question.
            -   ignoreIntegrCheck   ::  OPTIONAL, Type=Bool. Set to True to ignore the integrity check performed on the
                phase space dictionary.

            Returns:
            -   dict  ::  phaseSpaceDict dictionary.
        '''
        # ## Load all Jsons in Dicts/ dir.
        phaseSpaceDict = {}
        printCentered(' Looking in dir ' + targetDir + ' ', fillerChar='▀')

        try:
            dirFiles = os.listdir(self.resultDir + targetDir)
        except Exception as e:
            print(Fore.RED + str(e))
            return {}

        for jsonDict in dirFiles:
            if ('.json' in jsonDict):

                if ((specFile != '') and (specFile in jsonDict)) or (specFile == ''):
                    try:

                        with open(self.resultDir + targetDir + jsonDict) as inFile:
                            tempDict = json.load(inFile)
                        printCentered(' Opening ' + jsonDict + ' ', fillerChar='-')
                        phaseSpaceDict = {**phaseSpaceDict, **tempDict}
                    except Exception as e:
                        print(e)
                        printCentered('❎ Cannot open ' + jsonDict, color=Fore.RED, fillerChar='-')

        print()
        # ######### COMEBACK #######
        # ## Integrity check , excludes all points that have None as an attribute
        pointsToRemove = []

        if ignoreIntegrCheck is False:
            for point in phaseSpaceDict.keys():
                for attribute in self.allDicts.keys():

                    # print(self.)
                    # for attribute in self.allDicts[attributeType].keys():

                    # ### Check if the point in question hass all the attributes specified by the model
                    if attribute not in phaseSpaceDict[point].keys():
                        # print(attribute, ' not present in', point)
                        pointsToRemove.append(point)

                    # ### If it has all the attributes then check if they are non empty
                    elif (phaseSpaceDict[point][attribute] is None) and (attribute not in self.noneAttr):
                        # attribute!='ChiSquared'
                        # print(attribute)
                        pointsToRemove.append(point)

        # exit()
        # Remove the points , using set to ensure they're no duplicates.
        for point in set(pointsToRemove):
            # print(point)
            del phaseSpaceDict[point]

        # print( len(phaseSpaceDict) )
        # ### Return all or a number of points chosen at random.
        if nbOfPoints == 'All':
            return phaseSpaceDict
        elif type(nbOfPoints) == int:
            # listOfPointIDs = list (phaseSpaceDict.keys()) [0:nbOfPoints]
            keyList = list(phaseSpaceDict.keys())
            listOfPointIDs = [random.choice(keyList) for i in range(nbOfPoints)]

            return {k: phaseSpaceDict[k] for k in set(phaseSpaceDict).intersection(listOfPointIDs)}

    def engineProcedure(self, generatingEngine, newParamsDict, threadNumber='0', debug=False,
                        ignoreInternal=False, ignoreExternal=False):
        '''
                Auxiliary procedure to compactify the generating engine and getting attributes.
            Also has the requirements for a engine along with the cleaning procedure
        '''
        # generatingEngine = self.engineClass()
        # generatingEngine = self.generatingEngine
        genValidPointOutDict = generatingEngine.runPoint(newParamsDict, threadNumber=threadNumber, debug=debug)

        # Associate a Point ID
        currTime = strftime("-%d%m%Y%H%M%S", gmtime())
        pointKey = 'Point T' + threadNumber + "-" + str(int(random.uniform(1, 1000))) + currTime

        phaseSpaceDict_int = generatingEngine._getRequiredAttributes(newParamsDict, threadNumber, genValidPointOutDict,
                                                                     pointKey)

        phaseSpaceDict = self._getCalcAttribForDict(phaseSpaceDict_int, threadNumber=threadNumber,
                                                    ignoreExternal=ignoreExternal, ignoreInternal=ignoreInternal)
        massTruth = generatingEngine._check0Mass(phaseSpaceDict)

        return massTruth, phaseSpaceDict

    def _mThreadAUXexplore(self, q, childConn, threadNumber="0", debug=False, newParamBounds={}, ignoreExternal=False,
                           ignoreInternal=False):  # <----- Needs NEW documentation!!!
        '''
                Auxiliary function needed for multithreading, which generates valid points in the phase space along
            with getting the required attributes and putting them in a dictionary, via a Queue().

            Will use the generating engine specified to produce the points. Requires engine have the following methods:
                †)  _genValidPoint          ::          Method should generate a valid phaseSpaceDictOut given
                    paramsDictMinMax.
                †)  _getRequiredAttributes  ::          Method that gets the required attributes from the out
                    given by _genValidPoint.
                †)  _check0Mass             ::          Consistency check on phaseSpaceDict.
                †)  _clean                  ::          Cleaning file method.

            Arguments:
                - q                     ::          Multiprocessing Queue() object which takes the results from all
                                                    the child processes and then passes them to the main function
                - threadNumber          ::          DEFAULT:'0' .  To be used in multiprocessing to identify what
                  thread is being used.
                - debug                 ::          DEFAULT = False. Set to True to get error messages and a Spectrum.
                  file when running points.
                - newParamBounds        ::      DEFAULT: {}. new bounds to be used if the user wants to target a
                  specific hypervolume in the phase space.


            Return:
                - Queue : [phaseSpaceDict]
                - Return : None

                Puts the valid phase space dictionary in a que that is used later for multithreading, but returns None

        '''
        generatingEngine = self.engineClass()
        # generatingEngine = self.generatingEngine
        # generatingEngine = self.engineClass(self.modelName, self.case)

        if bool(newParamBounds) is True:
            paramsDictMinMax = newParamBounds
        else:
            paramsDictMinMax = self.paramBounds

        smartRndGen = smartRand(paramsDictMinMax, self.condDict, self.rndDict, self.toSetDict)

        killMsg = False
        while killMsg is False:
            # print(threadNumber, ' Started ------------->')

            # Kill the child process if the parent has sent the message
            # print(killMsg)
            # if killMsg is True:
            #     print('\nTerminating Session Nb ', threadNumber)
            #     generatingEngine._terminateSession()
            #     childConn.send(threadNumber)
            #     return None
            # else:
            try:
                # Generate a random number and run it via the engine procedure
                newParamsDict = smartRndGen.genSmartRnd(debug=debug)
                # print('\n', threadNumber, ' Started ------------->')
                massTruth, phaseSpaceDict = self.engineProcedure(generatingEngine, newParamsDict,
                                                                 threadNumber=threadNumber,
                                                                 debug=debug, ignoreExternal=ignoreExternal,
                                                                 ignoreInternal=ignoreInternal)
                # print('\n', threadNumber, '  <------------- Finished')

                if massTruth is False:
                    generatingEngine._clean(threadNumber)
                    continue

                else:
                    # pp(phaseSpaceDict)
                    generatingEngine._clean(threadNumber)
                    pass

            except Exception as e:

                print(e)
                raise
                generatingEngine._clean(threadNumber)
                continue

            # print('Put in the Que', threadNumber)
            # print(phaseSpaceDict)
            q.put(phaseSpaceDict)

            if childConn.poll():
                killMsg = childConn.recv()
                # print('\n', killMsg, threadNumber)
            # else:
            #     killMsg = False
        if killMsg is True:
            printCentered(' Terminating Session Nb ' + threadNumber + ' ', color=Fore.RED, fillerChar='*')
            generatingEngine._terminateSession()
            childConn.send(threadNumber)

        return None

    def runMultiThreadExplore(self, numberOfPoints=10, nbOfThreads=1, debug=False, quitTime=50000, newParamBounds={},
                              runComment='', ignoreExternal=False, ignoreInternal=False):
        '''
                Multiprocessing Exploration Scan, main parent function to a number of _mThreadAUXexplore to get all
            the points and store them in a proper phaseSpaceDict.

            Arguments:
                - numberOfPoints        ::      DEFAULT:10 ; Number of Points intended for the scan to collect
                - nbOfThreads           ::      DEFAULT: 1 ; Number of child processes to be started and ran.
                - debug                 ::      DEFAULT: False ; Set to True to print out error messages &
                  Spectrum. files
                - quitTime              ::      DEFAULT: 300; If after quitTime secconds the scan can't find one
                  point that produces EWSB it exits and prints out an error message.
                - newParamBounds        ::      DEFAULT: {}. new bounds to be used if the user wants to target a
                  specific hypervolume in the phase space.

                Returns:
                    - None.
                        Writes a ScanResults.xxxxxxx.json file with the complete phaseSpaceDict in the
                    Results/modelName/Dicts/ directory:

                    phaseSpaceDict = {"Point ...1": { Params : {...},
                                                     Particles:{...},
                                                     Couplings{...}},
                                      "Point ...2": { Params : {...},
                                                      Particles:{...},
                                                      Couplings{...}},
                                       ... }
        '''
        # modelName = self.modelName
        # replacementRules = self.rules
        # caseHandle = self.case
        # print(delimitator)

        localQue = Queue()
        # parentConn, childConn = Pipe()
        # connDict
        connDict = {'Conn::' + str(x): Pipe() for x in range(nbOfThreads)}
        processes = {'Proc::' + str(x): Process(target=self._mThreadAUXexplore,
                                                args=(localQue, connDict['Conn::' + str(x)][1], str(x),
                                                      debug, newParamBounds, ignoreExternal, ignoreInternal))
                     for x in range(nbOfThreads)}

        resultDict = {}
        for procKey in processes.keys():
            processes[procKey].start()

        abandonScan = False
        spinner = Halo(text='Trying to find a valid point in phase space. Will timeout after '
                            + Fore.RED + str(quitTime) + ' s' + Style.RESET_ALL, spinner='dots')
        spinner.start()

        try:
            result = localQue.get(block=True, timeout=quitTime)
        except Exception as e:
            spinner.stop_and_persist(symbol=Fore.RED+'\u2718' + Style.RESET_ALL,
                                     text='Cannot find valid point in phase space.')
            errorMsg = '\n' + Fore.RED + "Timeout Reached." + Fore.GREEN + \
                       " Model with specified rules cannot produce valid points in phase space. " + Style.RESET_ALL
            print(errorMsg)

            for procKey in processes.keys():
                processes[procKey].terminate()
            # for proc in processes:
            #     proc.terminate()
            abandonScan = True

        if abandonScan is False:

            spinner.stop_and_persist(symbol=Fore.GREEN+'\u2713' + Style.RESET_ALL,
                                     text='Model can produce points in phase space. Starting scan for '
                                     + Fore.RED + self.modelName + '-' + self.case + Style.RESET_ALL)

            pointHandle = 0
            scanID = self.modelName + '_' + self.case.replace(" ", "") + '_' + strftime("%d-%m-%-Y_%H:%M:%S", gmtime())

            resultsDirDicts = self.resultDir + 'Dicts/'
            subprocess.call('mkdir ' + resultsDirDicts, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

            writeToLogFile_Action(self, 'Started', 'Explore')
            printHeader('Explore', 'Started', nbOfThreads)
            pbar = tqdm(total=numberOfPoints,
                        bar_format='%s{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]' % Fore.GREEN)

            try:
                while pointHandle < numberOfPoints:

                    result = localQue.get()
                    resultDict.update(result)
                    pbar.update(1)

                    # ### Update the Json file every 10 pointsself.
                    if True:  # pointHandle % 10 == 0:
                        # print(delimitator)
                        # print(result)
                        # print(type(result))
                        # print(delimitator)
                        with open(resultsDirDicts + 'ScanResults.' + scanID + '.json', 'w') as outfile:
                            json.dump(resultDict, outfile)

                    pointHandle += 1

            except KeyboardInterrupt:
                # raise
                print('\nProcess killed by user')
                pbar.close()
                for procKey in processes.keys():
                    processes[procKey].terminate()
                connDict = {}
                processes = {}

            finally:
                # Kill the sessions
                # print(delimitator)
                for connID in connDict.keys():
                    connDict[connID][0].send(True)

                while processes:
                    while connDict:
                        # localQue.get(block=False)

                        connID = random.choice(list(connDict.keys()))
                        if connDict[connID][0].poll():
                            killThreadNb = connDict[connID][0].recv()
                            processes['Proc::' + str(killThreadNb)].terminate()
                            del processes['Proc::' + str(killThreadNb)]
                            del connDict['Conn::' + str(killThreadNb)]
                            # print(bool(processes), processes)

                pbar.close()
                for procKey in processes.keys():
                    processes[procKey].terminate()
                # for proc in processes:
                #     proc.terminate()

                printHeader('Explore', 'Finished', nbOfThreads)
                print(Style.RESET_ALL)

                writeToLogFile_Action(self, 'Finished', 'Explore')
                # mergeAllResDicts(self)

        spinnerWait = Halo(text='Waiting for everything to finish running.', spinner='dots')
        spinnerWait.start()

        self.cleanRun(nbOfThreads)
        spinnerWait.stop_and_persist(symbol=Fore.GREEN + '✔' + Style.RESET_ALL, text='Done cleaning.')

        return resultDict

    def cleanRun(self, nbOfThreads):
        '''
            Cleaning method used to clean all the possible remnants of the threads.

            Arguments:
            -   nbOfThreads     ::      Total number of threads over which it should clean

            Return:
            -   None
        '''
        # generatingEngine = self.engineClass( self )
        generatingEngine = self.generatingEngine
        for threadNumber in range(nbOfThreads):
            generatingEngine._clean(threadNumber)

        return None

    # ####################  Evaluations ##############################################
    def _getCalcAttribForDict(self, phaseSpaceDict,  exportJson=False, ignoreInternal=False, ignoreExternal=False,
                              threadNumber='0'):
        '''
            Given a phaseSpaceDict, for each point in the phase space,  the function will go through the calcDict
        specified in the configFile, and calculate the specified attributes.

        Arguments:
            - phaseSpaceDict            ::      Phase space dictionary containing a numbe of points.
            - disableExternal           ::      DEFAULT: False. Set to True to enable external dependency calculations.
            - exportJson                ::      DEFAULT: False. Set to True to export to json , the new phaseSpaceDict
              with the calculated
                                                attributes.
        Returns:
            - phaseSpaceDict            with the new calculated attributes.
        '''

        for point in phaseSpaceDict.keys():
            for calcParam in self.calc.keys():

                # ############# Possible BADNESS = 10000 ±!!!!!
                if calcParam not in phaseSpaceDict[point].keys():
                    phaseSpaceDict[point][calcParam] = None

                if (phaseSpaceDict[point][calcParam] is None):
                    # ############# InternalCalc ################################
                    if ignoreInternal is False:
                        if self.calc[calcParam]['Calc']['Type'] == 'InternalCalc':
                            for paramToUse in self.calc[calcParam]['Calc']['ToCalc']['ParamList']:
                                exec(paramToUse + '=' + str(phaseSpaceDict[point][paramToUse]))

                            calcParamVal = eval(self.calc[calcParam]['Calc']['ToCalc']['Expression'])

                            phaseSpaceDict[point][calcParam] = calcParamVal
                    else:
                        pass

                    # ############# External ################################
                    if ignoreExternal is False:
                        if self.calc[calcParam]['Calc']['Type'] == 'ExternalCalc':

                            # routineStr = 'Routines.' + self.calc[calcParam]['Calc']['Routine']
                            routineModule = self.calcRoutines[calcParam]
                            methodStr = self.calc[calcParam]['Calc']['Method']

                            # routineModule = importlib.import_module(routineStr)

                            extParamDict = {}
                            for paramName in self.calc[calcParam]['Calc']['ParamList']:
                                extParamDict[paramName] = phaseSpaceDict[point][paramName]

                            calcVal = routineModule.__dict__[methodStr](extParamDict, threadNumber=threadNumber)
                            phaseSpaceDict[point][calcParam] = calcVal
                    else:
                        pass

        if exportJson is True:

            spinner = Halo(text='Writing to JSON.', spinner='dots')
            spinner.start()
            scanID = self.modelName + self.case.replace(" ", "") + '_wPM_wCalc' + strftime("-%d%m%Y%H%M%S", gmtime())

            # Remove old jsonDicts
            subprocess.call('rm ' + self.resultDir + 'Dicts/*', shell=True)
            # Write to new jsonDict
            with open(self.resultDir + 'Dicts/' + scanID + '.json', 'w') as outFile:
                json.dump(phaseSpaceDict, outFile)

            spinner.stop_and_persist({'symbol': Fore.GREEN + '✓' + Style.RESET_ALL, 'text': 'Finished.'})

        return phaseSpaceDict

    def getTopNChiSquaredPoints(self, phaseSpaceDict, countChi2, minimisationConstr='Global', specificCuts='Global',
                                ignoreConstrList=[], returnDict=False, exportAsDict=False, sortByChiSquare=True,
                                sortbyThrNb=False, statistic='ChiSquared'):  # Needs more documentation
        '''
                Given a phase Space dictionary, and a the top number of points to be ranked via their chi2 value, the
            function returns the sorted list of chi2 values (where chi2 refferes to the TEST statistic). Can be toggled
            to return the dictionary, or return the countChi2 random number of points.

            Arguments:
            -   phaseSpaceDict  ::  Type=Dict. Phase space dictionary contianing a number of points with their IDs.
            -   countChi2   ::  Type=Int. The N top number of points to be returned.

            -   sortByChiSquare    ::    OPTIONAL, Type=Bool. Set to False to return just a random sorted order.
                Function then acts as a cut on the top N points on the stack.
        '''

        chiSquareDict = {}
        modelConstr = constrEval(self)

        for pointKey in phaseSpaceDict.keys():

            notemptyDict = True
            for modelAttribute in self.allDicts.keys():
                if modelAttribute not in self.noneAttr and (phaseSpaceDict[pointKey][modelAttribute] != 0):

                    notemptyDict = notemptyDict and bool(phaseSpaceDict[pointKey][modelAttribute])

            # ### Not entirely sure about the checkHardCut if it should or shouldn't be in here.
            if notemptyDict is True and modelConstr._checkHardCut(phaseSpaceDict[pointKey], specificCuts=specificCuts):

                # print('aaaaaaaaaa')
                if statistic == 'ChiSquared':
                    chiSquare = modelConstr.getChi2(phaseSpaceDict[pointKey], ignoreConstrList=ignoreConstrList,
                                                    minimisationConstr=minimisationConstr, returnDict=False)
                elif statistic == 'LogL':
                    chiSquare = modelConstr.getLogLikelihood(phaseSpaceDict[pointKey])
                chiSquareDict[pointKey] = chiSquare
                # print(chiSquare)

        if sortbyThrNb is True:
            sortedChiSquare_ListOfTuples = sorted(chiSquareDict.items(), key=lambda kv: kv[0])
        else:
            if sortByChiSquare is True:
                sortedChiSquare_ListOfTuples = sorted(chiSquareDict.items(), key=lambda kv: kv[1])
            else:
                sortedChiSquare_ListOfTuples = [(pointKey, chiSquareDict[pointKey])
                                                for pointKey in chiSquareDict.keys()]

        # pp(sortedChiSquare_ListOfTuples)
        # exit()
        # pp(sortedChiSquare_ListOfTuples)
        # print(delimitator)
        # pp(constrAux)
        #
        # exit()

        if exportAsDict is False:
            topChi2List = []
            for pointAttr in sortedChiSquare_ListOfTuples[0:countChi2]:
                pointKey = pointAttr[0]
                topChi2List.append({pointKey: phaseSpaceDict[pointKey]})
        else:
            topChi2List = {}
            for pointAttr in sortedChiSquare_ListOfTuples[0:countChi2]:
                pointKey = pointAttr[0]
                topChi2List.update({pointKey: phaseSpaceDict[pointKey]})

        return topChi2List, sortedChiSquare_ListOfTuples[0:countChi2]

    def _restrictInterestingPoints(self, phaseSpaceDict, restrictingParam, restrictingParamMin, restrictingParamMax):
        '''
                Restricts phaseSpaceDict to a subregion specified by restrictingParam, and the bounds
            [restrictingParamMin, restrictingParamMax].

            Arguments:
                - listOfInteresingPoints                    ::          List of interesting points
                  from getInterstingPoints.
                - restrictingParam                          ::          Attribute to restrict.
                - restrictingParamMin, restrictingParamMax  ::          Bounds for the restriction.

            Returns:
                - vettedList :
                List of the points that are within the subregion.
        '''
        vettedDict = {}
        modelConstr = constrEval(self)

        # paramType  = self.classification[restrictingParam]

        for phaseSpacePointDict in phaseSpaceDict.items():

            pointAttr = phaseSpacePointDict[1]
            pointKey = phaseSpacePointDict[0]

            if restrictingParam == 'ChiSquared':
                toVet = modelConstr.getChi2(pointAttr)

            else:
                toVet = pointAttr[restrictingParam]

            # ## Vetting procedure ####
            if restrictingParamMax > toVet > restrictingParamMin:
                vettedDict[pointKey] = pointAttr

        return vettedDict

    def filterDictByCutDict(self, phaseSpaceDict, cutDict):
        '''
            Give a valid phase space dictionary phaseSpaceDict, and a cut Dictionary of the form :

            E.g.
                cutDict = {
                           'mTop'   :   {'Min':162.0, 'Max' : 182.0},
                           'Higgs'  :   {'Min':115.0, 'Max' : 135.0},
                           'ChiSquared' :{'Min':0.0, 'Max' : 100.0}
                           }
            The function will return the points in the phaseSpaceDict that lie within ALL the specified bounds
            in the cutDict
        '''
        for attrToCut in cutDict.keys():

            vettedDict = self._restrictInterestingPoints(phaseSpaceDict, attrToCut, cutDict[attrToCut]['Min'],
                                                         cutDict[attrToCut]['Max'])

            phaseSpaceDict = vettedDict

        return phaseSpaceDict

    def _exportFocusStats(self, focusDir, nbOfPoints, numbOfCores, algorithm):
        '''
            Exports the stats of the focus run so it can be recreated
        '''
        dataDict = {'nbOfPoints': nbOfPoints, 'numbOfCores': numbOfCores, 'algorihm': algorithm}
        with open(focusDir + 'RunCard.pickle', 'wb') as fPickl:
            pickle.dump(dataDict, fPickl, pickle.HIGHEST_PROTOCOL)

    # def _getAlgInitPop(self, phaseSpaceDict, numberOfCores, numberOfPoints):

    def runGenerationMultithread(self, phaseSpaceDict, numberOfPoints=16, numbOfCores=1,
                                 minimisationConstr='Global', ignoreConstrList=[], noOfSigmasB=1, noOfSigmasPM=1,
                                 timeOut=600, debug=False,
                                 chi2LowerBound=1.0,  sortByChiSquare=True,
                                 algorithm='singleCellEvol',  statistic='ChiSquared',
                                 reload=False, enableSubSpawn=False,
                                 ignoreExternal=False, ignoreInternal=False
                                 ):
        '''
                Given a phaseSpaceDict of points the function will multiprocess on numberOfCores a certain number of
            numberOfPoints, either randomly selected , or selected by their chi2 Value. The specified algorithm will
            produce a generational evolution.
        '''

        # if sortByChiSquare == False and algorithm == 'diffEvol':
        #     numberOfPoints = len( list( phaseSpaceDict.keys() ) )

        bestChiSquares, sortedChiSquare_ListOfTuples = self.getTopNChiSquaredPoints(phaseSpaceDict, numberOfPoints,
        sortByChiSquare=sortByChiSquare, sortbyThrNb=reload, statistic=statistic)

        if bool(bestChiSquares) is False:
            printCentered('  ❎ Empty list of χ²s. Check Constraints and point list ', color=Fore.RED, fillerChar='-')
            return None

        listOfchi2Lists = chunkList(bestChiSquares, numbOfCores, threadNBSort=reload)
        listOfsortedChi2Lists = chunkList(sortedChiSquare_ListOfTuples, numbOfCores, threadNBSort=reload)

        localQue = Queue()
        algClasses = [minimAlg(self, localQue, listOfchi2Lists[x], listOfsortedChi2Lists[x],
                               str(x), minimisationConstr, timeOut,  ignoreConstrList, noOfSigmasB, noOfSigmasPM,
                               debug, chi2LowerBound, ignoreExternal, ignoreInternal)
                      for x in range(numbOfCores)]

        processes = {'Proc::'+str(x+1): Process(target=algClasses[x].__class__.__dict__[algorithm],
                                                args=[algClasses[x]]
                                                )
                     for x in range(numbOfCores)}

        # ####################### Printing info and generating Scan ID ########################
        scanID = self.modelName + self.case.replace(" ", "") + strftime("-%d-%m-%Y_%H_%M_%S", gmtime())
        resultsDirDicts = self.resultDir + 'Dicts/Focus' + strftime("-%m-%d-%Y_%H_%M_%S/", gmtime())
        subprocess.call('mkdir ' + resultsDirDicts, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call('mkdir ' + resultsDirDicts + 'GenResults', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        self._exportFocusStats(resultsDirDicts, numberOfPoints, numbOfCores, algorithm)
        print(delimitator)

        resultDict = {}
        for procKey in processes.keys():
            processes[procKey].start()
        writeToLogFile_Action(self, 'Started', 'Focus_' + algorithm)

        spinnText = 'Started ' + Fore.RED + strftime("%d/%m/%Y at %H:%M:%S ", gmtime()) + Style.RESET_ALL \
                    + 'Running on ' + Fore.RED + str(len(processes.keys())) + ' thread/s.' + Style.RESET_ALL\
                    + ' Lower Statistic bound of ' + Fore.RED + str(round(chi2LowerBound, 4)) + Style.RESET_ALL
        spinner = Halo(text=spinnText, spinner='dots')
        spinner.start()

        try:
            while len(processes) > 0:
                result = localQue.get()

                # ### Update the generational status of the thread sending the information
                if 'GenStat' in result.keys():
                    genNb, chi2Min, chi2Mean, chi2Std = result['GenStat']['GenNb'], result['GenStat']['chi2Min'], result['GenStat']['chi2Mean'], result['GenStat']['chi2Std']
                    thrNb_str = str(result['GenStat']['ThreadNb'])

                    writeGenStat(resultsDirDicts, str(result['GenStat']['ThreadNb']),
                                 [genNb, chi2Min, chi2Mean, chi2Std],
                                 ['GenNb-', 'MinChi2: ', 'MeanChi2: ', 'StdChi2: '])

                    subprocess.call('rm ' + resultsDirDicts + 'GenResults/*ThreadNb-'
                                    + str(result['GenStat']['ThreadNb']) + '*', shell=True, stdout=FNULL,
                                    stderr=subprocess.STDOUT)

                    with open(resultsDirDicts + 'GenResults/GenResults.' + str(genNb) + '-ThreadNb-'
                              + str(result['GenStat']['ThreadNb']) + '.json', 'w') as genOut:
                        json.dump(result['GenStat']['GenDict'], genOut)

                    if enableSubSpawn is True and self._evalKillThread(thrNb_str, algorithm, resultsDirDicts) is True:

                        newAlg = self._getSubAlgorithm(algorithm)
                        swicthAlg = {'NewAlg': newAlg}

                        # #### Kill current thread and start a new gnerational run with the remnants of current gen.
                        processes['Proc::' + thrNb_str].terminate()
                        del processes['Proc::' + thrNb_str]
                        print(len(processes))
                        print(3*(Fore.YELLOW + delimitator))

                        processes_subThr = Process(target=self.resumeGenRun, args=('MostRecent', swicthAlg, thrNb_str))
                        processes_subThr.start()

                # ### Update the json result file of the thread sending the info
                if 'NewPoint' in result.keys():
                    scanIDwThread = scanID + '_ThreadNb-' + str(result['NewPoint']['ThreadNb'])
                    with open(resultsDirDicts + 'ScanResults.' + scanIDwThread + '.json', 'a') as outfile:
                        json.dump(result['NewPoint']['Dict'], outfile)

                # ### Terminate the respective thread sending the information
                if 'Terminate' in result.keys():
                    processes['Proc::'+str(result['Terminate'])].terminate()
                    del processes['Proc::'+str(result['Terminate'])]

        except KeyboardInterrupt:
            print('\nProcess killed by user')

        # ########### Terminate the processes #############
        for procKey in processes.keys():
            processes[procKey].terminate()
        spinner.stop()

        writeToLogFile_Action(self, 'Finished', 'Focus_' + algorithm)
        self.cleanRun(numbOfCores)
        fixJsonWAppend(resultsDirDicts)

        print(Fore.GREEN + delimitator + Style.RESET_ALL)

        return resultDict

    def _evalKillThread(self, threadNb, algorithm, focusDir, genOfSet=6, evolPerc=0.01, ordMag=1):
        '''
            Condition to kill a thread based on the convergence speed, varies for each algorithm specified.
        '''
        try:
            with open(focusDir + 'GenStatus_ThreadNb' + threadNb + '.dat', 'r') as fileIn:
                GenStatAll = fileIn.readlines()
        except Exception as e:
            print(e)
            return False

        statDict = {}
        for genLine in GenStatAll:
            genNb = genLine.replace(' ', '').split('||')[0]

            auxDict = {attrName: float(genLine.replace(' ', '').split('||')[x].split(':')[1])
                       for x, attrName in zip([1, 2, 3], ['MinChi2', 'MeanChi2', 'StdChi2'])}
            statDict.update({genNb: auxDict})

        genList_revSort = sorted(statDict.keys(), key=lambda genNbr: int(genNbr.split('-')[1]), reverse=True)
        latestGen = genList_revSort[0]

        try:
            targetGen = genList_revSort[genOfSet]
        except Exception as e:
            print(e)
            return False
        else:
            # evolPerc = 0.5
            # ordMag = 1

            currChi2Mean = statDict[latestGen]['MeanChi2']
            currChi2Std = statDict[latestGen]['StdChi2']
            currChi2Min = statDict[latestGen]['MinChi2']
            prevChi2Min = statDict[targetGen]['MinChi2']

            # pp(subAlg_rules[algorithm])

            if algorithm == 'diffEvol':
                # ### Cut diff evolution if :
                # 1) The current Mean and Minimum are 1 σ away from each other
                # 2) Current Minimum hasn't evolved more than 1 % in the last genOfSet entries

                if (currChi2Mean // 10**ordMag) > currChi2Std:
                    print('001', threadNb, algorithm, currChi2Min, currChi2Std)
                    return True

                # prevChi2Min = statDict[targetGen]['MinChi2']
                if abs(prevChi2Min - currChi2Min) / prevChi2Min < evolPerc:
                    print('002', threadNb, algorithm, prevChi2Min, currChi2Min)
                    return True

            elif algorithm == 'singleCellEvol':
                # ### Cut single Cell evolution if :
                # 1) Current Minimum hasn't evolved more than 1 % in the last genOfSet entries

                if abs(prevChi2Min - currChi2Min) / prevChi2Min < evolPerc:
                    print('001', threadNb, algorithm, currChi2Min, currChi2Std)
                    return True

        print('000')
        return False

    def _getSubAlgorithm(self, algorithm):
        '''
            Given an algorithm function returns one of the subalgorithms specified by the user in the algorithm module.
        '''

        return random.choice(subAlg_rules[algorithm]['Children'])

    def _setAlgParams(self, algorithm, numbOfCores, nbOfPoints, threadNb='All'):
        '''
            Given the algorithm will set  numberOfPoints ,  sortByChiSquare
        '''
        if threadNb == 'All':
            algDict = {'singleCellEvol': {'numbOfCores': nbOfPoints,
                                          'nbOfPoints': nbOfPoints,
                                          'sortByChiSquare': True},
                       'diffEvol': {'numbOfCores': numbOfCores,
                                    'nbOfPoints': nbOfPoints,
                                    'sortByChiSquare': False}
                       }
        else:
            algDict = {'singleCellEvol': {'numbOfCores': nbOfPoints // numbOfCores,
                                          'nbOfPoints': nbOfPoints // numbOfCores,
                                          'sortByChiSquare': True},
                       'diffEvol': {'numbOfCores': 1,
                                    'nbOfPoints': nbOfPoints // numbOfCores,
                                    'sortByChiSquare': False}
                       }

        return algDict[algorithm]

    def resumeGenRun(self, focusDateTime_str='MostRecent', swicthAlg=False, threadNb='All'):
        '''
                Used to continue the generational multirun if interupted. Defaults to the most recent run of the model,
            loads the parameter and algorithm runs from the pickle run file.
        '''

        try:
            # focusDate = ''
            dirEntries = os.listdir(self.resultDir + 'Dicts/')

            listOfDirs = []
            for dirEntry in dirEntries:
                if 'Focus' in dirEntry and ('.' not in dirEntry):
                    listOfDirs.append(dirEntry.replace('Focus_', ''))

            focusDate_DateTime = checkListForLatestDate(listOfDirs)
            focusDateTime_str = convertDateTimeToStr(focusDate_DateTime)

        except Exception as e:
            print(e)
            raise
        # print(focusDate)
        # exit()

        focusDir = self.resultDir + 'Dicts/Focus-' + focusDateTime_str + '/'
        pickleName = focusDir + 'RunCard.pickle'
        with open(pickleName, 'rb') as fPickl:
            runCard = pickle.load(fPickl)
        threadDict = []

        # ### Gather the latest generational data
        try:
            dirEntries = os.listdir(focusDir + 'GenResults/')

            for dirEntry in dirEntries:
                with open(focusDir + 'GenResults/' + dirEntry, 'r') as jsonIn:
                    thData = json.load(jsonIn)

                # pp(thData)
                thrNb = str(dirEntry.split('ThreadNb-')[1].replace('.json', ''))
                if threadNb != 'All' and thrNb == threadNb:

                    threadDict.append(thData)
                elif threadNb == 'All':
                    threadDict.append(thData)

        except Exception as e:
            print(e)
            raise

        pp(runCard)
        sortByChiSquare = False
        reload = False

        if type(swicthAlg) == dict:
            runCard['algorihm'] = swicthAlg['NewAlg']
            newAlgDict = self._setAlgParams(swicthAlg['NewAlg'], runCard['numbOfCores'], runCard['nbOfPoints'],
                                            threadNb=threadNb)
            # pp(newAlgDict)
            runCard['nbOfPoints'], runCard['numbOfCores'], sortByChiSquare = newAlgDict['nbOfPoints'], newAlgDict['numbOfCores'], newAlgDict['sortByChiSquare']
            reload = False

        psDict = {}
        for dictToApp in threadDict:
            psDict.update(dictToApp)

        # pp(psDict)
        # pp(runCard)
        # exit()
        # pp(psDict)
        # print(delimitator)
        self.runGenerationMultithread(psDict, numbOfCores=runCard['numbOfCores'], numberOfPoints=runCard['nbOfPoints'],
                                      algorithm=runCard['algorihm'], sortByChiSquare=sortByChiSquare, reload=reload)

        return None

    def _mThreadAUXrerun(self, q, listOfPoints, threadNumber='0', debug=False, ignoreInternal=False,
                         ignoreExternal=False):
        '''
            Auxiliary worker multiprocessing function used to do a phase space rerun. Called in the master
        function reRunMultiThreadself.

        Arguments:
            - q                     ::       Queue() object that passes results to the master function.
            - listOfPoints          ::       List of points to be run by a specific thread.
            - threadNumber          ::       DEFAULT: 0 . Identifies the thread number, is set in the master function.
            - debug                 ::       DEFAULT: False. Set to True to enable verbose error messages.

        Returns:
            - None      ;;     !!Puts results in Queue()
        '''
        # generatingEngine = self.engineClass(self)
        generatingEngine = self.generatingEngine

        ################################################################
        while bool(listOfPoints) is not False:
            paramsDict = listOfPoints[-1]

            try:
                massTruth, phaseSpaceDict = self.engineProcedure(generatingEngine,
                                                                 paramsDict, threadNumber=threadNumber, debug=debug,
                                                                 ignoreExternal=ignoreExternal,
                                                                 ignoreInternal=ignoreInternal)

                # generatingEngine.runPoint( paramsDict, threadNumber = threadNumber , debug = debug)
                # phaseSpaceDict = generatingEngine._getRequiredAttributes(paramsDict, threadNumber)
                # massTruth = generatingEngine._check0Mass( phaseSpaceDict )

                if massTruth is True:
                    q.put(phaseSpaceDict)

                # generatingEngine._clean( threadNumber)
                listOfPoints.pop()

            except Exception as e:

                print(e)
                listOfPoints.pop()
                # generatingEngine._clean( threadNumber )

                q.put(None)

        return None

    def reRunMultiThread(self, phaseSpaceDict, numbOfCores=8, debug=False,  ignoreInternal=False,
                         ignoreExternal=False):
        '''
            Master multiprocessing function to be used to rerun points in a phaseSpaceDict. Writes the results to json,

            !!!!!!!!!!!! DELETES OLD RESULTS AND LOGS !!!!!!!!!!!!!

            Arguments:
                - phaseSpaceDict        ::       Dictionary of points in the phase space.
                - numbOfCores           ::       DEFAULT: 14. Should be set to whatever the optimum number is for
                  the machine on which it  is run. Run the corePicker utility to find the optimum.
                - debug                 ::       DEFAULT: False. Set to True to enable verbose error messages.

            Returns:
                - None

        '''
        listOfLists = []
        for core in range(numbOfCores):
            listOfLists.append([])
        pointCounter = 0

        for point in phaseSpaceDict.keys():
            try:
                phaseSpacePoint = phaseSpaceDict[point]['Params']
            except Exception as e:
                paramsDict = {modelAttr: phaseSpaceDict[point][modelAttr] for modelAttr in self.params}
                phaseSpacePoint = paramsDict

            listOfLists[pointCounter % numbOfCores].append(phaseSpacePoint)
            pointCounter += 1

        # pp(listOfLists)
        # exit()

        localQue = Queue()
        processes = [Process(target=self._mThreadAUXrerun,
                             args=(localQue, listOfLists[coreNumber], str(coreNumber), debug, ignoreInternal,
                                   ignoreExternal))
                     for coreNumber in range(numbOfCores)]

        for proc in processes:
            proc.start()

        scanID = self.modelName + '_' + self.case.replace(" ", "") + '_' + strftime("%d-%m-%-Y_%H:%M:%S", gmtime())
        printHeader('ReRun', 'Started', numbOfCores)
        writeToLogFile_Action(self, 'Start', 'ReRun')
        pbar = tqdm(total=pointCounter,
                    bar_format='%s{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]' % Fore.LIGHTYELLOW_EX)

        resultDict = {}
        pointCounterCopy = pointCounter

        try:
            while pointCounter > 0:
                result = localQue.get()

                if result is not None:
                    resultDict.update(result)
                pbar.update(1)

                if pointCounter % 10 == 0:
                    with open(self.resultDir + 'Dicts/ReRun_ScanResults.' + scanID + '.json', 'w') as outfile:
                        json.dump(resultDict, outfile)

                pointCounter += (-1)
                ##################################################
        except KeyboardInterrupt:
            print('\nProcess killed by user')

        for proc in processes:
            proc.terminate()

        pbar.close()
        printHeader('ReRun', 'Finished', numbOfCores)
        print('Success Rate: ', len(resultDict), ' /', pointCounterCopy)
        print(Style.RESET_ALL)

        # ######################   Clean old dicts and plots #########################
        # subprocess.call('rm *.json', shell = True, cwd = self.resultDir + 'Dicts/' )
        # subprocess.call('rm -r Plots', shell = True, cwd = self.resultDir )

        # with open(self.resultDir + 'Dicts/ScanResults.' + scanID + '.json', 'w') as outfile:
        #     json.dump(resultDict, outfile)
        # self.cleanFiles()

        writeToLogFile_Action(self, 'Finished', 'ReRun')
        # mergeAllResDicts(self)

        return None

    def exportPSDitctCSV(self, phaseSpaceDict, listOfAttr, nameOut='Default'):
        '''
                Given a phase space dictionary function will create a csv file with the PointIDs and the attributes
            specified in listOfAttr
        '''
        # write it
        if nameOut == 'Default':
            csvFileName = 'ExportCSV-' + strftime("-%d-%m-%Y_%H:%M:%S", gmtime()) + '.csv'
        else:
            csvFileName = nameOut + '.csv'

        with open(self.resultDir + csvFileName, 'w') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(['PointID'] + listOfAttr)
            # [writer.writerow(r) for r in tableConstr]

            for pointTuple in phaseSpaceDict.items():
                pointID = pointTuple[0]
                pointAttr = pointTuple[1]

                rowToWrite = [pointID]

                for attrToAdd in listOfAttr:

                    rowToWrite.append(pointAttr[attrToAdd])

                writer.writerow(rowToWrite)

        return None


if __name__ == '__main__':

    # modelName = 'ackleyFunct'
    # auxCase ='DummyCase'
    # micrOmegasName = modelName

    modelName = 'SO11Hosotani'
    auxCase = 'DummyCase'
    micrOmegasName = modelName

    # genEngine = 'HosotaniSO110'
    # engineString = 'Engines.' + genEngine + ".engine_" + genEngine
    # engineModule_Class = importlib.import_module(engineString)
    # engine = engineModule_Class()
    newModel = phaseScannerModel(modelName, auxCase, micrOmegasName=micrOmegasName, writeToLogFile=True)
    print(len(newModel.loadResults(targetDir='Dicts/PlotDicts_Sep2019/', ignoreIntegrCheck=True)))
