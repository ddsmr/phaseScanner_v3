import sys
sys.path.append('../')

from phaseScanner import *
from pprint import pprint as pp
import json
import argparse
from datetime import date

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Utility script that looks into a focus dictionary specified by the user and examines the engoing or ended scan for a certain generation.')

    parser.add_argument('modelName', help='Model to query for the Multithread run.', type=str)
    parser.add_argument('auxCase',   help='Auxiliary case that describes the model case.', type=str)
    parser.add_argument('ThreadNb',  help='Thread Number to inspect.', type=int)
    parser.add_argument('GenNb',     help='Generation number to inspect.', type=int)

    # parser.add_argument('--Engine', default = None, help = 'By default the script will assume the name of the engine is the same as the model. Specify as string if otherwise. ', type = str)
    parser.add_argument('--FocusDate', default=None,
                        help='The script will by default look into the most recent run. Can be specified as a date e.g. "08-13-2019_11_33_29" ', type = str)

    argsPars = parser.parse_args()
    modelAttributes = vars(argsPars)

    modelName = modelAttributes['modelName']
    auxCase = modelAttributes['auxCase']

    micrOmegasName = modelName
    # if modelAttributes['Engine'] is None:
    #     generatingEngine = modelAttributes['modelName']
    # else:
    #     generatingEngine = modelAttributes['Engine']

    threadNbCheck = 'ThreadNb-' + str(modelAttributes['ThreadNb'])
    genToCheck = r'GenNb' + str(modelAttributes['GenNb'])
    engineVersion = '0.1'

    wkPSmodel = phaseScannerModel(modelName, auxCase, micrOmegasName=micrOmegasName, writeToLogFile=False)

    try:
        focusDate = ''
        dirEntries = os.listdir(wkPSmodel.resultDir + 'Dicts/')

        listOfDirs = []
        for dirEntry in dirEntries:
            if 'Focus' in dirEntry and ('.' not in dirEntry):
                listOfDirs.append(dirEntry.replace('Focus_', ''))

        focusDate_DateTime = checkListForLatestDate(listOfDirs)
        focusDate = convertDateTimeToStr(focusDate_DateTime)

    except Exception as e:
        print(e)
        pass

    print(focusDate)
    focusDir = wkPSmodel.resultDir + 'Dicts/Focus-' + focusDate + '/'

    printCentered(' Looking in dir ' + focusDir + ' ', fillerChar='█')
    print()

    try:
        dirFiles = os.listdir(focusDir)
    except Exception as e:
        print(Fore.RED + str(e))
        raise

    for jsonDict in dirFiles:
        if ('.json' in jsonDict) and (threadNbCheck in jsonDict) and ('Fixed' not in jsonDict):
            try:

                with open(focusDir + jsonDict) as inFile:
                    jsonContent = inFile.readline()

                # strTest = re.compile(r'T\d+-\d+-\d+-GenNb1')
                strTest = re.compile(r'Point T[\d-]+'+genToCheck+r'"')

                pointIDs = strTest.findall(jsonContent)
                print(pointIDs)
                print(delimitator)

                for pointID in pointIDs:
                    strJson = re.compile(pointID + r': ')
                    # print(strJson.split(jsonContent))
                    # print(delimitator)

                    afterPointID = strJson.split(jsonContent)[1]

                    # print(afterPointID)
                    # print(delimitator)

                    bracketStr = re.compile(r'}{')
                    dictStr = bracketStr.split(afterPointID)[0]

                    dataDict = json.loads(dictStr)
                    printCentered(pointID[:-1], fillerChar='-')
                    pp(dataDict)
                    print(delimitator2)

            except Exception as e:
                print(e)
                printCentered('❎ Cannot open ' + jsonDict, color=Fore.RED, fillerChar='-')

        elif ('.json' in jsonDict) and (threadNbCheck in jsonDict) and ('Fixed' in jsonDict):

            with open(focusDir + jsonDict) as inFile:
                jsonContent = json.load(inFile)

            for pointKey in jsonContent.keys():
                if genToCheck in pointKey:
                    printCentered(pointKey, fillerChar='-')
                    pp(jsonContent[pointKey])

                    # pp(jsonContent[pointKey].get('Particles'))
