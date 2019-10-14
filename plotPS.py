import argparse
import re
from phaseScanner import phaseScannerModel, checkListForLatestDate, convertDateTimeToStr, getLatestFocusDir
from Utils.Gmail.gMailModule import *
from Utils.printUtils import *
from Utils.dictplotting import *


def convertToFloatList(strToConvert):
    '''
        Given a string with delimitators ',', function converts it into a list of floats.

        Arguments:
            - strToConvert              ::          Format of the string e.g [0.1 , 52]

        Returns:
            - splitList
            List of the floats in the string.
    '''
    toReplaceList = ['[', ']', ' ']
    convers = strToConvert
    for char in toReplaceList:
        convers = convers.replace(char, '')

    splitList = []
    for strBound in convers.split(','):

        splitList.append(float(strBound))

    return splitList


def makeCutDictFromStr(strToConvert):
    '''
            Given a string in the form "{Higgs:[100, 200], Top:[300, 400]}" the function creates a cut dictionary in the
        form {'Higgs': {'Min': 100, 'Max': 200}, 'Top':{'Min': 300, 'Max': 400}}
    '''
    pKeys = re.compile(r':')
    pPunct = re.compile(r'\W')

    cutDict = {}
    for attrEntry in strToConvert.split('|'):
        splitStr = pKeys.split(attrEntry)
        attrKey, intervalStr = pPunct.sub('', splitStr[0]), splitStr[1]

        minMaxDict = {}
        for intervalSide, intKey in zip(intervalStr.split(','), ('Min', 'Max')):
            minMaxDict[intKey] = float(pPunct.sub('', intervalSide))
        cutDict[attrKey] = minMaxDict

    return cutDict


