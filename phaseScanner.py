# import os
import subprocess
import json
from multiprocessing import Process, Queue, Pipe
import importlib
from time import gmtime, strftime


from halo import Halo
from tqdm import tqdm
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



from Utils.printUtils import *
from Utils.SmartRandomGenerator.smartRand import *
from Utils.metaLogging import *
from Utils.constrEval  import *
# from Utils.multiThreadAlg import *





def genRndDict(paramDict):
    '''
        Given a parameter Dictionary , the function will generate the default random pciker with Succes as the 1st stage, e.g. :

        rndDict = OrderedDict ([  ('Check-0', {'ToPick': ['Lambda', 'Kappa', 'tanBeta'],
                                               'ToCheck': [],
                                               'ToSet' : [],
                                               'Pass' : 'Success',
                                               'Fail' : 'Check-0'}
                                  )
                                ])
    '''
    from collections import OrderedDict

    rndDict = OrderedDict ([  ('Check-0', {'ToPick': list( paramDict.keys() ),
                                           'ToCheck': [],
                                           'ToSet' : [],
                                           'Pass' : 'Success',
                                           'Fail' : 'Check-0'}
                              )
                            ])
    return rndDict

class phaseScannerModel:
    '''
        Class that initialises a phaseScannerModel model and then is used to to the various things specified in the documentation.

        Pre-requirements:
            - Generating engine for the points with it's required functionalities.

    '''

    def __init__(self, modelName, caseHandle, micrOmegasName='', userDescription="" ,       writeToLogFile = False):
        '''
            Init stage for the modelFS class.

            Attributes:
                - modelName             ::      Name of the specified model that we want to work with.
                - caseHandle            ::      Casehandle that specifies which case the model will be dealing with.
                                                !!! NOTE : if there's just one case pass dummy case handle e.g. 'DummyCase'.

                - generatingEngine      ::      Engine that will generate the required attributes. Should be the same name as the .py file in Engines/

                - userDescription       ::      Description user passes to further help with identification.
                - writeToLogFile        ::      Set to True to write to log file.
        '''


        import importlib
        configString = 'Configs.configFile_' + modelName


        try:
            configModule = importlib.import_module(configString)
        except Exception as e:
            print(e)

        self.genEngine = configModule.genEngine
        self.engineVersion = configModule.engVers
        engineString = 'Engines.' + self.genEngine + ".engine_" + self.genEngine

        try:
            engineModule = importlib.import_module(engineString)
        except Exception as e:
            print(e)

        ############### Engine class ###################
        self.engineClass = engineModule.engineClass

        ############### Model Bits ###################
        self.modelName = modelName
        self.case = caseHandle
        if micrOmegasName != '':
            self.micrOmegasName = modelName

        ############### Data bits ####################
        # self.targetDir = configModule.engineDir
        # self.runCMD = configModule.runCMD
        self.description = userDescription

        ############## Smart Random Bits ############
        try:
            self.rndDict = configModule.rndDict
            self.condDict = configModule.condDict
            self.toSetDict = configModule.toSetDict

        except Exception as e:
            self.condDict = {}
            self.toSetDict = {}
            self.rndDict = genRndDict(configModule.paramDict)
            print(Fore.YELLOW, delimitator2, e, '\nWARNING: Created default random parameter selection.', Style.RESET_ALL)


        ####### Result and Log directories #########
        if ('Utils' in os.getcwd()):
            self.resultDir = '../Results/' + modelName + '_' +caseHandle.replace(" ", '') + '/'
            self.logDir = '../Logs/' + modelName + '_' +caseHandle.replace(" ", '') + '/'
        else:
            self.resultDir = 'Results/' + modelName + '_' +caseHandle.replace(" ", '') + '/'
            self.logDir = 'Logs/' + modelName + '_' +caseHandle.replace(" ", '') + '/'


        for dirToMake in ['Results/', 'Logs/', self.resultDir, self.logDir]:
            subprocess.call('mkdir ' + dirToMake, shell = True,  stdout=FNULL, stderr=subprocess.STDOUT)


        ####### Params, Particles , Rules, Calcs ###########

        self.params = configModule.paramDict
        self.rules = configModule.replacementRules[caseHandle]

        self.modelAttrs = configModule.attrDict
        self.calc = configModule.calcDict

        try:
            self.noneAttr = configModule.noneAttr
        except Exception as e:
            self.noneAttr = []
        finally:
            self.noneAttr.append('ChiSquared')

        #### Param Ranges and sigmas ##############
        self.paramBounds = configModule.dictMinMax

        try:
            self.plotFormatting = configModule.plotFormatting
        except Exception as e:
            print(Fore.YELLOW, delimitator2, e, '\nWARNING: Setting default plotting attrs.', Style.RESET_ALL)
            self.plotFormatting = {
                 'failPlot' : {'alpha':0.5, 'lw' :0, 's':100},
                 'passPlot' : {'alpha':1,   'lw' : 0.6, 's':240},
                 'fontSize' : 40
                  # 'failPlot' : {'alpha':0.1, 'lw' :0, 's':30},
                  # 'passPlot' : {'alpha':1,   'lw' : 0.17, 's':140}
                  # 'fontSize' : 30
            }

        ##### Classification & All dicts #################
        classDict = {}
        for params, paramType in zip( [self.params.keys(), self.modelAttrs.keys(), self.calc.keys()] , ['Param', 'Attr', 'Calc']):
            for param in params:
                classDict[param] = paramType
        self.classDict = classDict

        self.allDicts = {}
        for dict in  [self.params, self.modelAttrs,  self.calc]:
            if dict:
                self.allDicts.update(dict)

        ##### Constraint list #################################

        constrList = []
        cutList = []
        polygCuts = []

        for attr in self.allDicts.keys():
            # for attr in self.allDicts[attrType].keys():
            if self.allDicts[attr]['Constraint']['Type'] == 'ParamMatch':
                constrList.append ( 'ParamMatch-' + attr  )
            elif self.allDicts[attr]['Constraint']['Type'] == 'CheckBounded':
                constrList.append ( 'CheckBounded-' + attr  )
            elif self.allDicts[attr]['Constraint']['Type'] in ['HardCutLess', 'HardCutMore']:
                cutList.append(attr)
            elif self.allDicts[attr]['Constraint']['Type']=='CombinedCut':
                cutList.append(attr)
                cutList.append(self.allDicts[attr]['Constraint']['ToCheck']['ToCheck'])
            elif self.allDicts[attr]['Constraint']['Type']=='PolygonCut':
                cutList.append(attr)
                polygCuts.append(attr)

        self.constrList = constrList
        self.cutList = cutList

        ############### Set up exclusion polygon if available ##############

        cutDict = {}
        try:
            for attrToCut in polygCuts:
                plotDataName = 'Configs/ExperimentalCuts/plotCut_'  + attrToCut + '.csv'

                polygonList = []
                with open(plotDataName, 'r') as fileIn:
                    csvReader = csv.reader(fileIn)

                    for rawRow in csvReader:
                        xCoord, yCoord = float(rawRow[0]), float(rawRow[1])
                        polygonList.append( (xCoord, yCoord) )

                cutDict.update( {attrToCut : Polygon( polygonList )} )
        except:
            pass
        #######################################################################################
        self.polygCuts = cutDict


        if (writeToLogFile == True):
            writeToLogFile_InitModel(self)
        printCentered( ' ✔ Done Initialising Model', fillerChar = '█', color = Fore.GREEN )

    def loadResults(self, nbOfPoints='All', targetDir = 'Dicts/', specFile = ''):
        '''
            Loads all the json result dictionaries as a full dictionary.

            Attributes:

            Returns:
            - dict              ::          phaseSpaceDict dictionary with all the points contained in all the json files.
        '''
        ### Load all Jsons in Dicts/ dir.
        phaseSpaceDict = {}
        printCentered(' Looking in dir '+ targetDir +' ', fillerChar='▀')

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
                        printCentered(' Opening ' + jsonDict+ ' ', fillerChar='-')
                        phaseSpaceDict = {**phaseSpaceDict, **tempDict}
                    except Exception as e:
                        print(e)
                        printCentered('❎ Cannot open ' + jsonDict, color=Fore.RED, fillerChar='-')

        print()
        ########## COMEBACK #######
        ### Integrity check , excludes all points that have None as an attribute
        pointsToRemove = []
        for point in phaseSpaceDict.keys():
            for attribute  in self.allDicts.keys():

                # print(self.)
                # for attribute in self.allDicts[attributeType].keys():

                #### Check if the point in question hass all the attributes specified by the model
                if attribute not in phaseSpaceDict[point].keys() :
                    pointsToRemove.append (point)

                #### if it has all the attributes then check if they are non empty
                elif phaseSpaceDict[point][attribute] == None  and attribute not in self.noneAttr :
                # attribute!='ChiSquared'
                    # print(attribute)
                    pointsToRemove.append (point)

        # exit()
        for point in pointsToRemove:
            del phaseSpaceDict[point]

        # print( len(phaseSpaceDict) )
        #### Return all or a number of points chosen at random.
        if nbOfPoints=='All':
            return phaseSpaceDict
        elif type(nbOfPoints) == int:
            # listOfPointIDs = list (phaseSpaceDict.keys()) [0:nbOfPoints]
            keyList = list (phaseSpaceDict.keys())
            listOfPointIDs =[  random.choice( keyList ) for i in range(nbOfPoints)]

            return {k:phaseSpaceDict[k] for k in set(phaseSpaceDict).intersection(listOfPointIDs)}

    def _mThreadAUXexplore(self, q , threadNumber = "0", debug = False, newParamBounds = {} ): #<----- Needs documentation!!!
        '''
            Auxiliary function needed for multithreading, which generates valid points in the phase space along with getting the required attributes and putting them in a dictionary, via a Queue().

            Will use the generating engine specified to produce the points. Requires engine have the following methods:
                †)  _genValidPoint          ::          Method should generate a valid phaseSpaceDictOut given paramsDictMinMax.
                †)  _getRequiredAttributes  ::          Method that gets the required attributes from the out given by _genValidPoint.
                †)  _check0Mass             ::          Consistency check on phaseSpaceDict.
                †)  _clean                  ::          Cleaning file method.

            Arguments:
                - q                     ::          Multiprocessing Queue() object which takes the results from all
                                                    the child processes and then passes them to the main function
                - threadNumber          ::          DEFAULT:'0' .  To be used in multiprocessing to identify what thread is being used.
                - debug                 ::          DEFAULT = False. Set to True to get error messages and a Spectrum. file when running points.
                - newParamBounds        ::      DEFAULT: {}. new bounds to be used if the user wants to target a spcific hypervolume in the phase space.


            Return:
                - Queue : [phaseSpaceDict]
                - Return : None

                Puts the valid phase space dictionary in a que that is used later for multithreading, but returns None

        '''


        generatingEngine = self.engineClass(self)

        # generatingEngine = self.engineClass(self.modelName, self.case)


        if bool(newParamBounds) == True:
            paramsDictMinMax = newParamBounds
        else:
            paramsDictMinMax = self.paramBounds

        smartRndGen = smartRand(paramsDictMinMax, self.condDict, self.rndDict, self.toSetDict)
        while True:

            try:

                # genValidPointOutDict = generatingEngine._genValidPoint(paramsDictMinMax, threadNumber = threadNumber, debug = debug)

                newParamsDict = smartRndGen.genSmartRnd( debug = debug)


                genValidPointOutDict = generatingEngine.runPoint( newParamsDict, threadNumber = threadNumber , debug = debug)

                phaseSpaceDict_int = generatingEngine._getRequiredAttributes(newParamsDict, threadNumber)



                phaseSpaceDict = self._getCalcAttribForDict( phaseSpaceDict_int )
                massTruth = generatingEngine._check0Mass( phaseSpaceDict )


                if  massTruth == False:
                    generatingEngine._clean( threadNumber )
                    continue

                else:
                    # pp(phaseSpaceDict)
                    generatingEngine._clean( threadNumber )
                    pass

            except Exception as e:

                print(e)
                raise


                generatingEngine._clean( threadNumber )
                continue


            q.put(phaseSpaceDict)

        return None

    def runMultiThreadExplore(self, numberOfPoints = 10, nbOfThreads = 1, debug = False, quitTime = 50000, newParamBounds = {}, runComment = ''):
        '''
            Multiprocessing Exploration Scan, main parent function to a number of _mThreadAUXexplore to get all the points and store them in a proper phaseSpaceDict.

            Arguments:
                - numberOfPoints        ::      DEFAULT:10 ; Number of Points intended for the scan to collect
                - nbOfThreads           ::      DEFAULT: 1 ; Number of child processes to be started and ran.
                - debug                 ::      DEFAULT: False ; Set to True to print out error messages & Spectrum. files
                - quitTime              ::      DEFAULT: 300; If after quitTime secconds the scan can't find one point that produces EWSB it exits and prints out an error message.
                - newParamBounds        ::      DEFAULT: {}. new bounds to be used if the user wants to target a spcific hypervolume in the phase space.

                Returns:
                    - None.
                    Writes a ScanResults.xxxxxxx.json file with the complete phaseSpaceDict in the Results/modelName/Dicts/ directory:

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
        processes = [Process(target=self._mThreadAUXexplore , args=(localQue, str(x), debug, newParamBounds)) for x in range(nbOfThreads)]

        resultDict = {};
        for proc in processes:
            proc.start()

        abandonScan = False
        spinner = Halo(text='Trying to find a valid point in phase space. Will timeout after ' + Fore.RED +  str(quitTime) + ' s' + Style.RESET_ALL, spinner='dots')
        spinner.start()

        try:
            result = localQue.get(block=True, timeout=quitTime)
        except :
            spinner.stop_and_persist(symbol=Fore.RED+'\u2718' + Style.RESET_ALL,
                                     text = 'Cannot find valid point in phase space.')
            errorMsg ='\n'+ Fore.RED + "Timeout Reached." + Fore.GREEN + " Model with specified rules cannot produce valid points in phase space. " + Style.RESET_ALL
            print (errorMsg)

            for proc in processes:
                proc.terminate()
            abandonScan = True


        if abandonScan == False:

            spinner.stop_and_persist(symbol = Fore.GREEN+'\u2713'+ Style.RESET_ALL,
                                     text ='Model can produce points in phase space. Starting scan for ' + Fore.RED + self.modelName + '-' + self.case + Style.RESET_ALL)

            pointHandle = 0

            scanID = self.modelName + '_' + self.case.replace(" ","") +'_' + strftime("%d-%m-%-Y_%H:%M:%S", gmtime())

            resultsDirDicts = self.resultDir + 'Dicts/'
            subprocess.call('mkdir ' + resultsDirDicts, shell = True, stdout=FNULL, stderr=subprocess.STDOUT)

            writeToLogFile_Action(self, 'Started', 'Explore')
            printHeader('Explore', 'Started', nbOfThreads)
            pbar = tqdm(total=numberOfPoints, bar_format='%s{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]' % Fore.GREEN )


            while pointHandle < numberOfPoints:

                result = localQue.get()
                resultDict.update(result)
                pbar.update(1)

                #### Update the Json file every 10 pointsself.
                if True:#pointHandle % 10 == 0:
                    with open(resultsDirDicts +'ScanResults.' + scanID + '.json', 'w') as outfile:
                        json.dump(resultDict, outfile)

                pointHandle += 1

            pbar.close()
            for proc in processes:
                proc.terminate()

            printHeader('Explore', 'Finished', nbOfThreads )
            print (Style.RESET_ALL)


            writeToLogFile_Action(self, 'Finished', 'Explore')
            # mergeAllResDicts(self)


        spinnerWait = Halo(text = 'Waiting for everything to finish running.', spinner='dots')
        spinnerWait.start()
        time.sleep(1)

        self.cleanRun( nbOfThreads )
        spinnerWait.stop_and_persist(symbol = Fore.GREEN + '✔' + Style.RESET_ALL, text = 'Done cleaning.')



        return resultDict

    def cleanRun(self, nbOfThreads):
        '''
            Cleaning method used to clean all the possible remnants of the threads.

            Arguments:
            -   nbOfThreads     ::      Total number of threads over which it should clean

            Return:
            -   None
        '''
        generatingEngine = self.engineClass( self )

        for threadNumber in range(nbOfThreads):
            generatingEngine._clean( threadNumber )

        return None

    #####################  Evaluations ##############################################
    def _getCalcAttribForDict(self, phaseSpaceDict,  exportJson = False):
        '''
        Given a phaseSpaceDict, for each point in the phase space,  the function will go through the calcDict specified in the configFile, and calculate the specified attributes.

        Arguments:
            - phaseSpaceDict            ::      Phase space dictionary containing a numbe of points.
            - disableExternal           ::      DEFAULT: False. Set to True to enable external dependency calculations.
            - exportJson                ::      DEFAULT: False. Set to True to export to json , the new phaseSpaceDict with the calculated
                                                attributes.
        Returns:
            - phaseSpaceDict            with the new calculated attributes.
        '''


        for point in phaseSpaceDict.keys():
            for calcParam in self.calc.keys():


                ############## Possible BADNESS = 10000 ±!!!!!
                if calcParam not in phaseSpaceDict[point].keys():
                    phaseSpaceDict[point][calcParam] = None


                if ( phaseSpaceDict[point][calcParam] == None ):


                    ############## InternalCalc ################################
                    if self.calc[calcParam]['Calc']['Type'] == 'InternalCalc':
                        for paramToUse in self.calc[calcParam]['Calc']['ToCalc']['ParamList']:
                            exec(paramToUse + '=' +
                                 str(phaseSpaceDict[point][paramToUse]))

                        calcParamVal = eval( self.calc[calcParam]['Calc']['ToCalc']['Expression'])

                        phaseSpaceDict[point][calcParam] = calcParamVal

                    ############## External ################################
                    if self.calc[calcParam]['Calc']['Type'] == 'ExternalCalc' :

                        routineStr = 'Routines.' + self.calc[calcParam]['Calc']['Routine']
                        methodStr = self.calc[calcParam]['Calc']['Method']

                        routineModule = importlib.import_module(routineStr)

                        paramListStr = ''
                        for paramToUse in self.calc[calcParam]['Calc']['ParamList']:
                            exec(paramToUse + '=' +
                                 str(phaseSpaceDict[point][paramToUse]))
                            paramListStr = paramListStr + paramToUse + ','




                        routineCmd = 'routineModule.' + methodStr + '('+ paramListStr[:-1]  +')'
                        exec( calcParam + '_Aux =' + routineCmd)
                        phaseSpaceDict[point][calcParam] = eval( calcParam + '_Aux')

                        # pp(phaseSpaceDict[point])



        if exportJson == True:

            spinner = Halo(text='Writing to JSON.', spinner='dots')
            spinner.start()
            scanID = self.modelName + self.case.replace(" ","") +'_wPM_wCalc' + strftime("-%d%m%Y%H%M%S", gmtime())

            # Remove old jsonDicts
            subprocess.call('rm ' + self.resultDir + 'Dicts/*', shell=True)
            # Write to new jsonDict
            with open(self.resultDir + 'Dicts/' + scanID + '.json', 'w') as outFile:
                json.dump(phaseSpaceDict, outFile)

            spinner.stop_and_persist({'symbol':Fore.GREEN+'✓' + Style.RESET_ALL, 'text':'Finished writing to Json'})

        return phaseSpaceDict

    def getTopNChiSquaredPoints(self, phaseSpaceDict, countChi2, minimisationConstr ='Global', specificCuts = 'Global', ignoreConstrList = [], returnDict = False, exportAsDict = False, sortByChiSquare = True):
        '''
            Given a phase Space dictionary, and a the top number of points to be ranked via their chi2 value, the function returns the sorted list of chi2 . Can be toggled to return the dictionary, or return the countChi2 random number of points.
        '''

        chiSquareDict = {}
        modelConstr = constrEval( self )


        for pointKey in phaseSpaceDict.keys():


            notemptyDict = True
            for modelAttribute in self.allDicts.keys():
                if modelAttribute not in self.noneAttr:
                    notemptyDict = notemptyDict and bool(phaseSpaceDict[pointKey][modelAttribute])

            #### Not entirely sure about the checkHardCut if it should or shouldn't be in here.
            if notemptyDict == True and modelConstr._checkHardCut(phaseSpaceDict[pointKey], specificCuts = specificCuts):


                chiSquare = modelConstr.getChi2(phaseSpaceDict[pointKey], ignoreConstrList = ignoreConstrList,
                                    minimisationConstr = minimisationConstr, returnDict = False)
                chiSquareDict[pointKey] = chiSquare



        if sortByChiSquare == True:
            sortedChiSquare_ListOfTuples = sorted(chiSquareDict.items(), key=lambda kv: kv[1])
        else:
            sortedChiSquare_ListOfTuples = [ (pointKey, chiSquareDict[pointKey]) for pointKey in chiSquareDict.keys()   ]

        # pp(sortedChiSquare_ListOfTuples)
        # print(delimitator)
        # pp(constrAux)
        #
        # exit()



        if exportAsDict == False:
            topChi2List = []
            for pointAttr in sortedChiSquare_ListOfTuples[0:countChi2]:
                pointKey = pointAttr[0]
                topChi2List.append( { pointKey : phaseSpaceDict[ pointKey ] })
        else:
            topChi2List = {}
            for pointAttr in sortedChiSquare_ListOfTuples[0:countChi2]:
                pointKey = pointAttr[0]
                topChi2List.update( { pointKey : phaseSpaceDict[ pointKey ] })

        return topChi2List, sortedChiSquare_ListOfTuples[0:countChi2]

    def _restrictInterestingPoints(self, phaseSpaceDict, restrictingParam, restrictingParamMin, restrictingParamMax):
        '''
            Restricts phaseSpaceDict to a subregion specified by restrictingParam, and the bounds [restrictingParamMin, restrictingParamMax].

            Arguments:
                - listOfInteresingPoints                    ::          List of interesting points from getInterstingPoints.
                - restrictingParam                          ::          Attribute to restrict.
                - restrictingParamMin, restrictingParamMax  ::          Bounds for the restriction.

            Returns:
                - vettedList :
                List of the points that are within the subregion.
        '''
        vettedDict = {}
        modelConstr = constrEval( self )

        # paramType  = self.classification[restrictingParam]

        for phaseSpacePointDict in phaseSpaceDict.items():

            pointAttr = phaseSpacePointDict[1]
            pointKey = phaseSpacePointDict[0]

            if restrictingParam == 'ChiSquared':
                toVet = modelConstr.getChi2( pointAttr )

            else:
                toVet = pointAttr[restrictingParam]

            ### Vetting procedure ####
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
            The function will return the points in the phaseSpaceDict that lie within ALL the specified bounds in the cutDict
        '''
        for attrToCut in cutDict.keys():

            vettedDict = self._restrictInterestingPoints(phaseSpaceDict, attrToCut, cutDict[attrToCut]['Min'],  cutDict[attrToCut]['Max'])

            phaseSpaceDict = vettedDict

        return phaseSpaceDict

    def runGenerationMultithread(self, phaseSpaceDict, numberOfPoints = 16, numbOfCores = 1, minimisationConstr = 'Global', ignoreConstrList = [], timeOut = 120, noOfSigmasB = 1, noOfSigmasPM = 1, debug= False,  chi2LowerBound = 1.0,  sortByChiSquare = True, overSSH=False, algorithm = 'diffEvol'):
        '''
            Given a phaseSpaceDict of points the function will multiprocess on numberOfCores a certain number of numberOfPoints, either randomly selected , or selected by their chi2 Value. The specified algorithm will produce a generational evolution.
        '''

        # if sortByChiSquare == False:
        #     numberOfPoints = len( list( phaseSpaceDict.keys() ) )
        #
        #
        # bestChiSquares, sortedChiSquare_ListOfTuples = self.getTopNChiSquaredPoints(phaseSpaceDict, numberOfPoints, sortByChiSquare = sortByChiSquare )
        #
        # listOfchi2Lists = chunkList(bestChiSquares, numbOfCores)
        # listOfsortedChi2Lists= chunkList(sortedChiSquare_ListOfTuples, numbOfCores)
        configString = 'Utils.multiThreadAlg'

        try:
            algModule = importlib.import_module(configString)
        except Exception as e:
            print(e)

        from Utils.multiThreadAlg import exec(algorithm)
        exit()


        localQue = Queue()
        processes = { 'Proc::'+str(x+1) : Process(target = self._walkAroundListOfPoints_Gamma ,
                                                args=(localQue, listOfchi2Lists[x],
                                                listOfsortedChi2Lists[x], str(x), minimisationConstr, timeOut,  ignoreConstrList, noOfSigmasB, noOfSigmasPM, debug, numberOfPoints, chi2LowerBound )
                                                )
                    for x in range(numbOfCores) }


        ######################## Printing info and generating Scan ID ########################
        scanID = self.modelName + self.case.replace(" ","") + strftime("-%d-%m-%Y_%H_%M_%S", gmtime())
        resultsDirDicts = self.resultDir + 'Dicts/Focus' + strftime("_%d_%m_%Y/", gmtime())
        subprocess.call('mkdir ' + resultsDirDicts, shell = True, stdout=FNULL, stderr=subprocess.STDOUT)
        print(delimitator)



        resultDict = {}
        for procKey in processes.keys():
            processes[procKey].start()

        spinner = Halo(text='Started ' + Fore.RED +strftime("%d/%m/%Y at %H:%M:%S ", gmtime()) + Style.RESET_ALL +'Running on '+ Fore.RED + str(len(processes.keys())) + ' thread/s.'  + Style.RESET_ALL, spinner='dots')
        spinner.start()

        try:
            while True:
                continue
        except KeyboardInterrupt:
            print('Process killed by user')

        ############ Terminate the processes #############
        for procKey in processes.keys():
            processes[procKey].terminate()
        spinner.stop()


        self.cleanRun( numbOfCores )
        fixJsonWAppend(resultsDirDicts)

        print(Fore.GREEN + delimitator + Style.RESET_ALL)

        return resultDict


if __name__ == '__main__':

    modelName = 'testEngine'
    auxCase ='DummyCase'
    micrOmegasName = modelName


    newModel = phaseScannerModel( modelName, auxCase , micrOmegasName= micrOmegasName, writeToLogFile =True)
    # modelConstr = constrEval( newModel )

    psDict = newModel.loadResults( )
    newModel.runGenerationMultithread(psDict)
