import argparse
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


if __name__ == '__main__':
    # #################################      Arguments      ###########################################
    parser = argparse.ArgumentParser(description='Process the inputs for the plotting function')
    parser.add_argument('modelName', help=Fore.GREEN + 'Name of the model to be initialiased.' + Style.RESET_ALL)
    parser.add_argument('modelCase', help=Fore.GREEN + 'Case to be handled.' + Style.RESET_ALL)
    # parser.add_argument('--CustomRun', default = None, help = 'Use flag to run custom user defined script.')

    parser.add_argument("-x", '--xAxis', help='Attribute to plot on the x Axis. Default specified in config',
                        type=str, default='')
    parser.add_argument("-y", '--yAxis', help='Attribute to plot on the y Axis. Default specified in config',
                        type=str, default='')
    parser.add_argument("-c", '--colorAxis', help='Attribute to plot on the color Axis. Default specified in config',
                        type=str, default='')
    parser.add_argument('-oRF', help='Open the latest focus directory for plotting. Enable to true',
                        action="store_true")
    parser.add_argument('--targetResDir', default='', help='Open the specific result directory for plotting.')
    parser.add_argument('--colorMap', default='winter_r', help='Color map to be used. Default winter_r')

    axisMsg = 'Handle to specify if the axis are restricted. Set to string of the form e.g. "[100, 200]"'
    parser.add_argument('--xAxisLim', help=axisMsg, type=str)
    parser.add_argument('--yAxisLim', help=axisMsg, type=str)

    exprAxisMsg = Fore.RED + 'DEFAULT: False ' + Style.RESET_ALL \
                           + ('Handle to specify if the axis are expressions. If set to TRUE , the axis should be '
                              'entered as a string consisting of [param1, param2, ...] | expr(param1, param2, ...),'
                              'with the | delimitator.  E.g. -x="[BMu, Mu, aHat]| BMu / Mu  + 2* aHat" ')
    parser.add_argument('--exprAxis', help=exprAxisMsg, type=bool, default=False)

    texLabelMsg = ('Labels for the axis if exprAxis is used. Enter raw TeX strings for each axis that requires a '
                   'custom label. E.g. if we have 2 custom axis we enter "$\alpha$ | $\beta$" for their formatting.')
    parser.add_argument('--TeXlabels', help=texLabelMsg, type=str)

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
    for axisLabel in ['xAxis', 'yAxis', 'colorAxis']:
        if scanCard[axisLabel] == '':
            plotDict[axisLabel] = newModel.defaultPlot[axisLabel]
        else:
            plotDict[axisLabel] = scanCard[axisLabel]

    # ################## Limiting axis ranges ################################

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

    modelPlotter = dictPlotting(newModel)
    modelPlotter.plotModel(psDict, plotDict['xAxis'], plotDict['yAxis'], plotDict['colorAxis'],
                           useChi2AsTest={'Enable': True, 'Chi2UpperBound': 11.0705, 'TestStatistic': 'ChiSquared'})
    # modelPlotter.plotModel(psDict , 'tanBeta', [['tanBeta', 'Lambda'],  'tanBeta * Lambda'], 'mBottom',
    # TeXAxis = [r'$\Delta\Delta\Delta$'])
