import re
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import math as math
import json

from matplotlib.pyplot import colorbar
from Utils.printUtils import *
from halo import Halo


class dictPlotting():
    '''
    '''

    def __init__(self, psObject):
        '''
            Inherits all the attributes from the ps object.
        '''
        self.psObject = psObject
        return None

    def _makePassFailDicts(self, phaseSpaceDict, specificCuts = 'Global',  noOfSigmasB = 1, noOfSigmasPM = 1, ignoreConstrList = [], useChi2AsTest = {'Enable': False , 'Chi2UpperBound' : 1.0, 'TestStatistic': 'ChiSquared'}):
        '''
            Function that separates the large phaseSpaceDict into two dictionaries: passDict, failDict based on the hardcuts and the constraintEvaluation. Is used in plotting.

            Arguments:
                - phaseSpaceDict                ::      Phase space dictionary.
                - specificCuts                  ::      DEFAULT: Global. Can be set to a list of a subset of all the cuts in the config.
                - noOfSigmasB                   ::           Number of sigmas for the bounds.
                - noOfSigmasPM                  ::           Number of sigmas for the parameter matching.
                - ignoreConstrList              ::           DEFAULT : [] . List of constraints to be ignored . Used in plotting multiple constaints in the plot function.

            Returns:
                - {'Passed': passDict, 'Failed' : failDict}
                Passed/ Failed point dictionaries.

        '''

        passDict = {}
        failDict = {}

        constrEvaluator = self.psObject.modelConstr

        #   Check the HardCuts and separate into pass/fail.
        for point in phaseSpaceDict.keys():

            # Check if the point passes the hard cuts
            hardCutPass = constrEvaluator._checkHardCut(phaseSpaceDict[point], specificCuts=specificCuts)

            # If point passes HardCuts then check if it passes bounded/ ParamMatch constraints
            constraintDictPoint = constrEvaluator._constraintEvaluation(phaseSpaceDict[point],
                                                     noOfSigmasB=noOfSigmasB, noOfSigmasPM=noOfSigmasPM,
                                                     ignoreConstrList=ignoreConstrList)

            # Start testing the passing criterion via the required test statistic.
            if useChi2AsTest['Enable'] is True and useChi2AsTest['TestStatistic'] == 'ChiSquared':
                pointChiSquared = constrEvaluator._calculateChiSquared(constraintDictPoint,
                                                                       minimisationConstr='Global')
                phaseSpaceDict[point].update({'ChiSquared': pointChiSquared})

                # For χ² we have < bound  as the passing criterion.
                if pointChiSquared < useChi2AsTest['Chi2UpperBound']:
                    pointPassed = True
                else:
                    pointPassed = False

            elif useChi2AsTest['Enable'] is True and useChi2AsTest['TestStatistic'] == 'LogL':
                pointChiSquared = constrEvaluator._calculateLogLikelyhood(constraintDictPoint,
                                                                          minimisationConstr='Global')
                phaseSpaceDict[point].update({'LogL': pointChiSquared})

                # For Log L we have > bound as the passing criterion.
                if pointChiSquared > useChi2AsTest['Chi2UpperBound']:
                    pointPassed = True
                else:
                    pointPassed = False

            elif useChi2AsTest['Enable'] is False:

                pointPassed = True
                for constraints in constraintDictPoint.keys():
                    pointPassed = pointPassed and constraintDictPoint[constraints]['PassTruth']

            if (pointPassed and hardCutPass) is True:
                passDict.update({point: phaseSpaceDict[point]})

            else:
                failDict.update({point: phaseSpaceDict[point]})

            # else:
            #     # ####################### CHI SQUARED HERE!
            #     if useChi2AsTest['Enable'] is True and useChi2AsTest['TestStatistic'] == 'ChiSquared':
            #         pointChiSquared = constrEvaluator._calculateChiSquared(constraintDictPoint,
            #                           minimisationConstr = 'Global')
            #         # print(pointChiSquared, useChi2AsTest )
            #         phaseSpaceDict[point].update({'ChiSquared': pointChiSquared} )
            #
            #     elif useChi2AsTest['Enable']== True and useChi2AsTest['TestStatistic'] == 'LogL':
            #         pointChiSquared = constrEvaluator._calculateLogLikelyhood(constraintDictPoint,
            #                           minimisationConstr = 'Global')
            #         # print(pointChiSquared, useChi2AsTest )
            #         phaseSpaceDict[point].update({'LogL': pointChiSquared} )
            #
            #
            #     failDict.update({point:phaseSpaceDict[point]})

        return {'Passed': passDict, 'Failed': failDict}

    def _makeListFromDict(self, phaseSpaceDict):
        '''
            Given a phase space dictionary, the function produces a dictionary of ordered lists with all the attributes of the phaseSpaceDict.

            Arguments:
                - phaseSpaceDict        ::      A valid phase space dictionary.

            Returns:
                - dictOfLists={
                            Attr1: [point1_Attr1, point2_Attr1, ...],
                            Attr2: [point1_Attr2, point2_Attr2, ...],
                            ...
                                }

                Dictionary containing all the attributes as keys and lists with the points attibute values.

        '''
        dictOfLists = {}
        for modelAttribute in self.psObject.allDicts.keys():
            # for modelAttribute in self.psObject.allDicts[dictType].keys():
            dictOfLists[modelAttribute] = []

        for point in phaseSpaceDict.keys():
            for modelAttribute in self.psObject.allDicts.keys():
                # for modelAttribute in self.psObject.allDicts[dictType].keys():

                # print(modelAttribute)
                # pp(phaseSpaceDict[point])
                # try:
                if (phaseSpaceDict[point][modelAttribute] != None):

                    # dictOfLists[modelAttribute].append( float(phaseSpaceDict[point][modelAttribute]) )
                    if type(phaseSpaceDict[point][modelAttribute]) == dict:

                        for subAttr in phaseSpaceDict[point][modelAttribute]:
                            if modelAttribute + '-' + subAttr not in dictOfLists.keys():
                                dictOfLists[modelAttribute + '-' + subAttr] = []

                            dictOfLists[modelAttribute + '-' + subAttr].append(phaseSpaceDict[point][modelAttribute][subAttr])
                    else:
                        dictOfLists[modelAttribute].append(phaseSpaceDict[point][modelAttribute])

                # except Exception as e:
                #     print(e)
                #     pass

        # print(len (  list(dictOfLists['Higgs']) ))
        # exit()
        return dictOfLists

    def _makeAxisFromDict(self, phaseSpaceDictPF,  xAxisHandles, yAxisHandles, colorAxisHandles, exprAxis=False):
        '''
            Given a phase space dictionary (either pass or fail), it makes plotting axis, according to the arguments.

            Arguments:
                - phaseSpaceDictPF                                        ::      Phase space dictionary.
                - xAxisHandles, yAxisHandles, colorAxisHandles            ::      e.g. [ 'Params', 'aHat' ]

                IF :
                    - exprAxis      :: DEFAULT : False. Is set to TRUE then one of the axis handles comes in the form:
                                        [ ['Param1', 'Param2', ... ] 'usrFct(Param1, Param2, ...)'  ]
                                        E.g. :
                                            xAxisHandle OR yAxisHandle OR colorAxisHandles =   [['BMu', 'Mu'],  'BMu/Mu']

            Returns:
                - {'xAxis' : xAxis, 'yAxis': yAxis, 'colorAxis':colorAxis }
                Dictionary with the different axis.
        '''

        xAxis = []
        yAxis = []
        colorAxis = []
        pointIDAxis = []



        # If exprAxis is False, format assumed is keys and their classification from self.classification['axisName']
        if exprAxis is False:

            for point in phaseSpaceDictPF.keys():

                # try:
                #     print( point, float ( phaseSpaceDictPF[point][colorAxisHandles[0]][colorAxisHandles]) )
                # except Exception as e:
                #     print(e)
                #     exit()

                # exit()

                for axis, axisHandle in zip([xAxis, yAxis, colorAxis], [  xAxisHandles, yAxisHandles, colorAxisHandles]):
                    try:
                        valToAppend = phaseSpaceDictPF[point][axisHandle]
                    except:
                        valToAppend = None

                    axis.append( valToAppend  )
                pointIDAxis.append(point)


        # If exprAxis is True then assume exec for all the axis and drop the classification
        #      exprAxis = True
        #      xAxisHandle OR yAxisHandle OR colorAxisHandles =   [['BMu', 'Mu'],  'BMu/Mu']
        else:
            for point in phaseSpaceDictPF.keys():
                for axis, axisHandles in zip([xAxis, yAxis, colorAxis], [xAxisHandles, yAxisHandles, colorAxisHandles]):

                    # print(axis, axisHandles)

                    if type(axisHandles) == list:

                        axisParams = axisHandles[0]
                        axisExpr = axisHandles[1]
                        # print(axisExpr, axisParams, 'aaaaaaaaaaaaaa')
                        for param in axisParams:

                            paramType = self.psObject.classDict[param]
                            # print (param, phaseSpaceDictPF[point][param])
                            exec(param + '=' + str(phaseSpaceDictPF[point][param]))
                            # exit()

                        # print(eval (axisExpr))
                        axis.append(eval(axisExpr))

                    elif axisHandles in self.psObject.allDicts.keys():
                        # print(axisParams)
                        # print('delimitator')
                        axis.append(phaseSpaceDictPF[point][axisHandles])
                    # else:

        return {'xAxis': xAxis, 'yAxis': yAxis, 'colorAxis': colorAxis, 'pointIDAxis': pointIDAxis}

    def plotModel(self, phaseSpaceDict, xAxisHandles, yAxisHandles, colorAxisHandles, colorMap='winter_r',
                  specificCuts='Global',
                  ignoreConstrList=[], noOfSigmasB=1, noOfSigmasPM=1,  # < ------- Needed in the pass Fail stage
                  restrictAxis=False, xAxisLim=[], yAxisLim=[],
                  # exprAxis=False,
                  TeXAxis='',
                  pltName='',
                  plotSeparateConstr=[], separateConstrMarkers=['h'], defaultMarker='o',
                  exportFormatList=['png', 'pdf'],
                  useChi2AsTest={'Enable': True, 'Chi2UpperBound': 11.0705, 'TestStatistic': 'ChiSquared'},
                  plotCard={}
                  ):
        '''
            Super duper function to plot whatever you want from the model.

            Arguments:
                - phaseSpaceDict                                          ::      Phase space Dictionary.
                - xAxisHandles, yAxisHandles, colorAxisHandles            ::      e.g. [ 'Params', 'aHat' ]
                - colorMap                      ::          DEFAULT : 'flag'. Set to what color scheme you want.
                See matplotlib documentation for all available styles.

                - plotSeparateConstr            ::          DEFAULT: []. Sepcify in list what constraints to be plot
                separatelly, i.e. disregarding the others. If let empty will look at all constraints.
                - separateConstrMarkers         ::          DEFAULT: ['o']. all the diffrent constraint markers to go
                with plotSeparateConstr.

                - exprAxis                      ::          DEFAULT: False. Set to true to use expresions for the axis.
                - TeXAxis                       ::          DEFAULT: ''. To be set to the LaTeX label for the exprAxis.

                - restrictAxis                  ::          DEFAULT: False. Set to true to restrict axis.
                - xAxisLim , yAxisLim           ::          DEFAULT: []. Set to new axis bounds.


                For checkHardCut:
                - specificCuts                  ::          DEFAULT: Global. Can be set to a list of a subset of all
                the cuts in the config. Will plot points based on subset of cuts instead of all.

                For constraintEvaluation:
                - noOfSigmasB                   ::           Number of sigmas for the bounds.
                - noOfSigmasPM                  ::           Number of sigmas for the parameter matching.
                - ignoreConstrList              ::           DEFAULT : [] . List of constraints to be ignored . Used in
                plotting multiple constaints in the plot function.

            Returns:
                - auxDict = {'Passed' : passDict, 'Fail' : failDict }
        '''
        if type(xAxisHandles) == list or type(yAxisHandles) == list or type(colorAxisHandles) == list:
            exprAxis = True
        else:
            exprAxis = False

        if (bool(plotSeparateConstr) is False):
            plotCount = 1
        else:
            plotCount = len(plotSeparateConstr)

        plotListPass = []
        plotListExclude = []
        # ######### Font size / Fig sizefrom matplotlib import rc
        plt.rc('font', **{'family': 'serif', 'serif': ['DejaVu Sans']})
        plt.rc('font', size=self.psObject.plotFormatting['fontSize'])
        plt.rc('text', usetex=True)

        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(111)

        returnDict = {}

        spinner = Halo(text='Working hard for the money, so hard for the money ' + Fore.GREEN + '$$$' + Style.RESET_ALL,
                       spinner='dots')
        spinner.start()

        print(exprAxis)

        # if exprAxis == False:
        #     pltStr = xAxisHandles.replace('/', '.') + '-' + yAxisHandles.replace('/', '.') + '-' + colorAxisHandles.replace('/', '.')
        # else:
        # stripedName = p.sub('', self.psObject.name+'.')
        # pltStr = (str(xAxisHandles)+ '-' + str(yAxisHandles) + '-' + str(colorAxisHandles))
        p = re.compile(r"['*[,\] ]+")
        if exprAxis is not True:
            pltStr = p.sub('', (str(xAxisHandles) + '-' + str(yAxisHandles) + '-' + str(colorAxisHandles)))
        else:
            pltStr = 'CustomPlot-' + pltName
        # pltStr = p.sub('', (str(xAxisHandles) + '-' + str(yAxisHandles) + '-' + str(colorAxisHandles)))
        # print(delimitator)
        # print(pltStr)
        # print(stripedName)
        # print(delimitator)
        # exit()

        self._writePlotAttr(xAxisHandles, yAxisHandles, colorAxisHandles, useChi2AsTest, pltStr)
        for plotNumber in range(plotCount):

            if bool(plotSeparateConstr) is False:
                auxDict = self._makePassFailDicts(phaseSpaceDict, specificCuts=specificCuts, noOfSigmasB=noOfSigmasB,
                                                  noOfSigmasPM=noOfSigmasPM, ignoreConstrList=ignoreConstrList,
                                                  useChi2AsTest=useChi2AsTest)

                statsStr = 'Global'

            else:
                auxIgnoreList = copy.deepcopy(plotSeparateConstr)
                auxIgnoreList.remove(plotSeparateConstr[plotNumber])

                statsStr = plotSeparateConstr[plotNumber]

                auxDict = self._makePassFailDicts(phaseSpaceDict, specificCuts=specificCuts, noOfSigmasB=noOfSigmasB,
                                                  noOfSigmasPM=noOfSigmasPM, ignoreConstrList=auxIgnoreList,
                                                  useChi2AsTest=useChi2AsTest)

            passDict = auxDict['Passed']
            failDict = auxDict['Failed']

            # print(delimitator)
            #
            # print(len(passDict), len(failDict))
            # print(delimitator)

            self._writeStatsFromDict(passDict, pltStr, passFailString='Passed-' + statsStr + '-Constr')
            self._writeStatsFromDict(failDict, pltStr, passFailString='Failed-' + statsStr + '-Constr')

            passAxisDict = self._makeAxisFromDict(passDict, xAxisHandles, yAxisHandles, colorAxisHandles,
                                                  exprAxis=exprAxis)
            failAxisDict = self._makeAxisFromDict(failDict, xAxisHandles, yAxisHandles, colorAxisHandles,
                                                  exprAxis=exprAxis)

            scattPlot = ax1.scatter(failAxisDict['xAxis'], failAxisDict['yAxis'], c=failAxisDict['colorAxis'],
                                    cmap=plt.get_cmap(colorMap), marker=defaultMarker,
                                    alpha=self.psObject.plotFormatting['failPlot']['alpha'],
                                    lw=self.psObject.plotFormatting['failPlot']['lw'],
                                    s=self.psObject.plotFormatting['failPlot']['s'], zorder=1)
            climx, climy = scattPlot.get_clim()
            if (len(passAxisDict['colorAxis']) != 0):
                climx = min(climx, min(passAxisDict['colorAxis']))
                climy = max(climy, max(passAxisDict['colorAxis']))

            scattPlot_pass = ax1.scatter(passAxisDict['xAxis'], passAxisDict['yAxis'], cmap=plt.get_cmap(colorMap),
                                         marker=separateConstrMarkers[plotNumber], c=passAxisDict['colorAxis'],
                                         alpha=self.psObject.plotFormatting['passPlot']['alpha'],
                                         lw=self.psObject.plotFormatting['passPlot']['lw'],
                                         s=self.psObject.plotFormatting['passPlot']['s'],
                                         zorder=2,  vmin=climx, vmax=climy, edgecolor='black')

            if bool(plotSeparateConstr) is False:
                returnDict = auxDict
            else:
                returnDict[plotSeparateConstr[plotNumber]] = auxDict

        # Puts labels according to the type of dictionary
        axisLabels = []
        TeXAxisCount = 0
        for axis in [xAxisHandles, yAxisHandles, colorAxisHandles]:

            if type(axis) == list:
                if exprAxis is True:
                    latexLabel = TeXAxis[TeXAxisCount]
                    axisLabels.append(latexLabel)
                    TeXAxisCount += 1

            elif axis in self.psObject.allDicts.keys():
                latexLabel = self.psObject.allDicts[axis]['LaTeX']
                axisLabels.append(latexLabel)

        color_bar = fig.colorbar(scattPlot, format='%.3f')  # , label=axisLabels[2], ticks=[climx, 0, climy])
        color_bar.set_label(axisLabels[2], labelpad=20)

        if type(colorAxisHandles) != list:
            toCheckDict = self.psObject.allDicts[colorAxisHandles]

        # Checks if the collor axis has a 'CheckBounded' constraint and sets two markers on the lower and upper bounds
            if colorAxisHandles.replace(' ', '') in toCheckDict.keys():
                if toCheckDict[colorAxisHandles]['Constraint']['Type'] == 'CheckBounded':

                    plusSigma = toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['CentralVal'] + toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['TheorySigma'] + toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['ExpSigma']

                    minusSigma = toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['CentralVal'] - toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['TheorySigma'] - toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['ExpSigma']

                    centralVal = toCheckDict[colorAxisHandles]['Constraint']['ToCheck']['CentralVal']


                    if plusSigma > climy:
                        pass
                    else:
                        color_bar.ax.plot([0, 1], [( plusSigma - climx) / (climy - climx)]*2 , color = 'black')

                    if minusSigma > climy:
                        pass
                    else:
                        color_bar.ax.plot([0, 1], [( minusSigma - climx) / (climy - climx)]*2 , color = 'black')

        color_bar.set_alpha(1)
        color_bar.draw_all()

        if restrictAxis is True:
            if (yAxisLim != []):
                plt.ylim(yAxisLim)
            if(xAxisLim != []):
                plt.xlim(xAxisLim)

        # plt.xticks([]), plt.yticks([])
        plt.xlabel(axisLabels[0], fontsize=self.psObject.plotFormatting['fontSize'],  labelpad=20)
        plt.ylabel(axisLabels[1], fontsize=self.psObject.plotFormatting['fontSize'])

        spinner.stop_and_persist(symbol=Fore.GREEN + '✓' + Style.RESET_ALL,
                                 text='Finished plotting. Moving on to exporting')

        formatStr = ''
        for format in exportFormatList:
            formatStr += format
            formatStr += ' '

        # sensitivity region here
        # 100 TeV band: [0.958, 1.044]
        # CMS sensitivity band: [39.128 / 16.319, 14.000479 / 16.319]
        # xmin, xmax, ymin, ymax = plt.axis()
        # ax1.margins(x=0)
        # cmapClrs = plt.get_cmap(colorMap)
        # fillColor = cmapClrs(0.3)
        # ax1.fill_between(np.linspace(xmin, xmax), 1.044, 0.958, alpha=0.3, zorder=3,
        # ax1.fill_between(np.linspace(xmin, xmax), 39.128 / 16.319, 14.000479 / 16.319, alpha=0.3, zorder=3,
        #                  facecolor=fillColor,
        #                  edgecolor=fillColor, hatch=r'/', lw=0.1
        #                  )
        # # inset axes....
        # from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
        # axins = zoomed_inset_axes(ax1, 2.5, loc=1)  # zoom-factor: 2.5, location: upper-left
        # axins.scatter(passAxisDict['xAxis'], passAxisDict['yAxis'], cmap=plt.get_cmap(colorMap),
        #                              marker=separateConstrMarkers[plotNumber], c=passAxisDict['colorAxis'],
        #                              alpha=self.psObject.plotFormatting['passPlot']['alpha'],
        #                              lw=self.psObject.plotFormatting['passPlot']['lw'],
        #                              s=self.psObject.plotFormatting['passPlot']['s'],
        #                              zorder=2,  vmin=climx, vmax=climy, edgecolor='black')
        # axins.scatter(failAxisDict['xAxis'], failAxisDict['yAxis'], c=failAxisDict['colorAxis'],
        #                             cmap=plt.get_cmap(colorMap), marker=defaultMarker,
        #                             alpha=self.psObject.plotFormatting['failPlot']['alpha'],
        #                             lw=self.psObject.plotFormatting['failPlot']['lw'],
        #                             s=self.psObject.plotFormatting['failPlot']['s'], zorder=1)
        #
        # xmin, xmax, ymin, ymax = plt.axis()
        # axins.margins(x=0)
        #
        #
        # axins.fill_between(np.linspace(xmin, xmax), 1.044, 0.958, alpha=0.3, zorder=3,
        #                  facecolor=fillColor,
        #                  edgecolor=fillColor, hatch=r'/', lw=0.1
        #                  )
        # x1, x2, y1, y2 = 0.85, 1.03, 0.90, 1.15# specify the limits
        # axins.set_xlim(x1, x2) # apply the x-limits
        # axins.set_ylim(y1, y2) # apply the y-limits
        # plt.yticks(visible=False)
        # plt.xticks(visible=False)
        #
        # from mpl_toolkits.axes_grid1.inset_locator import mark_inset
        # mark_inset(ax1, axins, loc1=2, loc2=4, fc="none", ec="0.5")

        # fig.tight_layout()
        fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
        # fig.tight_layout(pad=1.0, w_pad=0.5, h_pad=1.0)

        spinner = Halo(text='Exporting plots in format : ' + Fore.RED + formatStr + Style.RESET_ALL, spinner='dots')
        spinner.start()

        self._exportPlots(xAxisHandles, yAxisHandles, colorAxisHandles, pltStr, exportFormatList=exportFormatList,
                          plotCard=plotCard)
        spinner.stop_and_persist(symbol=Fore.GREEN + '✓' + Style.RESET_ALL,
                                 text='Finished exporting.')
        plt.show()

        return returnDict, passAxisDict, failAxisDict

    def _exportPlots(self, xAxisHandle, yAxisHandle, colorAxisHandle, plotName, exportFormatList=['png', 'pdf'],
                    plotCard={}):
        '''
            Given a string handle for the xAxis, yAxis, and colorAxis, the function exports plots in the formats
            specified in the exportFormatList, default is .pdf

            Arguments:
                - xAxisHandle, yAxisHandle, colorAxisHandle     ::      handles for the different axis.
                - exportFormatList                              ::      DEFAULT : ["pdf"]. List of the different
                formats to export to.

            Return:
                - None.
                Exports the plots as:
                    xAxis-yAxis-colorAxis.ext1,
                    ---------""----------.ext2,
                    ...
        '''
        # modelFileName = self.modelName
        # auxHandle = self.case

        resultsDirPlots = self.psObject.resultDir + 'Plots/'

        FNULL = open(os.devnull, 'w')

        p = re.compile(r"['*[,\] ]+")
        # if type(xAxisHandle) != list and type(yAxisHandle) != list and type(colorAxisHandle) != list:
        #     plotName = p.sub('', (str(xAxisHandle) + '-' + str(yAxisHandle) + '-' + str(colorAxisHandle)))
        # else:
        #     plotName = 'CustomPlot-' + strftime("-%d%m%Y%H%M%S", gmtime())
        # plotName = xAxisHandle.replace('/', '.') + '-' + yAxisHandle.replace('/', '.') + '-' + colorAxisHandle.replace('/', '.')
        subprocess.call('mkdir ' + resultsDirPlots, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call('mkdir ' + resultsDirPlots + plotName + '/', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

        for formatType in exportFormatList:
            plotStr = resultsDirPlots + plotName + '/' + plotName + "." + formatType
            plt.savefig(plotStr)

        # Save the .json file containing the plt parameters
        with open(resultsDirPlots + plotName + '/' + plotName + ".json", 'w') as jsonOut:
            json.dump(plotCard, jsonOut)
        return None

    # ######## Write TeX stuff ###########
    def _writeTeXfile(self, rawString, passFailString='Global', titleStr='Give Me A Title', resultDir='Default'):
        '''
            Function that compiles and produces a pdf file via pdflatex.
        '''

        header = r'''\documentclass{article} \title{''' + titleStr + r'''} \begin{document} '''
        footer = r'''\end{document}'''

        # main = '''I'm writing #LaTeX with Python !'''

        content = header + rawString + footer
        fileName = self.psObject.name + '_Stats_' + passFailString
        with open(fileName + '.tex', 'w') as f:
            f.write(content)

        try:
            subprocess.call('pdflatex ' + fileName, shell=True,  stdout=FNULL, stderr=subprocess.STDOUT)
        except Exception as e:
            raise
            print(e)
        # commandLine = subprocess.Popen(['pdflatex', fileName])
        # commandLine.communicate()

        for fileExtension in ['.aux', '.log', '.tex']:
            os.unlink(fileName + fileExtension)

        if resultDir == 'Default':
            toMoveDir = self.psObject.resultDir
        else:
            toMoveDir = resultDir

        subprocess.call('mv ' + fileName + '.pdf ' + toMoveDir + fileName + '.pdf', shell=True)

    def _writePlotAttr(self, xAxisHandle, yAxisHandle, colorAxisHandle, useChi2AsTest, plotStr, individConstr=''):
        '''
            Function is called when we make a plot to write in the same directory the attirbutes on which the plot is
            based, i.e. what are the :
                - HardCuts
                - Global / local Chi squared with it's constituents and standard deviations.

        '''
        p = re.compile(r'\W+|[_]')
        stripedName = p.sub('', self.psObject.name+'.')
        resultsDirPlots = self.psObject.resultDir + 'Plots/'

        p = re.compile(r"['*[,\] ]+")
        # plotStr = p.sub('', (str(xAxisHandle) + '-' + str(yAxisHandle) + '-' + str(colorAxisHandle)))
        # plotStr = (str(xAxisHandle)+ '-' + str(yAxisHandle) + '-' + str(colorAxisHandle)).replace('/','.')

        # plotStr = xAxisHandle.replace('/', '.') + '-' + yAxisHandle.replace('/', '.') + '-' + colorAxisHandle.replace('/', '.')

        subprocess.call('mkdir ' + resultsDirPlots, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call('mkdir ' + resultsDirPlots + plotStr + '/',  shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

        TeXString = '''\maketitle
        Statistics for ''' + stripedName + r''' attributes.'''
        TeXString += '''\\newline We are imposing a ''' + useChi2AsTest['TestStatistic'] + ''' cut at a upper bound of :''' + \
                     str(useChi2AsTest['Chi2UpperBound']) + '''\\newline'''
        TeXString += ''' The following are the attributes that go into the making of the plot \\textbf{''' + plotStr+ '''}: \\newline\\newline  The following have a contribution to $\chi^2_G$ corresponding to: \\newline \\newline'''

        #### Putting in the constraints:
        for mdlConstr in self.psObject.constrDict.keys():

            constrType = self.psObject.allDicts[mdlConstr]['Constraint']['Type']
            if constrType == 'CheckBounded':
                mdlTeX = self.psObject.allDicts[mdlConstr]['LaTeX']
                testMean = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck']['CentralVal']
                expSigma = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck']['ExpSigma']
                theorySigma = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck']['TheorySigma']

                TeXString+=   mdlTeX + ''' with test mean, experimental StdDev, and theoretical StdDev: '''



                rawStr = r'''\begin{itemize}
                             \item '''+ mdlTeX + ''' Test Mean : ''' +  str(testMean) + \
                             r'''\item '''+ mdlTeX + ''' Expedimental Standard deviation : ''' +  str(expSigma)  + \
                             r'''\item '''+ mdlTeX + ''' Theoretical Standard deviation : ''' +  str(theorySigma)  + \
                         r'''\end{itemize}'''
                TeXString += rawStr
            elif constrType == 'ParamMatch':

                toCheckParamsList = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck'][0]
                toCheckParams = '.'.join( str(attrToCheck)+' ' for attrToCheck in toCheckParamsList )


                toCheckCond = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck'][1]
                toCheckSigma = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck'][2]

                TeXString += '  ' + mdlConstr + ' has ParamMatch with: '

                rawStr = r'''\begin{itemize}
                             \item To Check Params: $'''+ toCheckParams + '''$ '''  + \
                             r'''\item To Check Condition:  $'''+ toCheckCond + '''$''' + \
                             r'''\item To Check StandarDev: $'''+ toCheckSigma + '''$''' + \
                         r'''\end{itemize}'''
                TeXString += rawStr
                # TeXString += ''' \\newline '''

        ### Putting in the Hard Cuts:
        ToPrintStr = r'\makebox[\linewidth]{\rule{\paperwidth}{3pt}}'
        TeXString += ToPrintStr


        TeXString += ''' \\newline The following have a hard cut corresponding to: \\newline \\newline'''

        for mdlConstr in self.psObject.cutDict.keys():

            print( mdlConstr )

            cutType = self.psObject.allDicts[mdlConstr]['Constraint']['Type']
            cutVal = self.psObject.allDicts[mdlConstr]['Constraint']['ToCheck']
            mdlTeX = self.psObject.allDicts[mdlConstr]['LaTeX']

            TeXString+=   mdlTeX + ''' with a cut type and value '''
            rawStr = r'''\begin{itemize}
                         \item '''+ mdlTeX + ''' Cut Type :''' +  cutType + \
                         r'''\item '''+ mdlTeX + ''' Cut Value : ''' +  str(cutVal)  + \
                     r'''\end{itemize}'''
            TeXString += rawStr

        self._writeTeXfile(TeXString, titleStr='Plot Attributes ' + stripedName, resultDir=resultsDirPlots + plotStr + '/',
                           passFailString='PlotAttrib' + individConstr)

        return None

    def _writeStatsFromDict(self, phaseSpaceDict, plotStr, passFailString='Global', printStats=True, showHists=False):
        '''
            Given a valid phaseSpaceDict, the function goes through the values of the different attributes and outputs the average value and standard deviation.

            Arguments:
                - phaseSpaceDict        ::          A valid phase space dictionary.
        '''
        dictOfLists = self._makeListFromDict(phaseSpaceDict)
        resultsDirPlots = self.psObject.resultDir + 'Plots/'

        p = re.compile(r'\W+|[_]')
        stripedName = p.sub('', self.psObject.name+'.')

        TeXString = '''\maketitle
        Statistics for ''' + stripedName + r''' attributes.'''
        TeXString += ''' The following is for points that \\textbf{''' + passFailString + '''} the constraints: \\newline\\newline'''

        dictMinMax = {classType: {} for classType in self.psObject.allDicts.keys()}
        teXDict = {classType: {'BodyStr': '',
                               'HeaderStr': r'The following are the statistics for \textbf{ ' + str(classType) + r'} :'}
                   for classType in self.psObject.classList}

        # sectionHeader = {'Params':{'String':'Param String'},
        #                  'Particles':{'String':'Particles String'},
        #                  'Calc':{'String':'Calc String'}}
        #
        # pp(self.allDicts)
        # pp( list(dictOfLists.keys())  )
        # exit()
        # pp(dictOfLists)

        for modelAttribute in dictOfLists.keys():
            # print(delimitator2)
            # print(modelAttribute)

            try:

                dictMinMax[modelAttribute] = {'Min': min(dictOfLists[modelAttribute]), 'Max': max(dictOfLists[modelAttribute])}


                meanVal = np.mean(dictOfLists[modelAttribute])
                stdVal = np.std(dictOfLists[modelAttribute])

                minVal = np.min(dictOfLists[modelAttribute])
                maxVal = np.max(dictOfLists[modelAttribute])

                if printStats:
                    print()
                    print( 'Minimum Value for ', Fore.RED + modelAttribute + Style.RESET_ALL , ' is: ', minVal )
                    print( 'Maximum Value for ', Fore.RED + modelAttribute + Style.RESET_ALL , ' is: ', maxVal )
                    print( 'Average Value for ', Fore.RED + modelAttribute + Style.RESET_ALL , ' is: ', meanVal )
                    print( 'Standard deviation for ', Fore.RED + modelAttribute + Style.RESET_ALL , ' is: ', stdVal )
                    print (delimitator)

                try:
                    modelAttribute_TeX = self.psObject.allDicts[modelAttribute]['LaTeX']
                except:
                    try:
                        modelAttribute_TeX = self.psObject.allDicts[ modelAttribute.split('-')[0] ]['LaTeX'] + modelAttribute.split('-')[1]
                    except:
                        modelAttribute_TeX = modelAttribute

                try:
                    attrClassif = self.psObject.classDict[modelAttribute]
                except:
                    attrClassif = self.psObject.classDict[modelAttribute.split('-')[0] ]
                # print(attrClassif)

                rawStr = modelAttribute_TeX + r''' :''' +\
                         r'''\begin{itemize}
                             \item The average value for ''' + modelAttribute_TeX + ''' is : ''' + \
                             str(meanVal) + \
                             r'''\item Standard deviation for ''' + modelAttribute_TeX + ''' is : ''' + \
                             str(stdVal) + \
                             r'''\item Minimum value for ''' + modelAttribute_TeX + ''' is : ''' + \
                             str(minVal) + \
                             r'''\item Maximum value for ''' + modelAttribute_TeX + ''' is : ''' + \
                             str(maxVal) + \
                         r'''\end{itemize}'''
                teXDict[attrClassif]['BodyStr'] += rawStr


            except KeyError as e:
                raise

            except Exception as e:

                if printStats:
                    print(delimitator2)
                    print (Fore.YELLOW + 'Attribute {modelAttribute} has no values.'.format(modelAttribute = modelAttribute), e)
                    print(delimitator2, delimitator)

                continue

            if showHists:# and (self.classification[modelAttribute]=='Particles' or modelAttribute=='ChiSquared'):

                try:
                    plt.figure(figsize = (10,10))
                    n, bins, patches = plt.hist( dictOfLists[modelAttribute], 'auto', density=True, facecolor='g', alpha=0.75)


                    plt.xlabel(self.psObject.allDicts[modelAttribute]['LaTeX'])
                    # plt.ylabel('Probability')
                    plt.title('Histogram of ' + modelAttribute + " - " + passFailString)
                    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
                    # plt.axis([40, 160, 0, 0.03])
                    plt.grid(True)
                    # plt.show()



                    subprocess.call('mkdir ' + self.resultDir + 'Histograms/', shell = True, stdout=FNULL, stderr=subprocess.STDOUT)
                    plt.savefig(self.resultDir + 'Histograms/Histogram_' + modelAttribute + passFailString +'.png')
                except Exception as e:
                    print(delimitator2)
                    print (Fore.YELLOW + r'Can\'t produce histogram for {modelAttribute} in the {passFail} stage.'.format(modelAttribute = modelAttribute, passFail = passFailString), e)
                    print(delimitator2, delimitator)


        for classType in teXDict.keys():

            ToPrintStr = r'\makebox[\linewidth]{\rule{\paperwidth}{3pt}}' +'\n' + \
            teXDict[classType]['HeaderStr'] + r'\newline \newline' + teXDict[classType]['BodyStr']
            TeXString += ToPrintStr

        self._writeTeXfile(TeXString, passFailString, titleStr=stripedName + ' ' + passFailString,
                           resultDir=resultsDirPlots + plotStr + '/')

        # import sys
        # sys.exit()
        # printCentered('Constraint: ' + plotSeparateConstr[plotNumber], Fore.RED)
        # print( 'Average Value for ', xAxisHandles[1], ' is: ', np.mean(passAxisDict['xAxis'] + failAxisDict['xAxis']))
        # print( 'Average Value for ', yAxisHandles[1], ' is: ', np.mean(passAxisDict['yAxis']+ failAxisDict['yAxis']))
        # print( 'Average Value for ', colorAxisHandles[1], ' is: ', np.mean(passAxisDict['colorAxis']+ failAxisDict['colorAxis']))
        # print (delimitator)

        return dictMinMax