if __name__ == '__main__':
    # #################################      Arguments      ###########################################
    parser = argparse.ArgumentParser(description='Process the inputs for the plotting function')
    exprAxisMsg = Fore.RED + ' Optional Behaviour || ' + Style.RESET_ALL \
                           + ('If the axis are expressions, the axis should be '
                              'entered as a string consisting of [param1, param2, ...] | expr(param1, param2, ...),'
                              'with the | delimitator.  E.g. -x="[BMu, Mu, aHat]| BMu / Mu  + 2* aHat" ')
    parser.add_argument('modelName', help=Fore.GREEN + 'Name of the model to be initialiased.' + Style.RESET_ALL)
    parser.add_argument('modelCase', help=Fore.GREEN + 'Case to be handled.' + Style.RESET_ALL)
    # parser.add_argument('--CustomRun', default = None, help = 'Use flag to run custom user defined script.')

    parser.add_argument("-x", '--xAxis', help='Attribute to plot on the x Axis. Default specified in config' + exprAxisMsg,
                        type=str, default='')
    parser.add_argument("-y", '--yAxis', help='Attribute to plot on the y Axis. Default specified in config',
                        type=str, default='')
    parser.add_argument("-c", '--colorAxis', help='Attribute to plot on the color Axis. Default specified in config',
                        type=str, default='')
    parser.add_argument('-oRF', help='Open the latest focus directory for plotting. Enable to true',
                        action="store_true")
    parser.add_argument('--targetResDir', default='', help='Open the specific result directory for plotting.')
    parser.add_argument('--colorMap', default='winter_r', help='Color map to be used. Default winter_r')
    parser.add_argument('--filterByAttrs', default='', help='Set to filter by attributes, e.g. "{Higgs:[100, 200], mTop:[300, 400]}" will only admit those points that have a Higgs mass between the values of 100 and 400.', type=str)
    axisMsg = 'Handle to specify if the axis are restricted. Set to string of the form e.g. "[100, 200]"'
    parser.add_argument('--xAxisLim', help=axisMsg, type=str)
    parser.add_argument('--yAxisLim', help=axisMsg, type=str)


    # parser.add_argument('--exprAxis', help=exprAxisMsg, type=bool, default=False)
    parser.add_argument('--pltName', help='Set custom Name for the plot.' + Fore.RED + 'Required' + Style.RESET_ALL + ' for custom expression plots', type=str, default='')

    texLabelMsg = ('Labels for the axis if exprAxis is used. Enter raw TeX strings for each axis that requires a '
                   'custom label. E.g. if we have 2 custom axis we enter "$\alpha$ | $\beta$" for their formatting.')
    parser.add_argument('--TeXlabels', help=texLabelMsg, type=str, default='')

    parser.add_argument("-g", '--pushToGit', help='Push by default to the Results_Auto repo the plot when done.',
                        action="store_true")

    parser.add_argument("-mA", '--modelAttributes', help='See what attributes are available to be plotted.',
                        action="store_true")
    sepConstrMsg = 'Specify handle to plot the separate constraints indiviudally as opposed to a global chi squared.'
    parser.add_argument('--plotSepConstr', help=sepConstrMsg, action="store_true")

    # ########################################################################################################
    argsPars = parser.parse_args()
    scanCard = vars(argsPars)

    modelName = scanCard['modelName']
    modelCase = scanCard['modelCase']
    psDict = {}

    # if scanCard['micrOmegasName'] is None:
    micrOmegasName = modelName

    try:
        newModel = phaseScannerModel(modelName, modelCase, micrOmegasName=micrOmegasName, writeToLogFile=True)
    except Exception as e:
        print('🔥' + Fore.RED + '  No such model in the database   🚒')
        print(e)
        raise

    plotDict = {}
    exprAxis = False
    for axisLabel in ['xAxis', 'yAxis', 'colorAxis']:
        if scanCard[axisLabel] == '':
            plotDict[axisLabel] = newModel.defaultPlot[axisLabel]
        else:
            if scanCard[axisLabel] not in newModel.allDicts.keys():
                exprAxis = True
            plotDict[axisLabel] = scanCard[axisLabel]

    teXAxisList = []
    if exprAxis is True:
        # xHandles = []
        # yHandles = []
        # colorHandles = []
        if scanCard['TeXlabels'] != '':
            for teXAxis in scanCard['TeXlabels'].split('|'):
                # print(teXAxis)
                # exit()
                teXAxisList.append(teXAxis)
        else:
            print("Need TeXlabels!")
            exit()

        for axisType in ['xAxis', 'yAxis', 'colorAxis']:

            if (scanCard[axisType] not in newModel.classDict.keys()) and (scanCard[axisType] != ''):

                paramList = scanCard[axisType].split('|')[0]
                for char in ['[', ']', ' ']:
                    paramList = paramList.replace(char, '')

                paramList = paramList.split(',')
                paramExpres = scanCard[axisType].split('|')[1]
                plotDict[axisType] = [paramList, paramExpres]

                # axisHandles.append([paramList, paramExpres])

            else:
                pass
                # axisHandles.append([wkFSmodel.classification[modelAttributes[axisType]], modelAttributes[axisType]])

    # ################## Limiting axis ranges ################################
    # pp(plotDict)
    # exit()
    xAxisLimits = []
    yAxisLimits = []

    if scanCard['xAxisLim'] is not None:
        xAxisLimits = convertToFloatList(scanCard['xAxisLim'])
        restrictTruthX = True
    else:
        restrictTruthX = False
        xAxisLimits = []

    if scanCard['yAxisLim'] is not None:
        yAxisLimits = convertToFloatList(scanCard['yAxisLim'])
        restrictTruthY = True
    else:
        restrictTruthY = False
        yAxisLimits = []
    restrictTruth = restrictTruthX or restrictTruthY
    # ########################################################################
    if scanCard['oRF']:
        resDir = getLatestFocusDir(newModel)
    elif scanCard['targetResDir'] != '':
        resDir = 'Dicts/' + scanCard['targetResDir']
    else:
        resDir = 'Dicts/'
    psDict = newModel.loadResults(targetDir=resDir)

    if scanCard['filterByAttrs'] is not '':

        cutDict = makeCutDictFromStr(scanCard['filterByAttrs'])
        psDict = newModel.filterDictByCutDict(psDict, cutDict)

    modelPlotter = dictPlotting(newModel)
    # print(newModel.allDicts.keys())
    # exit()
    # print(len(psDict))
    # newModel.exportPSDictCSV(psDict, ['Higgs', 'mTop', 'ThetaHiggs', 'TopYukawa', 'HiggsTrilin'])

    modelPlotter.plotModel(psDict, plotDict['xAxis'], plotDict['yAxis'], plotDict['colorAxis'], colorMap=scanCard['colorMap'],
                           useChi2AsTest={'Enable': True, 'Chi2UpperBound': 20.52, 'TestStatistic': 'ChiSquared'},
                           TeXAxis=teXAxisList, pltName=scanCard['pltName'])
    # modelPlotter.plotModel(psDict , 'tanBeta', [['tanBeta', 'Lambda'],  'tanBeta * Lambda'], 'mBottom',
    # TeXAxis = [r'$\Delta\Delta\Delta$'])
