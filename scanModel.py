import argparse
import os
# from phaseScanner import *
from phaseScanner import phaseScannerModel, checkListForLatestDate, convertDateTimeToStr, getLatestFocusDir

# from Utils.Gmail.gMailModule import *
from Utils.printUtils import *


# def getLatestFocusDir(psObject):
#     '''
#         Given a psObject the function will get the latest focus directory from the Results directory.
#     '''
#     try:
#         # focusDate = ''
#         dirEntries = os.listdir(psObject.resultDir + 'Dicts/')
#
#         listOfDirs = []
#         for dirEntry in dirEntries:
#             if 'Focus' in dirEntry and ('.' not in dirEntry):
#                 listOfDirs.append(dirEntry.replace('Focus_', ''))
#
#         focusDate_DateTime = checkListForLatestDate(listOfDirs)
#         focusDateTime_str = convertDateTimeToStr(focusDate_DateTime)
#
#     except Exception as e:
#         print(e)
#         raise
#     # print(focusDate)
#     # exit()
#
#     focusDir = 'Dicts/Focus-' + focusDateTime_str + '/'
#     return focusDir


def _createFocusRunCard(algorihm, psDict, numbOfCores, targetThreads, psObject):
    '''
        Provided the algorithm the function gives bakc the parameters for the focus scan.
    '''
    focusCard = {}
    if 'diffEvol' in algorihm:
        focusCard['nbOfPoints'] = len(list(psDict.keys()))
        focusCard['nbOfCores'] = numbOfCores
        focusCard['chi2LowerBound'] = 10.0
        focusCard['sortByChiSquare'] = False
        focusCard['statistic'] = 'ChiSquared'
        outDict = psDict

    elif algorihm == 'singleCellEvol':
        focusCard['nbOfPoints'] = numbOfCores
        focusCard['nbOfCores'] = numbOfCores
        focusCard['chi2LowerBound'] = 10.0
        focusCard['sortByChiSquare'] = True
        focusCard['statistic'] = 'ChiSquared'

    elif algorihm == 'metropolisHastings':
        focusCard['nbOfPoints'] = numbOfCores
        focusCard['nbOfCores'] = numbOfCores
        focusCard['chi2LowerBound'] = -3.0
        focusCard['sortByChiSquare'] = True
        focusCard['statistic'] = 'LogL'

    if (targetThreads is True) and (algorihm != 'diffEvol'):
        dictOfThreadDicts = {}
        # sortedListOfPoints =  sorted(psDict.items(), key=lambda kv: kv[0])
        sortedListOfKeys = sorted(psDict.keys(), key=lambda kv: kv)

        for pointID in sortedListOfKeys:
            thrNb = pointID.split(' ')[1].split('-')[0]

            if thrNb not in dictOfThreadDicts.keys():
                dictOfThreadDicts[thrNb] = {}
                dictOfThreadDicts[thrNb].update({pointID: psDict[pointID]})

            else:
                dictOfThreadDicts[thrNb].update({pointID: psDict[pointID]})

        outDict = {}

        chi2List = []
        for threadNb in dictOfThreadDicts.keys():
            outDict.update(psObject.getTopNChiSquaredPoints(dictOfThreadDicts[threadNb], 1)[0][0])
            chi2List.append(psObject.getTopNChiSquaredPoints(dictOfThreadDicts[threadNb], 1)[1])

    else:
        outDict = psDict

    return focusCard, outDict


