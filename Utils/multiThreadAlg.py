'''
    Has algorithms for days
'''
from time import gmtime, strftime
import time
import numpy as np
import random
from random import randint
import json

from pprint import pprint as pp

from Utils.constrEval import *
from Utils.printUtils import *
from Utils.SmartRandomGenerator.smartRand import *


def makeRegistrar():
    '''
        Decorator function definition.
    '''
    registry = {}

    def registrar(func):
        registry[func.__name__] = func
        return func  # normally a decorator returns a wrapped function,
                     # but here we return func unmodified, after registering it
    registrar.all = registry
    return registrar


regAlg = makeRegistrar()


# DOC NEEDED
def formatTopChi2List_asGen0(topChi2List, sortedChiSquare_ListOfTuples, statistic='Chi2', Auxiliaries={}):
    '''
    '''
    pointTree = {}

    for pointNb, pointDict in enumerate(topChi2List):

        pointKey = list(pointDict.keys())[0]
        newKey = 'G0-P' + str(pointNb)

        pointTree[newKey] = {}
        # pp(pointDict[pointKey])
        auxDict = { pointKey: { auxKey: pointDict[pointKey][auxKey] for auxKey in pointDict[pointKey].keys() }}



        # pp(pointDict[pointKey])
        # pp(auxDict)

        # pp(pointTree[newKey]['FullDescription'])
        pointTree[newKey] = pointDict[pointKey]
        pointTree[newKey][statistic] = sortedChiSquare_ListOfTuples[pointNb][1]
        pointTree[newKey]['Parent'] = None
        pointTree[newKey]['Children'] = []

        pointTree[newKey]['FullDescription'] =  auxDict
        pointTree[newKey]['Aux'] = Auxiliaries
        # pp(pointTree[newKey])

        # pp(pointTree[newKey])
        # pp(pointTree[newKey])
        # pointTree[newKey]['OrigKey'] = pointKey

    return pointTree
def makeBranch( pointDict, newChi2 , parentID, pointID , Auxiliaries={}):
    '''
        E.g.   add Generation-2
    '''
    pointKey = list( pointDict.keys() ) [0]
    pointBranch = {}
    pointBranch[pointID] = {}

    pointBranch[pointID] .update( pointDict[pointKey] )
    pointBranch[pointID] .update( {'Chi2' : newChi2})
    pointBranch[pointID] .update( {'Children' : [] } )
    pointBranch[pointID] .update( {'Parent' : parentID } )
    pointBranch[pointID] .update( {'FullDescription' : pointDict } )
    pointBranch[pointID] .update( {'Aux' : Auxiliaries } )


    # pp (pointBranch)


    return pointBranch

