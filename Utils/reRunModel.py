import sys
import json
import argparse
import os
# from .. import phaseScanner
sys.path.append('../')
from phaseScanner import phaseScannerModel, checkListForLatestDate, convertDateTimeToStr, getLatestFocusDir
from Utils.printUtils import *

# from Utils.Gmail.gMailModule import *


if __name__ == '__main__':

    # #################################      Arguments      ###########################################
    parser = argparse.ArgumentParser(description='Process the inputs for the desired run.')
    parser.add_argument('modelName', help=Fore.GREEN + 'Name of the model to be initialiased.' + Style.RESET_ALL)
    parser.add_argument('modelCase', default='', help=Fore.GREEN + 'Case to be handled.' + Style.RESET_ALL)

    parser.add_argument('--numberOfCores', default=8, help='Number Of Threads to use in the scanning procedure.',
                        type=int)

    parser.add_argument('-tT', '--targetThreads',  help='Set flag to target the files from the previous thread runs',
                        action="store_true")

    parser.add_argument('--targetResDir', default='', help='Descriptor that user wants to associate with the model')
    parser.add_argument('--targetSpecFile', default='', help='Descriptor that user wants to associate with the model')

    parser.add_argument('--Description', default='', help='Descriptor that user wants to associate with the model')

    micrOmMsg = 'micrOmegas model name. If nothing is passed then micrOmegasName is taken the same as modelName.'
    parser.add_argument('--micrOmegasName', default=None, help=micrOmMsg)

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
    parser.add_argument("-gC", '--getCalcOnly', help='Enable to only rerun for the calc Attributes.', action="store_true")
    parser.add_argument('--contRun', help='Enable to continue the last available rerun', action="store_true")

    parser.add_argument("-d", '--debug', help=Fore.RED + 'Enable to debug.' + Style.RESET_ALL, action="store_true")
    #####################################################################################################

    argsPars = parser.parse_args()
    scanCard = vars(argsPars)
    # pprint.pprint(modelAttributes)

    modelName = scanCard['modelName']
    modelCase = scanCard['modelCase']
    numbOfCores = scanCard['numberOfCores']
    debug = scanCard['debug']
    psDict = {}

    if scanCard['micrOmegasName'] is None:
        micrOmegasName = modelName

    try:
        newModel = phaseScannerModel(modelName, modelCase, micrOmegasName=micrOmegasName, writeToLogFile=True)
    except Exception as e:
        print('🔥' + Fore.RED + '  No such model in the database   🚒')
        print(e)
        raise

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

    if scanCard['contRun'] is True:
        contDir = getLatestFocusDir(newModel, keyWord='Rerun')
        with open(newModel.resultDir + contDir + 'Remaining_Done_PointIDs.json', 'r') as jsonIn:
            rerunStatus = json.load(jsonIn)
    else:
        rerunStatus = None

    psDict = newModel.loadResults(targetDir=resDir, specFile=specFile, ignoreIntegrCheck=True)

    # Filter the phase space dictionary if they've been already run
    if scanCard['contRun'] is True:
        for pointID in rerunStatus['Done points']:
            del psDict[pointID]

    newModel.reRunMultiThread(psDict, numbOfCores=scanCard['numberOfCores'], debug=scanCard['debug'],
                              getCalcOnly=scanCard['getCalcOnly'], rerunStatus=rerunStatus)
