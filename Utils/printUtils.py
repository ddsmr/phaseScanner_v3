import os
from pprint import pprint as pp
from colorama import Fore, Back, Style
from time import gmtime, strftime



#### Printing utilities ####
nbrTerminalRows, nbrTerminalCols = os.popen('stty size', 'r').read().split()
nbrTerminalRows = int(nbrTerminalRows)
nbrTerminalCols = int(nbrTerminalCols)
delimitator = '\n' + '▓' * nbrTerminalCols + '\n'
delimitator2 = '\n' + '-' * nbrTerminalCols + '\n'

#### FNULL declaration to supress cmd line output ####
FNULL = open(os.devnull, 'w')


def printCentered(stringToPrint, color='', fillerChar=' '):
    '''
        Utility function that prints with a color the string defined in stringToPrint, centered in the console, with a fillerChar.

        Arguments:
            - stringToPrint     ::           String to be printed in the center of the console line.
            - color             ::           Color in which the string will be printed in.
            - fillerChar        ::           Character to fill the rest of the console line.

        Returns:
            - None

    '''
    rows, columnsTerm = os.popen('stty size', 'r').read().split()

    stringToPrint = fillerChar *  int ( (int(columnsTerm) - len(stringToPrint)) / 2) + color + stringToPrint + Style.RESET_ALL + fillerChar *  int ( (int(columnsTerm) - len(stringToPrint)) / 2)

    print(stringToPrint)

    return None

def printHeader(scanType, scanStage, numberOfCores):
    '''
        Prints out either a start or an end header for the scan, either Explore or Focus, with the number of processes being run.

        Arguments:
            - scanType      ::      Type of scan (Explore, Focus, Rerun, or other)
            - scanStage     ::      Stage of the scan (e.g. start, finish, etc.)
            - numberOfCores  ::      Number of Processes that are being run.

        Returns:
            - None
    '''
    rows, columnsTerm = os.popen('stty size', 'r').read().split()

    if scanType == 'Explore':
        printColor = Fore.GREEN
    elif scanType == 'Focus':
        printColor = Fore.BLUE
    elif scanType == 'ReRun':
        printColor = Fore.LIGHTYELLOW_EX
    elif scanType == 'DMrelicDens':
        printColor = Fore.BLUE
    else:
        printColor = ''
    scanColor = Fore.RED



    headerString = '-' * int(columnsTerm)
    infoString = scanColor + ' Cores : ' +str(numberOfCores) + printColor + '. Stage : ' + scanColor + scanType +  '. '+  scanStage + printColor + ' at ' + strftime("%d/%m/%Y  at %H:%M:%S ", gmtime())
    infoStringNoFormat = ' Cores : ' + str(numberOfCores) + '. Stage : '+ scanType + '. ' + scanStage + ' at ' + strftime("%d/%m/%Y  at %H:%M:%S ", gmtime())

    headerString2 = '*' *  int ( (int(columnsTerm) - len(infoStringNoFormat)) / 2) +  infoString +'*' *  int ( (int(columnsTerm) - len(infoStringNoFormat)) / 2)

    print (printColor + headerString)
    print (printColor + headerString2)
    print (printColor + headerString)


    return None

def printGenMsg(genNb, chi2Min, threadNumber, printStr, percChange):
    '''
    '''
    print(delimitator2)
    print ('\n'+'For ' +Fore.GREEN+'Gen# ' + str(genNb)+ Style.RESET_ALL +
            ' the best' + Fore.RED +  ' χ² of ', round(chi2Min,4) ,
            Fore.YELLOW + ' from ThreadNb :' + str(int(threadNumber)+1) ,
             # ' from point ', minKey ,
            "   |   ", Fore.BLUE + printStr +  Style.RESET_ALL, percChange , '%' )
    print(delimitator2)
    return None