class minimAlg:
    '''
    '''
    def __init__(self, psObject, q, bestChiSquares, sortedChiSquare_ListOfTuples,  threadNumber = '0', minimisationConstr='Global', timeOut = 120, ignoreConstrList = [], noOfSigmasB = 1, noOfSigmasPM = 1, debug= False,  chi2LowerBound = 1.0):
        '''
        '''
        self.psObject = psObject

        self.modelConstr = constrEval(self.psObject)
        self.generatingEngine = psObject.engineClass()

        self.Que = q
        self.bestChiSquares = bestChiSquares
        self.sortedChiSquare_ListOfTuples = sortedChiSquare_ListOfTuples
        self.threadNumber = threadNumber
        self.minimisationConstr = minimisationConstr
        self.timeOut = timeOut
        self.ignoreConstrList = ignoreConstrList
        self.noOfSigmasB = noOfSigmasB
        self.noOfSigmasPM = noOfSigmasPM
        self.debug = debug
        self.chi2LowerBound = chi2LowerBound

        return None

    @regAlg
    def diffEvol(self):
        '''
                Differential evolution algorithm works as per Storn and Price [see Good Parameters for Differential
            Evolution By Magnus Erik Hvass Pedersen for appropriate F_factor, CR_factor selection]
        '''

        modelConstr = constrEval(self.psObject)
        pointTree = formatTopChi2List_asGen0(self.bestChiSquares, self.sortedChiSquare_ListOfTuples)

        alphaParents = list(pointTree.keys())
        scanIDwThread = (self.psObject.modelName + self.psObject.case.replace(" ", "")
                         + strftime("-%d-%m-%Y_%H_%M_%S", gmtime()) + '_ThreadNb' + self.threadNumber)

        resultsDirDicts = self.psObject.resultDir + 'Dicts/Focus' + strftime("_%d_%m_%Y/", gmtime())

        # print(delimitator)
        resultDict_Thread = {}

        # chi2Min = sortedChiSquare_ListOfTuples[0][1]
        # pp(sortedChiSquare_ListOfTuples[0])
        # 'chi2Min': min( newListOfChi2 ),
        # 'chi2Mean' : np.mean( newListOfChi2),
        # 'chi2Std' : np.std( newListOfChi2)
        chi2Vals = [chi2Tuple[1] for chi2Tuple in self.sortedChiSquare_ListOfTuples]
        listOfChi2StatDicts = [{'chi2Min': min(chi2Vals),
                                'chi2Mean': np.mean(chi2Vals),
                                'chi2Std': np.std(chi2Vals)
                                }]

        listOfBestChi2 = [sorted(self.sortedChiSquare_ListOfTuples, key=lambda tup: tup[1])[0][1]]
        # ###  Pick target vector at rndom / as lowestchi2? ####
        F_factor = 0.66
        CR_factor = 0.236

        # F_factor = 0.5
        # CR_factor = 0.1

        generatingEngine = self.psObject.engineClass()

        # ### Initialisation stage ####
        genPopSize = len(alphaParents)
        genNb = 0
        changeNb = 0

        while True:

            newParents = []
            pointCount = 0

            # ### Populating the new generation. Stop when we have the same number of parents in the new one.
            while len(newParents) < genPopSize:

                for targetKey in alphaParents:
                    # Pick out 4 points in phase space and assign one of them as the target.
                    rndKeyChoice = random.sample(alphaParents, 3)
                    targetChi2 = pointTree[targetKey]['Chi2']

                    # ### Mutation stage ####
                    # Create a donnor vector out of the parameters of the 3 others via the formula below.
                    donorDict = {}
                    for modelParam in self.psObject.params.keys():
                        xr1_Comp = pointTree[rndKeyChoice[0]][modelParam]
                        xr2_Comp = pointTree[rndKeyChoice[1]][modelParam]
                        xr3_Comp = pointTree[rndKeyChoice[2]][modelParam]

                        donorDict[modelParam] = xr1_Comp + F_factor * (xr2_Comp - xr3_Comp)

                    # ### Recombination stage ####
                    # Make a new hybrid vector
                    mutatedDict = {}
                    rndParamChoice = random.choice(list(self.psObject.params.keys()))
                    for modelParam in self.psObject.params.keys():

                        if random.uniform(0, 1) <= CR_factor or modelParam == rndParamChoice:
                            mutatedDict[modelParam] = donorDict[modelParam]
                        else:
                            mutatedDict[modelParam] = pointTree[targetKey][modelParam]

                    # ########## Selection stage ############
                    massTruth, newPointWithAttr = self.psObject.engineProcedure(generatingEngine, mutatedDict,
                                                                                threadNumber=self.threadNumber,
                                                                                debug=self.debug)

                    if massTruth is True:

                        newPointKey = list(newPointWithAttr.keys())[0]
                        newChiSquared = modelConstr.getChi2(newPointWithAttr[newPointKey],
                                                            ignoreConstrList=self.ignoreConstrList,
                                                            minimisationConstr=self.minimisationConstr,
                                                            returnDict=False)
                    else:
                        newChiSquared = targetChi2 + 1

                    # ## New point evaluation. If the new point has a lower test statistic than it's target, then add
                    # it to the new generation
                    if newChiSquared < targetChi2:

                        oldID = list(newPointWithAttr.keys())[0]
                        pointGenID = oldID + '-GenNb' + str(genNb)

                        toAddDict = {}
                        toAddDict[pointGenID] = newPointWithAttr[oldID]
                        toAddChi2 = newChiSquared

                        self.Que.put({'NewPoint': {'Dict': toAddDict,
                                                   'ThreadNb': int(self.threadNumber)+1}})

                    # Otherwise propagate the target point to the new generation
                    else:
                        toAddDict = pointTree[targetKey]['FullDescription']
                        toAddChi2 = targetChi2

                    generatingEngine._clean(self.threadNumber)
                    # ## Add to the new generation
                    pointCount += 1

                    parentID = targetKey
                    childID = 'G' + str(genNb + 1) + '-P' + str(pointCount)
                    pointTree.update(makeBranch(toAddDict, toAddChi2, parentID, childID))

                    pointTree[parentID]['Children'].append(childID)
                    newParents.append(childID)

            # ### Move on to the new generation ####
            alphaParents = newParents
            genNb += 1

            # #### Getting the smallest Chi2 and sending it to the plotting function ####
            chi2Min = pointTree[alphaParents[0]]['Chi2']

            newListOfChi2 = []
            for newParent in alphaParents:
                newListOfChi2.append(pointTree[newParent]['Chi2'])

            chi2Min, chi2Mean, chi2Std = min(newListOfChi2), np.mean(newListOfChi2), np.std(newListOfChi2)

            newChi2Dict = {'chi2Min': chi2Min, 'chi2Mean': chi2Mean, 'chi2Std': chi2Std, 'chi2List': newListOfChi2}

            # ############ Printing section ###########
            quePut = False

            if chi2Min < listOfBestChi2[-1]:
                printStr = 'Minimum Decrease of'
                percChange = round((chi2Min - listOfBestChi2[-1]) / listOfBestChi2[-1], 4) * 100
                quePut = True
                changeNb += 1

                printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)

            elif chi2Mean < listOfChi2StatDicts[-1]['chi2Mean']:
                printStr = 'Distribution Mean Decrease of'
                percChange = round((chi2Mean - listOfChi2StatDicts[-1]['chi2Mean'])
                                   / listOfChi2StatDicts[-1]['chi2Mean'], 4) * 100

                quePut = True
                changeNb += 1
                printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)

            # Put in the que to export the Generational Statistics
            if quePut is True:
                genDict = {}
                auxList = [pointTree[parentID]['FullDescription'] for parentID in alphaParents]
                for membDict in auxList:
                    genDict.update(membDict)
                self.Que.put({'GenStat': {'GenNb': genNb,
                                          'ThreadNb': int(self.threadNumber)+1,
                                          'NewChi2': chi2Min,
                                          'OldChi2': listOfBestChi2[-1],
                                          'chi2Min': chi2Min,
                                          'chi2Mean': chi2Mean,
                                          'chi2Std': chi2Std,
                                          'GenDict': genDict}}
                             )

            listOfChi2StatDicts.append(newChi2Dict)
            listOfBestChi2.append(chi2Min)

            del listOfBestChi2[0]
            del listOfChi2StatDicts[0]

            # Send the termination message if we've gone past the minimum lowerbound, and terminate the Engine
            if chi2Min < self.chi2LowerBound:

                print(Fore.RED + delimitator + Style.RESET_ALL)
                printCentered('Hit χ² bound of '+str(self.chi2LowerBound) + '   :::   Killing Thread #'
                              + str(int(self.threadNumber)+1), color=Fore.RED)
                print(Fore.RED + delimitator + Style.RESET_ALL)

                generatingEngine._terminateSession()
                self.Que.put({'Terminate': int(self.threadNumber) + 1})
                break

        return None

    def _lookAroundPointForSmallerChi2 (self, phaseSpacePointDict, startTime, best_rSigma, debug = False):
        '''
            Given a point via phaseSpacePointDict, the function performs a random search in the hypercube defined by phaseSpacePointDict['Params'][param] ± sigmasDict[param] untill it finds a new point with a χ^2 smaller than the initial point. Requires a startTime to be externally monitored for timeOuts (recursive function calls itself).

            Arguments:
                - phaseSpacePointDict         ::      Dictionary of a point with the usual attributes: {'Params':{...}, 'Particles':{...}, 'Couplings': {...}}.
                - startTime                   ::      Time at which function is called (required outside).
                - threadNumber                ::      DEFAULT: '0'. Identifies process number.
                - minimisationConstr          ::      DEFAULT: 'Global' . By default function will find the global χ^2. Can be set to a list of a subset of constraints to find the combined χ^2.
                - timeOut                     ::      DEFAULT: 120. If after timeOut secconds the function hasn't found a new point with a smaller χ^2 then the function times out and returns None
                - noOfSigmasB                 ::       DEFAULT: 1 . Change this to relax number of sigmas for bounded params.
                - noOfSigmasPM                ::       DEFAULT: 1 . Change this to relax number of sigmas for parameter match.

            Return:
                - [newPointWithAttr, newPointConstraintDict, {'ChiSquared':newChiSquared}]    ::: IF IT HASN'T TIMED OUT.
                - None                                                                        ::: IF IT HAS TIMED OUT.

                A list with the newPoint with the required attributes, the new Point with attributes and constraints and the ChiSquared of the new point
        '''

        colorDict = {'0':Fore.RED, '1':Fore.GREEN, '2':Fore.YELLOW,  '3': Fore.BLUE , '4':Fore.MAGENTA}
        nbOfColors = len( list(colorDict.keys()) )

        generatingEngine = self.psObject.engineClass()
        smartRndGen = smartRand({}, self.psObject.condDict, self.psObject.rndDict, self.psObject.toSetDict)
        modelConstr = constrEval( self.psObject )


        ## TimeOut control
        if time.time() - startTime > self.timeOut:
            if debug:
                print (colorDict[ str(int(self.threadNumber) % nbOfColors) ] +
                        '-------------> ⏰ Timeout for thread Nb ' + self.threadNumber +' ⏰ <-------------' +
                        Style.RESET_ALL )

            return None


        pointKey = list(phaseSpacePointDict.keys())[0]
        # print(pointKey)
        # print(phaseSpacePointDict)
        chiSquareToMinimise = self.modelConstr.getChi2(phaseSpacePointDict[pointKey], ignoreConstrList = self.ignoreConstrList,
                                                        minimisationConstr = self.minimisationConstr, returnDict = False)

        # ### Ill defined original point
        # if chiSquareToMinimise == None:
        #     return None

        if self.debug:
            print(Fore.GREEN +'Χ^2 to  beat:  ' +  str(chiSquareToMinimise) + Style.RESET_ALL +' with ' + str(self.noOfSigmasB) + ' ,  ' +str(self.noOfSigmasPM) +  'σs \n')

        ### New point generation
        # generatingEngine = self.engineClass(self.modelName, self.case)

        while True:

            try:


                paramsDict = { modelAttr :phaseSpacePointDict[pointKey][modelAttr]   for modelAttr in self.psObject.params}
                newParamsDict = smartRndGen.genRandUniform_Rn( paramsDict , best_rSigma)
                ### Generate a point and extract its attributes

                # newParamsDict = generatingEngine._genPointAroundSeed(phaseSpacePointDict[pointKey]['Params'], best_rSigma, threadNumber = threadNumber, debug = debug)
                # newPointWithAttr = generatingEngine._getRequiredAttributes(newParamsDict, threadNumber)
                # massTruth = generatingEngine._check0Mass( newPointWithAttr )

                massTruth, newPointWithAttr = self.psObject.engineProcedure(generatingEngine, newParamsDict, threadNumber = self.threadNumber, debug = self.debug)

                # genValidPointOutDict = generatingEngine.runPoint( newParamsDict, threadNumber = self.threadNumber , debug = self.debug)
                # newPointWithAttr_int = generatingEngine._getRequiredAttributes(newParamsDict, self.threadNumber)
                # newPointWithAttr = self.psObject._getCalcAttribForDict(newPointWithAttr_int )
                # massTruth = generatingEngine._check0Mass( newPointWithAttr )

                if  massTruth == False:
                    ### Point has 0 masses clean and try again.
                    generatingEngine._clean( self.threadNumber)
                    continue
                else:

                    ### Escape condition when massTruth = True, move on to next stage.
                    generatingEngine._clean( self.threadNumber)
                    break

            except Exception as e:
                raise
                print(e)


                ### Ill defined point clean and try again.
                generatingEngine._clean( self.threadNumber)
                continue


        ### New point evaluation
        newPointKey = list(newPointWithAttr.keys())[0]
        newChiSquared = self.modelConstr.getChi2(newPointWithAttr[newPointKey], ignoreConstrList = self.ignoreConstrList,
                                    minimisationConstr = self.minimisationConstr, returnDict = False)

        # #### Returns none in case the new ChiSquared isn't defined.
        # if newChiSquared == None:
        #     return None

        if self.debug:
            if newChiSquared > chiSquareToMinimise:

                print(Fore.RED +'New Χ^2 of ' +  str(newChiSquared) + Style.RESET_ALL + '\n')
            else:
                print(Fore.BLUE + 'New Χ^2 of '  +str(newChiSquared) + Style.RESET_ALL + '\n')


        ### Check new point against old
        if newChiSquared > chiSquareToMinimise:
            return self._lookAroundPointForSmallerChi2(phaseSpacePointDict, startTime, best_rSigma, debug = debug)
        else:
            return {'NewPointDict': newPointWithAttr, 'ChiSquared':newChiSquared}

    def _findBest_rSigma(self, phaseSpacePointDict, testStat='ChiSquared', percGoal=0.01, nbOfTests=10, init_rSigma=3.0,
                         redFact=1.71828182846, maxGoal=1.0):
        '''
            Auxiliary algorithm to determine the best value for r_Sigma based on a percentage change of a test statistic
        '''
        # ### Check if we've already done this before
        try:
            with open('Configs/best_rSigma/' + self.psObject.name + '.json', 'r') as jsonIn:
                rSigmaDict_Test = json.load(jsonIn)
            # ##### Return slightly differenct ones
            return rSigmaDict_Test['best_rSigma'] , rSigmaDict_Test['max_rSigma']
        except:

            print(delimitator2,'No rSigma detected, running rSigma procedure for ThreadNb ', self.threadNumber, delimitator2)
            pass



        generatingEngine = self.psObject.engineClass()
        smartRndGen = smartRand({}, self.psObject.condDict, self.psObject.rndDict, self.psObject.toSetDict)
        modelConstr = constrEval( self.psObject )



        pointKey = list(phaseSpacePointDict.keys())[0]
        paramsDict = { modelAttr :phaseSpacePointDict[pointKey][modelAttr]   for modelAttr in self.psObject.params}

        good_rSigma = False
        foundMax = False
        best_rSigma = init_rSigma

        while good_rSigma == False:
            testCount = nbOfTests
            testStatSum = 0

            while testCount > 0:

                try:


                    # paramsDict = { modelAttr :phaseSpacePointDict[pointKey][modelAttr]   for modelAttr in self.psObject.params}

                    newParamsDict = smartRndGen.genRandUniform_Rn( paramsDict , best_rSigma)
                    ### Generate a point and extract its attributes
                    massTruth, newPointWithAttr = self.psObject.engineProcedure(generatingEngine, newParamsDict, threadNumber = self.threadNumber, debug = self.debug)
                    # genValidPointOutDict = generatingEngine.runPoint( newParamsDict, threadNumber = self.threadNumber , debug = self.debug)
                    # newPointWithAttr_int = generatingEngine._getRequiredAttributes(newParamsDict, self.threadNumber)
                    # newPointWithAttr = self.psObject._getCalcAttribForDict(newPointWithAttr_int )
                    # massTruth = generatingEngine._check0Mass( newPointWithAttr )

                    if  massTruth == False:
                        ### Point has 0 masses clean and try again.
                        generatingEngine._clean( self.threadNumber)
                        continue
                    else:

                        ### Escape condition when massTruth = True, move on to next stage.
                        generatingEngine._clean( self.threadNumber)

                        ### New point evaluation
                        newPointKey = list(newPointWithAttr.keys())[0]
                        if testStat == 'ChiSquared':
                            newChiSquared = self.modelConstr.getChi2(newPointWithAttr[newPointKey], ignoreConstrList = self.ignoreConstrList,
                                                        minimisationConstr = self.minimisationConstr, returnDict = False)
                        elif testStat == 'LogL':
                            newChiSquared = self.modelConstr.getLogLikelihood( newPointWithAttr[newPointKey] )

                        newPointWithAttr[newPointKey][testStat] = newChiSquared

                        # pp(newPointWithAttr[newPointKey]['ChiSquared'])
                        # pp(phaseSpacePointDict[pointKey]['ChiSquared'])

                        # print(delimitator2)

                        testCount += (-1)

                        testStatSum += abs(newPointWithAttr[newPointKey][testStat] - phaseSpacePointDict[pointKey][testStat]) / abs(phaseSpacePointDict[pointKey][testStat])


                        # print(testStatSum / (nbOfTests - testCount))
                        # break

                except Exception as e:
                    raise
                    print(e)


                    ### Ill defined point clean and try again.
                    generatingEngine._clean( self.threadNumber)
                    continue





            if (testStatSum / nbOfTests) > percGoal:
                best_rSigma = best_rSigma / redFact
                print(delimitator2)
                print('New best rSigma ', best_rSigma)

            else :
                good_rSigma = True

            if (testStatSum / nbOfTests) < maxGoal and not foundMax:
                max_rSigma = best_rSigma
                foundMax = True

        print(delimitator)
        print(Fore.GREEN +  'Best rSigma  with ',best_rSigma, Style.RESET_ALL)
        print(Fore.YELLOW +  'rSigma cutoff with ', max_rSigma, Style.RESET_ALL)
        print(delimitator)

        # subprocess.call('mkdir Configs/best_rSigma/', shell = True, )
        with open('Configs/best_rSigma/' + self.psObject.name + '.json', 'w') as jsonOut:
            json.dump({'best_rSigma': best_rSigma, 'max_rSigma': max_rSigma}, jsonOut)

        return best_rSigma, max_rSigma

    @regAlg
    def singleCellEvol( self ) :
        '''
            Single cell evolution algorithm starts off with a point that mutates untill the stoping criterion is reached.
        '''

        #### Controlling factors ####
        chi2PercCut = 0.1
        genNbKill = 15

        amplificationFactor = 1.71828182846


        #### Initialisation stage ####
        pointTree =  formatTopChi2List_asGen0( self.bestChiSquares, self.sortedChiSquare_ListOfTuples )
        alphaParents = list (pointTree.keys() )
        chi2Min = self.sortedChiSquare_ListOfTuples[0][1]
        genNb = 0

        listOfBestChi2 = [chi2Min]

        #### Selecting the best value for rSigma
        # printCentered(' Finding Best r Sigma for ThreadNb ' + str(self.threadNumber) + ' ', color=Fore.GREEN, fillerChar='◉')

        auxPoint = deepcopy(pointTree['G0-P0']['FullDescription'])
        pointKey = list( pointTree['G0-P0']['FullDescription'].keys() )[0]
        auxPoint[pointKey]['ChiSquared'] = pointTree['G0-P0']['Chi2']

        best_rSigma , best_rSigmaCutoff = self._findBest_rSigma( auxPoint , redFact = amplificationFactor, percGoal = chi2PercCut / genNbKill)



        # best_rSigma = 0.0045
        # best_rSigmaCutoff = 0.006

        best_rSigmaInit = best_rSigma
        justKicked = False

        chi2MinDict = {'GenNb-0': {'BestChi2':chi2Min , 'rSigmaVal':best_rSigma} }

        # rSigmaDict = {'Current_rSigma': best_rSigma, 'LastBest_rSigma': best_rSigma}

        resetCount = 0
        while True:


            # Update the list?
            newParents = []
            pointCount = 0

            for parentID in alphaParents:

                pointNb = int(parentID.split('P')[1])
                startTime = time.time()

                # pp(bestChiSquares[pointNb])
                # pp(pointTree[parentID]['FullDescription'])
                # exit()
                newPointDict = self._lookAroundPointForSmallerChi2(
                                                            pointTree[parentID]['FullDescription'],
                                                            startTime, best_rSigma, debug = self.debug
                                                            )

                if newPointDict == None:
                    #### If we've timed out
                    if resetCount >= 2:
                        # if pointTree[parentID]['Parent'] != None:
                        newParents = [random.choice (list(pointTree.keys())[:-1])]
                        resetCount = 0
                            # newParents.append( pointTree[parentID]['Parent'] )
                        # else:
                        #     newParents.append(parentID)
                    else:
                        ######### COMEBACK
                        newParents.append(parentID)
                        best_rSigma = best_rSigmaInit
                        resetCount +=1

                    # continue

                elif newPointDict['ChiSquared'] < pointTree[parentID]['Chi2']:

                    # {'NewPointDict': newPointWithAttr, 'ChiSquared':newChiSquared}
                    pointCount += 1

                    newPointKey = list(newPointDict['NewPointDict'].keys())[0]
                    newParamsDict = newPointDict['NewPointDict']
                    newChi2 = newPointDict['ChiSquared']


                    childID = 'G' + str(genNb + 1) + '-P' + str(pointCount)
                    pointTree.update (makeBranch( newPointDict['NewPointDict'],
                                                    newChi2, parentID, childID))
                    pointTree[parentID]['Children'].append( childID )
                    newParents.append( childID )

                    # self.Que.put( newPointDict['NewPointDict'] )
                    self.Que.put( {'NewPoint' : {'Dict' : newPointDict['NewPointDict'],
                                                 'ThreadNb' : int(self.threadNumber)+1}} )



            alphaParents = newParents

            chi2Min = pointTree[alphaParents[0]]['Chi2']
            minKey = alphaParents[0]



            for  newParent in alphaParents:
                if pointTree[newParent]['Chi2'] < chi2Min:
                    chi2Min = pointTree[newParent]['Chi2']
                    minKey = newParent


            genNb += 1

            printStr = 'Minimum Decrease of '
            percChange = round ( (chi2Min - listOfBestChi2[-1]) / listOfBestChi2[-1], 4) * 100
            printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)


            chi2MinDict.update( {'GenNb-'+str(genNb) : {'BestChi2': chi2Min, 'rSigmaVal': best_rSigma}  } )
            # pp(chi2MinDict)


            newListOfChi2 = []
            for  newParent in alphaParents:
                newListOfChi2.append(pointTree[newParent]['Chi2'])

            chi2Min, chi2Mean , chi2Std=  min( newListOfChi2 ), np.mean( newListOfChi2), np.std( newListOfChi2)
            genDict = {}
            auxList = [ pointTree[parentID]['FullDescription'] for parentID in alphaParents]
            for membDict in auxList:
                genDict.update(membDict)

            self.Que.put( {'GenStat':{'GenNb': genNb,
                                    'ThreadNb': int(self.threadNumber)+1,
                                    'NewChi2': chi2Min,
                                    'OldChi2': listOfBestChi2[-1],
                                    'chi2Min': chi2Min,
                                    'chi2Mean': chi2Mean,
                                    'chi2Std': chi2Std,
                                    'GenDict' : genDict}}
                )

            # If after genNbKill generations the chi2 measure hasn't changed by more than chi2PercCut percent then we increase the best_rSigma for the thread by a factor of amplificationFactor.

            # amplificationFactor = 2.71828182846

            if genNb >= genNbKill:
                chi2ToCompare = chi2MinDict[ 'GenNb-' + str(genNb-genNbKill) ]['BestChi2']

                if ( (abs( chi2Min - chi2ToCompare )/ chi2ToCompare < chi2PercCut)
                    and (genNb % genNbKill == 0)
                     ):

                     if best_rSigma > best_rSigmaCutoff :
                         best_rSigma = best_rSigmaInit
                         resetCount +=1

                         if resetCount >=2:
                             alphaParents = [random.choice (list(pointTree.keys())[:-1])]
                             resetCount = 0
                             pp(alphaParents)
                         # exit()
                         print(Fore.GREEN + delimitator + Style.RESET_ALL)
                         printCentered('Reset rSigma value to ' + str(best_rSigma), color=Fore.GREEN)
                         print(Fore.GREEN + delimitator + Style.RESET_ALL)
                     else:


                         best_rSigma = best_rSigma * amplificationFactor
                         justKicked = True
                         print(Fore.YELLOW + delimitator + Style.RESET_ALL)
                         printCentered('NEW rSigma value of ' + str(best_rSigma), color=Fore.YELLOW)
                         print(Fore.YELLOW + delimitator + Style.RESET_ALL)

            ##At some point by increasing rSigma enough we'll effectivelly land on a new region (which we define by best_rSigmaCutoff * amplificationFactor due to the lack of a better solution) we reset the rSigma value back to its initial value and restart the process.

            # #### NEED TO ADD COONDITION TO SEE IF THE NEW KICK HAS PRODUCED A SMALLER CHI 2
            # if genNb == 5:
            # if best_rSigma > best_rSigmaCutoff * amplificationFactor:
            #     best_rSigma = best_rSigmaInit
            #
            #     alphaParents = [random.choice (list(pointTree.keys())[:-1])]
            #     # pp(alphaParents)
            #     # exit()
            #     print(Fore.GREEN + delimitator + Style.RESET_ALL)
            #     printCentered('Reset rSigma value to ' + str(best_rSigma), color=Fore.GREEN)
            #     print(Fore.GREEN + delimitator + Style.RESET_ALL)



            listOfBestChi2.append(chi2Min)
            del listOfBestChi2[0]
            if chi2Min < self.chi2LowerBound:
                # self.Que.put( int(self.threadNumber)+1 )
                self.Que.put( {'Terminate': int(self.threadNumber)+1 } )




        return None

    @regAlg
    def metropolisHastings( self ):
        '''
            aaaaas
        '''
        generatingEngine = self.psObject.engineClass()
        smartRndGen = smartRand({}, self.psObject.condDict, self.psObject.rndDict, self.psObject.toSetDict)
        modelConstr = constrEval( self.psObject )



        #### Controlling factors ####
        chi2PercCut = 0.1
        genNbKill = 10

        amplificationFactor = 1.71828182846


        #### Initialisation stage ####
        pointTree =  formatTopChi2List_asGen0( self.bestChiSquares, self.sortedChiSquare_ListOfTuples , 'LogL')
        alphaParents = list (pointTree.keys() )
        chi2Min = self.sortedChiSquare_ListOfTuples[0][1]
        genNb = 0

        listOfBestChi2 = [chi2Min]

        #### Selecting the best value for rSigma
        # printCentered(' Finding Best r Sigma for ThreadNb ' + str(self.threadNumber) + ' ', color=Fore.GREEN, fillerChar='◉')

        auxPoint = deepcopy(pointTree['G0-P0']['FullDescription'])
        pointKey = list( pointTree['G0-P0']['FullDescription'].keys() )[0]

        auxPoint[pointKey]['LogL'] = pointTree['G0-P0']['LogL']

        best_rSigma , best_rSigmaCutoff = self._findBest_rSigma( auxPoint , redFact = amplificationFactor, percGoal = chi2PercCut / genNbKill, testStat = 'LogL')

        # best_rSigma , best_rSigmaCutoff = 0.00778, 0.3441
        best_rSigmaInit = best_rSigma
        justKicked = False

        chi2MinDict = {'GenNb-0': {'BestChi2':chi2Min , 'rSigmaVal':best_rSigma} }

        # rSigmaDict = {'Current_rSigma': best_rSigma, 'LastBest_rSigma': best_rSigma}

        resetCount = 0
        while True:


            # Update the list?
            newParents = []
            pointCount = 0

            for parentID in alphaParents:

                pointNb = int(parentID.split('P')[1])
                startTime = time.time()

                # pp(bestChiSquares[pointNb])
                # pp(pointTree[parentID]['FullDescription'])
                # exit()


                # newPointDict = ...
                # newPointDictID =  ...
                while True:
                    try:

                        phaseSpacePointDict = pointTree[parentID]['FullDescription']
                        pointKey = list(  phaseSpacePointDict.keys() )[0]

                        paramsDict = { modelAttr :phaseSpacePointDict[pointKey][modelAttr]   for modelAttr in self.psObject.params}
                        newParamsDict = smartRndGen.genRandUniform_Rn( paramsDict , best_rSigma)
                        ### Generate a point and extract its attributes

                        massTruth, newPointDict = self.psObject.engineProcedure(generatingEngine, newParamsDict, threadNumber = self.threadNumber, debug = self.debug)

                        if  massTruth == False:
                            ### Point has 0 masses clean and try again.
                            generatingEngine._clean( self.threadNumber)
                            continue
                        else:

                            ### Escape condition when massTruth = True, move on to next stage.
                            generatingEngine._clean( self.threadNumber)
                            break

                    except Exception as e:
                        raise
                        print(e)
                ### Generate a point and extract its attributes

                newPointKey = list(newPointDict.keys())[0]
                newLogL = modelConstr.getLogLikelihood( newPointDict[newPointKey] )



                ##### Get new point

                if (    (newLogL > pointTree[parentID]['LogL']
                    or (newLogL /  pointTree[parentID]['LogL']) > random.uniform(0,1) )
                    # or (newLogL -  pointTree[parentID]['LogL']) > math.log( random.uniform(0,1) ))
                    and newLogL != math.inf
                    ):

                    # {'NewPointDict': newPointWithAttr, 'ChiSquared':newChiSquared}
                    pointCount += 1

                    # newParamsDict = paramsDict
                    newPointDict[newPointKey]['LogL'] = newLogL
                    newChi2 = newLogL
                else:

                    newChi2 = phaseSpacePointDict[pointKey]['LogL']
                    newPointDict = phaseSpacePointDict
                    newPointDict[pointKey]['LogL'] = pointTree[parentID]['LogL']


                childID = 'G' + str(genNb + 1) + '-P' + str(pointCount)
                pointTree.update (makeBranch( newPointDict,
                                                newChi2, parentID, childID))
                pointTree[parentID]['Children'].append( childID )

                newParents.append( childID )

                # self.Que.put( newPointDict['NewPointDict'] )
                self.Que.put( {'NewPoint' : {'Dict' : newPointDict,
                                             'ThreadNb' : int(self.threadNumber)+1}} )



            alphaParents = newParents

            chi2Min = pointTree[alphaParents[0]]['LogL']
            minKey = alphaParents[0]



            for  newParent in alphaParents:
                if pointTree[newParent]['LogL'] < chi2Min:
                    chi2Min = pointTree[newParent]['LogL']
                    minKey = newParent


            genNb += 1

            printStr = 'Minimum Decrease of '
            percChange = round ( (chi2Min - listOfBestChi2[-1]) / listOfBestChi2[-1], 4) * 100
            printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)


            chi2MinDict.update( {'GenNb-'+str(genNb) : {'BestChi2': chi2Min, 'rSigmaVal': best_rSigma}  } )
            # pp(chi2MinDict)


            newListOfChi2 = []
            for  newParent in alphaParents:
                newListOfChi2.append(pointTree[newParent]['LogL'])

            chi2Min, chi2Mean , chi2Std=  min( newListOfChi2 ), np.mean( newListOfChi2), np.std( newListOfChi2)
            genDict = {}
            auxList = [ pointTree[parentID]['FullDescription'] for parentID in alphaParents]
            for membDict in auxList:
                genDict.update(membDict)

            self.Que.put( {'GenStat':{'GenNb': genNb,
                                    'ThreadNb': int(self.threadNumber)+1,
                                    'NewChi2': chi2Min,
                                    'OldChi2': listOfBestChi2[-1],
                                    'chi2Min': chi2Min,
                                    'chi2Mean': chi2Mean,
                                    'chi2Std': chi2Std,
                                    'GenDict' : genDict}}
                )

            # If after genNbKill generations the chi2 measure hasn't changed by more than chi2PercCut percent then we increase the best_rSigma for the thread by a factor of amplificationFactor.

            # amplificationFactor = 2.71828182846

            if genNb >= genNbKill:
                chi2ToCompare = chi2MinDict[ 'GenNb-' + str(genNb-genNbKill) ]['BestChi2']

                if ( (abs( chi2Min - chi2ToCompare) / abs(chi2ToCompare) < chi2PercCut)
                    and (genNb % genNbKill == 0)
                     ):

                     if best_rSigma > best_rSigmaCutoff :
                         best_rSigma = best_rSigmaInit
                         resetCount +=1

                         if resetCount >=2:
                             alphaParents = [random.choice (list(pointTree.keys())[:-1])]
                             resetCount = 0
                             pp(alphaParents)
                         # exit()
                         print(Fore.GREEN + delimitator + Style.RESET_ALL)
                         printCentered('Reset rSigma value to ' + str(best_rSigma), color=Fore.GREEN)
                         print(Fore.GREEN + delimitator + Style.RESET_ALL)
                     else:


                         best_rSigma = best_rSigma * amplificationFactor
                         justKicked = True
                         print(Fore.YELLOW + delimitator + Style.RESET_ALL)
                         printCentered('NEW rSigma value of ' + str(best_rSigma), color=Fore.YELLOW)
                         print(Fore.YELLOW + delimitator + Style.RESET_ALL)

            ##At some point by increasing rSigma enough we'll effectivelly land on a new region (which we define by best_rSigmaCutoff * amplificationFactor due to the lack of a better solution) we reset the rSigma value back to its initial value and restart the process.

            # #### NEED TO ADD COONDITION TO SEE IF THE NEW KICK HAS PRODUCED A SMALLER CHI 2
            # if genNb == 5:
            # if best_rSigma > best_rSigmaCutoff * amplificationFactor:
            #     best_rSigma = best_rSigmaInit
            #
            #     alphaParents = [random.choice (list(pointTree.keys())[:-1])]
            #     # pp(alphaParents)
            #     # exit()
            #     print(Fore.GREEN + delimitator + Style.RESET_ALL)
            #     printCentered('Reset rSigma value to ' + str(best_rSigma), color=Fore.GREEN)
            #     print(Fore.GREEN + delimitator + Style.RESET_ALL)



            listOfBestChi2.append(chi2Min)
            del listOfBestChi2[0]

            if chi2Min > self.chi2LowerBound:
                # self.Que.put( int(self.threadNumber)+1 )
                self.Que.put( {'Terminate': int(self.threadNumber)+1 } )




        return None

    @regAlg
    def diffEvolAdapt_1 ( self ):
        '''
            Differential evolution algorithm works as per Storn and Price [see ref]
        '''

        modelConstr = constrEval( self.psObject )
        mutationDictInit = {"F_factor" : 0.66,
                            "CR_factor" : 0.236}

        pointTree =  formatTopChi2List_asGen0( self.bestChiSquares, self.sortedChiSquare_ListOfTuples, Auxiliaries= mutationDictInit)



        alphaParents = list (  pointTree.keys() )
        scanIDwThread = self.psObject.modelName + self.psObject.case.replace(" ","") + strftime("-%d-%m-%Y_%H_%M_%S", gmtime()) + '_ThreadNb' + self.threadNumber
        resultsDirDicts = self.psObject.resultDir + 'Dicts/Focus' + strftime("_%d_%m_%Y/", gmtime())

        # print(delimitator)
        resultDict_Thread = {}


        # chi2Min = sortedChiSquare_ListOfTuples[0][1]
        # pp(sortedChiSquare_ListOfTuples[0])
        # 'chi2Min': min( newListOfChi2 ),
        # 'chi2Mean' : np.mean( newListOfChi2),
        # 'chi2Std' : np.std( newListOfChi2)
        chi2Vals = [chi2Tuple[1] for chi2Tuple in self.sortedChiSquare_ListOfTuples ]
        listOfChi2StatDicts = [ { 'chi2Min': min(chi2Vals),
                                    'chi2Mean': np.mean(chi2Vals) ,
                                    'chi2Std': np.std(chi2Vals)
                                                 } ]


        listOfBestChi2 = [  sorted(self.sortedChiSquare_ListOfTuples, key=lambda tup: tup[1])[0][1]  ]
        ####  Pick target vector at rndom / as lowestchi2? ####


        # F_factor = 0.5
        # CR_factor = 0.1


        generatingEngine = self.psObject.engineClass()



        #### Initialisation stage ####
        # Pick out 4 points in phase space and assign one of them as the target.

        ### This population size multiplier seems slightly unnecessary
        genPopSize = len(alphaParents)
        genNb = 0
        changeNb = 0


        while True:

            newParents = []
            pointCount = 0

            #### Populating the new generation. Stop when we have the same number of parents in the new one.
            while len(newParents) < genPopSize:

                for targetKey in alphaParents:



                    # alphaParentsMod = deepcopy(alphaParents)
                    # alphaParentsMod = [ parent for parent in alphaParents if parent != targetKey]
                    rndKeyChoice = random.sample(alphaParents , 3)

                    # targetKey = rndKeyChoice[0]
                    targetChi2 = pointTree[targetKey]['Chi2']
                    targetF_fact = pointTree[targetKey]['Aux']['F_factor']

                    # Gen newF_fact
                    if random.uniform(0,1) < 0.1:
                        newF_fact = 0.1 + random.uniform(0,1) * 0.9
                    else:
                        newF_fact = targetF_fact




                    #### Mutation stage ####
                    # Create a donnor vector out of the parameters of the 3 others via the formula below.
                    donorDict = {}
                    for modelParam in self.psObject.params.keys():
                        xr1_Comp = pointTree[rndKeyChoice[0]][modelParam]
                        xr2_Comp = pointTree[rndKeyChoice[1]][modelParam]
                        xr3_Comp = pointTree[rndKeyChoice[2]][modelParam]

                        # F_factor = random.uniform(0, 2)
                        # newF_fact

                        donorDict[modelParam] = xr1_Comp + newF_fact * (xr2_Comp - xr3_Comp)

                    # alphaParents = [parentPoint for parentPoint in alphaParents if parentPoint not in rndKeyChoice]



                    #### Recombination stage ####
                    # Make a new hybrid vector

                    mutatedDict = {}
                    rndParamChoice = random.choice(list(  self.psObject.params.keys() ) )
                    targetCR_fact = pointTree[targetKey]['Aux']['CR_factor']

                    # Gen newF_fact
                    if random.uniform(0,1) < 0.1:
                        newCR_fact = random.uniform(0,1)
                    else:
                        newCR_fact = targetCR_fact
                    # Gen newCR_fact

                    for modelParam in self.psObject.params.keys():
                        ### new CR Factor
                        if   random.uniform(0, 1) <= newCR_fact or modelParam == rndParamChoice :
                            # print ('_________--------\\\\\\\\')
                            mutatedDict[modelParam] = donorDict[modelParam]
                        else:
                            # print('---------------------')
                            mutatedDict[modelParam] = pointTree[targetKey][modelParam]




                    ########### Selection stage ############
                    massTruth, newPointWithAttr = self.psObject.engineProcedure(generatingEngine, mutatedDict, threadNumber = self.threadNumber, debug = self.debug)

                    # genValidPointOutDict = generatingEngine.runPoint( mutatedDict, threadNumber = self.threadNumber , debug = self.debug)
                    # newPointWithAttr_int = generatingEngine._getRequiredAttributes(mutatedDict, self.threadNumber)
                    # newPointWithAttr = self.psObject._getCalcAttribForDict( newPointWithAttr_int )
                    # massTruth = generatingEngine._check0Mass( newPointWithAttr )



                    if  massTruth == True:

                        newPointKey = list(newPointWithAttr.keys())[0]

                        newChiSquared = modelConstr.getChi2(
                        newPointWithAttr[newPointKey], ignoreConstrList = self.ignoreConstrList, minimisationConstr = self.minimisationConstr, returnDict = False)
                    else:
                        newChiSquared = targetChi2 + 1


                    # newPointWithAttr = generatingEngine._getRequiredAttributes(mutatedDict, threadNumber)
                    ### New point evaluation

                    # print(newChiSquared, targetChi2)
                    # time.sleep(0.3)

                    if newChiSquared < targetChi2:

                        oldID = list(newPointWithAttr.keys())[0]
                        pointGenID = oldID + '-GenNb'+ str(genNb)

                        toAddDict = {}
                        toAddDict[pointGenID] = newPointWithAttr[oldID]
                        toAddChi2 = newChiSquared

                        self.Que.put( {'NewPoint' : {'Dict' : toAddDict,
                                                     'ThreadNb' : int(self.threadNumber)+1}} )

                        # print(toAddChi2, list(toAddDict.keys()) )
                        # with open( resultsDirDicts +'ScanResults.' + scanIDwThread + '.json', 'a') as outfile:
                        #     json.dump(toAddDict, outfile)

                    else:
                        toAddDict = pointTree[targetKey]['FullDescription']
                        toAddChi2 = targetChi2

                    generatingEngine._clean( self.threadNumber )
                    # print( delimitator )
                    ### Add to the new generation
                    pointCount += 1

                    # newPointKey = list(newPointDict['NewPointDict'].keys())[0]
                    # newParamsDict = newPointDict['NewPointDict']
                    # newChi2 = newPointDict['ChiSquared']

                    parentID = targetKey
                    childID = 'G' + str(genNb + 1) + '-P' + str(pointCount)

                    # print(parentID)
                    # pp({'F_factor':newF_fact, 'CR_factor':newCR_fact})
                    pointTree.update ( makeBranch( toAddDict, toAddChi2, parentID, childID, Auxiliaries={'F_factor':newF_fact, 'CR_factor':newCR_fact}) )

                    pointTree[parentID]['Children'].append( childID )
                    newParents.append( childID )

                    # resultDict_Thread.update( toAddDict )



                    # q.put( toAddDict )

            #### Move on to the new generation ####
            # print(len(newParents))
            alphaParents = newParents
            genNb += 1


            ##### Getting the smallest Chi2 and sending it to the plotting function ####
            chi2Min = pointTree[alphaParents[0]]['Chi2']
            # minKey = alphaParents[0]

            newListOfChi2 = []
            for  newParent in alphaParents:
                newListOfChi2.append(pointTree[newParent]['Chi2'])


            chi2Min, chi2Mean , chi2Std=  min( newListOfChi2 ), np.mean( newListOfChi2), np.std( newListOfChi2)
            # chi2Mean = np.mean( newListOfChi2)

            newChi2Dict = {
            'chi2Min': chi2Min,
            'chi2Mean' : chi2Mean,
            'chi2Std' : chi2Std,
            'chi2List' : newListOfChi2 }

                #
                # if pointTree[newParent]['Chi2'] < chi2Min:
                #     chi2Min = pointTree[newParent]['Chi2']
                #     minKey = newParent

            # pp(pointTree[minKey])
            ############# Printing section ###########
            quePut = False

            if chi2Min < listOfBestChi2[-1]:
                printStr = 'Minimum Decrease of'
                percChange = round ( (chi2Min - listOfBestChi2[-1]) / listOfBestChi2[-1], 4) * 100
                quePut = True

                changeNb += 1

                printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)

                # print(delimitator2)
                # print ('\n'+'For ' +Fore.GREEN+'Gen# ' + str(genNb)+ Style.RESET_ALL +
                #         ' the best' + Fore.RED +  ' χ² of ', round(chi2Min,4) ,
                #         Fore.YELLOW + ' from ThreadNb :' + str(int(threadNumber)+1) ,
                #          # ' from point ', minKey ,
                #         "   |   ", Fore.BLUE + printStr +  Style.RESET_ALL, percChange , '%' )
                # print(delimitator2)
            # elif chi2Min >  listOfBestChi2[-1]:
            #     printStr = 'Increase of'

            elif chi2Mean < listOfChi2StatDicts[-1]['chi2Mean']:
                printStr = 'Distribution Mean Decrease of'
                percChange = round ( (chi2Mean - listOfChi2StatDicts[-1]['chi2Mean']) /
                                    listOfChi2StatDicts[-1]['chi2Mean'], 4) * 100

                quePut = True
                changeNb += 1
                printGenMsg(genNb, chi2Min, self.threadNumber, printStr, percChange)


            if quePut ==  True:

                genDict = {}
                auxList = [ pointTree[parentID]['FullDescription'] for parentID in alphaParents]
                for membDict in auxList:
                    genDict.update(membDict)
                # print( len(pointTree) )
                # print( alphaParents )
                self.Que.put( {'GenStat':{'GenNb': genNb,
                                        'ThreadNb': int(self.threadNumber)+1,
                                        'NewChi2': chi2Min,
                                        'OldChi2': listOfBestChi2[-1],
                                        'chi2Min': chi2Min,
                                        'chi2Mean': chi2Mean,
                                        'chi2Std': chi2Std,
                                        'GenDict' : genDict}}
                    )
                # self.Que.put( {'GenNb': genNb,
                #         'ThreadNb': int(self.threadNumber)+1,
                #         'NewChi2': chi2Min,
                #         'OldChi2': listOfBestChi2[-1],
                #         'NewChi2Dict': newChi2Dict ,
                #         'OldChi2Dict': listOfChi2StatDicts[-1] ,
                #         'ChangeNb': changeNb
                #         }
                #     )
                # with open(resultsDirDicts + 'GenStatus_ThreadNb'+ self.threadNumber +'.dat', 'a') as outFile:
                #
                #     outFile.write(  ''.join(  attrName + str(attr)+'   ||  '
                #                             for attrName, attr in zip(['GenNb-', 'MinChi2: ', 'MeanChi2: ', 'StdChi2: '],
                #                                                       [genNb, chi2Min, chi2Mean, chi2Std])
                #                                         ) +'\n'  )

            # print(delimitator2)
            # print ('\n'+'For ' +Fore.GREEN+'Gen# ' + str(genNb)+ Style.RESET_ALL +
            #         ' the best' + Fore.RED +  ' χ² of ', round(chi2Min,4) ,
            #         Fore.YELLOW + ' from ThreadNb :' + str(int(threadNumber)+1) ,
            #          # ' from point ', minKey ,
            #         "   |   ", Fore.BLUE + printStr +  Style.RESET_ALL, percChange , '%' )
            # print(delimitator2)

            # chi2MinDict.update( {'GenNb-'+str(genNb) : {'BestChi2': chi2Min, 'rSigmaVal': best_rSigma}  } )
            # pp(chi2MinDict)

            # listOfBestChi2.append( newChi2Dict )
            listOfChi2StatDicts.append( newChi2Dict )
            listOfBestChi2.append(chi2Min)

            del listOfBestChi2[0]
            del listOfChi2StatDicts[0]

            if chi2Min < self.chi2LowerBound:

                print(Fore.RED + delimitator + Style.RESET_ALL)
                printCentered('Hit χ² bound of '+str(self.chi2LowerBound) +   '   :::   Killing Thread #' + str(int(self.threadNumber)+1), color=Fore.RED)
                print(Fore.RED + delimitator + Style.RESET_ALL)

                # print(Fore.YELLOW + delimitator + Style.RESET_ALL)
                # self.Que.put( int(self.threadNumber)+1 )
                self.Que.put( {'Terminate': int(self.threadNumber)+1 } )
                break



        return None




algDict = regAlg.all
subAlg_rules = {'diffEvol'      :{'Children': ['singleCellEvol'], 'KillAlg':['CurrMiMeStd', 'CurrPrevMiMi']},
                'singleCellEvol':{'Children': ['singleCellEvol'], 'KillAlg':['CurrPrevMiMi']}
                }
