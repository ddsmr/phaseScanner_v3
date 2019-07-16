import math

class constrEval:
    '''
        Given ... will return stuff
    '''

    def __init__(self, phaseSpaceObj):
        '''
        '''
        self.allDicts = phaseSpaceObj.allDicts
        self.noneAttr = phaseSpaceObj.noneAttr

        return None

    def _constraintEvaluation(self, phaseSpacePointDict, noOfSigmasB = 1, noOfSigmasPM = 1, ignoreConstrList = []):
        '''
            Given  point in the phase space via phaseSpacePointDict, checks the different constraints specified in the parameterDict, particleDict and rgflowDict, be it a bound or a parameter match.

            Attributes:
                - phaseSpacePointDict = {'Params':{...},
                                         'Particles':{...},
                                         'Couplings':{...}}      ::      Dictionary associated with a valid point in phase space.
                - noOfSigmasB                       ::           Number of sigmas for the bounds.
                - noOfSigmasPM                      ::           Number of sigmas for the parameter matching.
                - ignoreConstrList                  ::           DEFAULT : [] . List of constraints to be ignored . Used in plotting multiple constaints in the plot function.

            Return:
                Depending on the different types of constraints it returns the chiSquared  and if the constraint passed the check via a dictionary:

                    cEvalDict = {'ConstraintType1' : {'Deviation': ...,
                                                     'PassTruth': ... ,
                                                     'Precision': ... ,
                                                     'Sigma': ...} ,
                                ... }
        '''

        cEvalDict = {}

        notemptyDict = True
        for key in self.allDicts.keys():

            if key not in self.noneAttr:
                # print(phaseSpacePointDict, key)
                notemptyDict = notemptyDict and bool(phaseSpacePointDict[key])

        if notemptyDict == True:

            for modelAttribute in self.allDicts.keys():
                # for modelAttribute in currentDict.keys():

                if modelAttribute not in ignoreConstrList:

                    ##  If the attribute doesn't have any Constraint, pass it , go to the next one
                    if(self.allDicts[modelAttribute]['Constraint']['Type'] == 'None' ):
                        pass

                    #  If the attribute is bounded
                    elif(self.allDicts[modelAttribute]['Constraint']['Type'] == 'CheckBounded'):

                        ## For 'CheckBounded' attribute should have 3 keys: 'CentralVal', 'TheorySigma', 'ExperimentSigma'
                        CentralVal = self.allDicts[modelAttribute]['Constraint']['ToCheck']['CentralVal']
                        TheorySigma = self.allDicts[modelAttribute]['Constraint']['ToCheck']['TheorySigma']
                        ExpSigma = self.allDicts[modelAttribute]['Constraint']['ToCheck']['ExpSigma']

                        try:
                            toCheckVal = phaseSpacePointDict[modelAttribute]
                            devBoundVal = abs(CentralVal - toCheckVal)
                        except:
                            print (delimitator)
                            print (phaseSpacePointDict)
                            print (modelAttribute)

                        # Checks if the value is within noOfSigmasB * σ_(Combined).
                        # print (delimitator)
                        # print (phaseSpacePointDict)
                        # print (modelAttribute)
                        # print(toCheckVal)
                        # print(delimitator)

                        if abs(CentralVal - toCheckVal) < ( math.sqrt(TheorySigma**2 + ExpSigma**2) * noOfSigmasB):
                            boundTruth = True
                        else:
                            boundTruth = False

                        ## cEvalDict new gains a new key for the CheckBounded - attribute with:
                        #       'Deviation'     ::  Distance of the value from the central value
                        #       'PassTruth'     ::  If the deviation is smaller than the combined σ, (i.e. the attribute
                        #                           is within noOfSigmasB * σ_(combined) from the central value it takes
                        #                           True. False otherwise)
                        #       'Precision'     ::  Gives σ_(combined) * noOfSigmasB

                        cEvalDict['CheckBounded' + '-' + modelAttribute] =  \
                                                                {'Deviation' : devBoundVal,
                                                                 'PassTruth':  boundTruth,
                                                                 'Precision' : math.sqrt(TheorySigma**2 + ExpSigma**2) * noOfSigmasB,
                                                                 'Sigma': math.sqrt(TheorySigma**2 + ExpSigma**2)}


                    # If the attribute is matched with some other parameters.
                    # Config file for ParamMatch should have a list with 3 components:
                    #   -   component1 = [list of parameters to evaluate]
                    #   -   component2 = [expression to evaluate]
                    #   -   component3 = [σ to evaluate]

                    elif(self.allDicts[modelAttribute]['Constraint']['Type'] == 'ParamMatch'):
                        # Goes into the first entry and assigns the values to the required mathching parameters from the values of the phaseSpacePointDict
                        for paramExec in self.allDicts[modelAttribute]['Constraint']['ToCheck'][0]:
                            exec(paramExec + '=' +                                  str(phaseSpacePointDict[paramExec]) )

                        # For ParamMatch we have 3 keys :
                        #       genParamMatch      ::   expression to be evaluated  specified in ['ToCheck']['1']
                        #       sigmaParamMatch    ::   Sigma deviation to be evaluated          ['ToCheck']['2']
                        #       devParamMatchVal   ::   Deviation fistance from the evaluated expression from 0.

                        genParamMatch =  eval(self.allDicts[modelAttribute]['Constraint']['ToCheck'][1])
                        sigmaParamMatch = eval(self.allDicts[modelAttribute]['Constraint']['ToCheck'][2])
                        devParamMatchVal = abs(0 - genParamMatch)

                        # Checks the deviation against σ_(generated) * noOfSigmasPM gives paramTruth True if smaller, False otherwise
                        if abs(0 - genParamMatch) < (sigmaParamMatch * noOfSigmasPM):
                            paramTruth = True
                        else:
                            paramTruth = False

                        cEvalDict['ParamMatch' + '-' + modelAttribute] = \
                                                                    {'Deviation': devParamMatchVal,
                                                                     'PassTruth' : paramTruth,
                                                                     'Precision' : sigmaParamMatch * noOfSigmasPM,
                                                                     'Sigma': sigmaParamMatch}


        else:
            return None

        return cEvalDict

    def _calculateChiSquared(self, constraintDict, minimisationConstr='Global', returnDict = False):
        '''
            Given the constraintDict produced by the _constraintEvaluation function, _calculateChiSquared produces either the Global chiSquared for all the constraints in the entire dictionary, or given a specific constraint produces that specific one.

            Arguments:
                - constraintDict        ::      constraint evaluation dictionary (from _constraintEvaluation() ) containing the different vals.
                - minimisationConstr    ::      DEFAULT: 'Global'. Handle that controls the χ^2. Either Global or a list to be passed with the subset of constraints to find the combined χ^2.

            Returns:
                - chiSquared
        '''
        chiSquaredGlobal = None

        if bool(constraintDict):
            if minimisationConstr == 'Global':
                constraintList = constraintDict.keys()
            elif type(minimisationConstr) == list:
                constraintList = minimisationConstr

            chiSquaredGlobal = 0
            chiSquaredDict = {}
            # pp(constraintDict)
            # pp(constraintList)

            for constraint in constraintList:
                auxToMinimise = (constraintDict[constraint]['Deviation'])**2 / (constraintDict[constraint]['Sigma'])**2

                chiSquaredGlobal += auxToMinimise
                chiSquaredDict['ChiSquared-'+constraint] = auxToMinimise

            # print( Fore.RED + 'Global 𝛘² of :' +str(chiSquaredGlobal) + Style.RESET_ALL)

        if returnDict == True:
            return chiSquaredDict
        else:
            return chiSquaredGlobal #, chiSquaredDict#############

    def _checkHardCut(self, phaseSpacePointDict, specificCuts = 'Global'):
        '''
            Function that looks in the attributes of phaseSpacePointDict and then checks in the config file if the attribute has any hard cuts, i.e. either HardCutLess, HardCutMore or CombinedCut.

            Attributes:
                - phaseSpacePointDict           ::          Point dictionary in phase space to constrain.
                - specificCuts                  ::          DEFAULT: Global. Can be set to a list of a subset of all the cuts in the config.

            Returns:
                - passCut == TYPE (bool)
                Returns True if the point passed the cuts, False otherwise.

        '''

        modelDicts = self.allDicts
        if type(specificCuts) == list :

            dictCopy = copy.deepcopy( phaseSpacePointDict )
            for attrib in modelDicts.keys():

                if attrib in specificCuts:
                    pass
                elif( self.allDicts[attrib]['Constraint']['Type'] == 'Constrained' ):
                    pass
                else:
                    del dictCopy[attrib]

            return self._checkHardCut(dictCopy, specificCuts = 'Global')

        elif( specificCuts == 'Global'):
            passCut = True

            # for dictType in phaseSpacePointDict.keys():
            #     attrToCut = phaseSpacePointDict[dictType]

                # print('-------------------------')
                # print(  dictType)
                # print (attrToCut)

            for modelAttribute in phaseSpacePointDict.keys():
                # For every attribute in the phase space dictionary we find the corresponding constraint in the sef.allDicts dictionaries.
                auxDict  = modelDicts[modelAttribute]['Constraint']
                constraintType = auxDict['Type']

                # If point doesn't have a value for the attribute, i.e. None, it is marked as passed for the specific cut for which the value is missing
                if phaseSpacePointDict[modelAttribute] == None:
                    passCut = passCut and True
                else:

                    # Ignore if it isn't one of the types of cuts
                    if constraintType not in ['HardCutLess', 'HardCutMore', 'CombinedCut', 'PolygonCut']:
                        pass

                    elif (constraintType == 'HardCutLess'):

                        constraintHCvalue = auxDict['ToCheck']
                        constrVal = float( phaseSpacePointDict[modelAttribute] )

                        if constrVal < constraintHCvalue:
                            passCut = passCut and True
                        else:
                            passCut = passCut and False

                    elif (constraintType == 'HardCutMore'):


                        constraintHCvalue = auxDict['ToCheck']
                        constrVal = float ( phaseSpacePointDict[modelAttribute] )

                        if constrVal > constraintHCvalue:
                            passCut = passCut and True
                        else:
                            passCut = passCut and False

                    elif (constraintType == 'CombinedCut'):

                        constraintCCvalue = auxDict['ToCheck']['Bound']
                        constraintCCToCheck = auxDict['ToCheck']['ToCheck']
                        constraintCCToCheckVal = auxDict['ToCheck']['ToCheckBound']


                        seccondConstrVal = phaseSpacePointDict[constraintCCToCheck]
                        firstConstrVal = phaseSpacePointDict[modelAttribute]

                        if seccondConstrVal > constraintCCToCheckVal and firstConstrVal > constraintCCvalue:
                            passCut = passCut and True
                        elif (seccondConstrVal < constraintCCToCheckVal):
                            passCut = passCut and True
                        else:
                            passCut = passCut and False

                    elif (constraintType == 'PolygonCut'):

                        # print(delimitator)

                        xCoordName = auxDict['ToCheck']['xCoord']
                        yCoordName = auxDict['ToCheck']['yCoord']
                        point_xCoord =  phaseSpacePointDict[xCoordName]
                        point_yCoord =  phaseSpacePointDict[yCoordName]

                        pointToTest = Point(point_xCoord, point_yCoord)
                        fitPolyg = self.polygCuts[modelAttribute]

                        # print( f'Point with (χ⁺, χ⁰) = ({point_xCoord}, {point_yCoord}) is inside the SUSY polygon --> ', fitPolyg.contains(pointToTest))
                        inPolygon = fitPolyg.contains(pointToTest)

                        passCut = passCut and (not(inPolygon))


        return passCut

    def getChi2(self, pointPSDict, noOfSigmasB = 1, noOfSigmasPM = 1, ignoreConstrList = [], minimisationConstr='Global', returnDict = False):
        '''
            Given a point's phase Space dictionary (no point ID) the funciton evaluates the different constraints and calculates the corresponding chi Square.
            Attributes:
                - phaseSpacePointDict = {'Params':{...},
                                         'Particles':{...},
                                         'Couplings':{...}}      ::      Dictionary associated with a valid point in phase space.
                - noOfSigmasB                       ::           Number of sigmas for the bounds.
                - noOfSigmasPM                      ::           Number of sigmas for the parameter matching.
                - ignoreConstrList                  ::           DEFAULT : [] . List of constraints to be ignored in the Constraint Evaluation.
                - minimisationConstr                ::           DEFAULT: 'Global'. Handle that controls the χ^2. Either Global or a list to be passed with the subset of constraints to find the combined χ^2.
        '''

        if not self._checkHardCut(pointPSDict):
            return math.inf

        else:

            constraintDict =  self._constraintEvaluation(pointPSDict, ignoreConstrList = ignoreConstrList,
                                                         noOfSigmasB = noOfSigmasB, noOfSigmasPM = noOfSigmasPM)


            chiSquare = self._calculateChiSquared(constraintDict, minimisationConstr = minimisationConstr,
                                                 returnDict = returnDict)


        return chiSquare
