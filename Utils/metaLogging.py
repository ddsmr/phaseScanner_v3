'''
    Module used to log actions in phase scanning.
'''
from time import gmtime, strftime
import json

def writeToLogFile_InitModel(phaseScannerModel ):
    '''
        Function to write to log file whenever the user is prompter with a new initalisation of the model.

        Attributes:
            - phaseScannerModel       ::      any instance of a phaseScannerModel class.


        Returns:
            - None
            - Writes to file Logs/<modelName + caseHandle>/ scanLog.log
    '''

    initTime = strftime("%d-%m-%Y_%H:%M:%S", gmtime())

    logFile = open(phaseScannerModel.logDir + 'scanLog.log', 'a')
    logFile.write("-"*100 + '\n')
    logFile.write("Initialised model @ " + initTime  + ' with attributes:\n')

    logFile.write("Engine ::" + phaseScannerModel.genEngine + '\n')
    logFile.write("Version :: " + phaseScannerModel.engineVersion  + '\n')

    logFile.write("Model Name: " + phaseScannerModel.modelName + '\n')
    logFile.write("Case Name: " + phaseScannerModel.case + '\n')
    logFile.write("Description: " + phaseScannerModel.description + '\n\n')

    # logFile.write("Templates: \n")
    # logFile.write(phaseScannerModel.templateData + '\n')

    logFile.write("Parameters: \n")
    logFile.write(json.dumps(phaseScannerModel.params)   + '\n')

    logFile.write("Attr: \n")
    logFile.write(json.dumps(phaseScannerModel.modelAttrs)   + '\n')

    # logFile.write("Couplings: \n")
    # logFile.write(json.dumps(phaseScannerModel.rgflow)   + '\n')
    logFile.write("-"*100 + '\n\n')

    logFile.write("Calculated Attributes: \n")
    logFile.write(json.dumps(phaseScannerModel.calc)   + '\n')
    logFile.write("-"*100 + '\n\n')

    logFile.close()

    return None

def writeToLogFile_Action(phaseScannerModel, actionStr, scanType):
    '''
        External class function to write to the corresponding log file of the model specified in phaseScannerModel when user performs and action (start/finish) of an ExploreScan.

        Attributes:
            - phaseScannerModel   ::      any instance of a phaseScannerModel class
            - actionStr ::      actionString to be wrote to the log file.
            - scanType  ::      Type of scan.

        Return:
            - None
            Writes to log file.
    '''

    logFile = open(phaseScannerModel.logDir + 'scanLog.log', 'a')
    logFile.write('*'*100 + '\n')
    logFile.write('Action : '+ '@ ' + strftime("%d/%m/%Y -- %H:%M:%S", gmtime()) + '  ' + actionStr + ' '+ scanType +' Scan :: ' + phaseScannerModel.modelName + phaseScannerModel.case.replace(" ","") + '\n')

    logFile.write('*'*100 + '\n\n')
    logFile.close()

    return None