if __name__ == '__main__':

    # #################################      Arguments      ###########################################
    parser = argparse.ArgumentParser(description='Process the inputs for the desired run.')
    parser.add_argument('modelName', help=Fore.GREEN + 'Name of the model to be initialiased.' + Style.RESET_ALL)
    parser.add_argument('modelCase', default='', help=Fore.GREEN + 'Case to be handled.' + Style.RESET_ALL)

    parser.add_argument('--numberOfCores', default=8, help='Number Of Threads to use in the scanning procedure.',
                        type=int)
    parser.add_argument('--numberOfPointsExplore', default=80,
                        help='Number Of Points to scan for in the exploration scan.', type=int)
    exploreMsg = Fore.RED + ("Enable exploration running. NOTE that atributes marked as ExternalCalc are by default"
                             "ignored. Set ignoreExternal = True to enable external attributes.") + Style.RESET_ALL
    parser.add_argument("-rE", '--runExplore',  help=exploreMsg, action="store_true")

    parser.add_argument("-rF", '--runFocused',  help=Fore.RED + 'Enable focused running.' + Style.RESET_ALL,
                        action="store_true")
    parser.add_argument('--algFocus', help='Algorithm to run focus scan with. Default algorithm is diffEvol.',
                        default='diffEvol', type=str)
    parser.add_argument('-tT', '--targetThreads',  help='Set flag to target the files from the previous thread runs',
                        action="store_true")

    parser.add_argument('--targetResDir', default='', help='Descriptor that user wants to associate with the model')
    parser.add_argument('--targetSpecFile', default='', help='Descriptor that user wants to associate with the model')

    parser.add_argument('--Description', default='', help='Descriptor that user wants to associate with the model')
    parser.add_argument('--resumeGenRun',  help='Resume the latest run.', action="store_true")

    micrOmMsg = 'micrOmegas model name. If nothing is passed then micrOmegasName is taken the same as modelName.'
    parser.add_argument('--micrOmegasName', default=None, help=micrOmMsg)
    parser.add_argument("-spwn", '--spawnSubAlgorithms',  help='Algorithm to run focus scan with', action="store_true")

    # parser.add_argument('--nbOfSigmasRelax', default = 1, help = 'Number Of Sigmas for the focus scan to relax.',
    # type = int)
    # parser.add_argument("-t", '--targetThread', default = False, help = 'Set to True to target', action="store_true")

    # parser.add_argument("-e", '--sendCompletionEmail', help='Enable completion email from being sent with the
    # provided params.', action="store_true")
    # parser.add_argument('--xAxis', default='mTop', help='X axis for the plot sent in the email.')
    # parser.add_argument('--yAxis', default='Higgs', help='Y axis for the plot sent in the email.')
    # parser.add_argument('--colorAxis', default='c0', help='Color axis for the plot sent in the email.')
    #
    # parser.add_argument("-g", '--pushToGit', help='Push by default to the Results_Auto git repo the results when
    # done.', action="store_true")
    # parser.add_argument("-FULL", '--fullBonanza',  help='Set to True for the full bonanza: Explore ≈ 5000 pts,
    # Focus, sendCompletionEmail, and pushToGit',action="store_true")

    parser.add_argument("-d", '--debug', help=Fore.RED + 'Enable to debug.' + Style.RESET_ALL, action="store_true")
    #####################################################################################################

    argsPars = parser.parse_args()
    scanCard = vars(argsPars)
    # pprint.pprint(modelAttributes)

    modelName = scanCard['modelName']
    modelCase = scanCard['modelCase']
    numbOfCores = scanCard['numberOfCores']
    debug = scanCard['debug']
    enableSubSpawn = scanCard['spawnSubAlgorithms']
    psDict = {}

    if scanCard['micrOmegasName'] is None:
        micrOmegasName = modelName

    try:
        newModel = phaseScannerModel(modelName, modelCase, micrOmegasName=micrOmegasName, writeToLogFile=True)
    except Exception as e:
        print('🔥' + Fore.RED + '  No such model in the database   🚒')
        print(e)
        raise

    if scanCard['runExplore'] is True:
        psDict = newModel.runMultiThreadExplore(numberOfPoints=scanCard['numberOfPointsExplore'],
                                                nbOfThreads=numbOfCores, debug=debug, ignoreExternal=True,
                                                ignoreInternal=False)

    if scanCard['runFocused'] is True and scanCard['resumeGenRun'] is False:
        specFile = ''
        if scanCard['targetThreads'] is True and scanCard['targetResDir'] == '':
            resDir = getLatestFocusDir(newModel)
        elif scanCard['targetResDir'] != '':
            resDir = 'Dicts/' + scanCard['targetResDir']
        elif scanCard['targetSpecFile'] != '':
            resDir = 'Dicts/'
            specFile = scanCard['targetSpecFile']
        else:
            resDir = 'Dicts/'

        # scanCard['targetThreads'] = True

        if bool(psDict) is False:
            psDict = newModel.loadResults(targetDir=resDir, specFile=specFile)

        algCard, psDict = _createFocusRunCard(scanCard['algFocus'], psDict, numbOfCores,
                                              scanCard['targetThreads'], newModel)

        # pp(psDict)
        # newModel.reRunMultiThread(psDict, numbOfCores=1)
        # newModel.reRunMultiThread(psDict, numbOfCores = algCard['nbOfCores'])
        # exit()

        newModel.runGenerationMultithread(psDict, numbOfCores=algCard['nbOfCores'], numberOfPoints=algCard['nbOfPoints'],
                                          chi2LowerBound=algCard['chi2LowerBound'], debug=debug,
                                          algorithm=scanCard['algFocus'], sortByChiSquare=algCard['sortByChiSquare'],
                                          statistic=algCard['statistic'], enableSubSpawn=enableSubSpawn,
                                          ignoreExternal=True)

    elif scanCard['resumeGenRun'] is True:
        newModel.resumeGenRun()
