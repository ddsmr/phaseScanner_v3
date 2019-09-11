import sys
import argparse
from printUtils import *
import math

import matplotlib.pyplot as plt

import numpy as np
import os
import subprocess

from halo import Halo

sys.path.append('../')
from phaseScanner import phaseScannerModel, checkListForLatestDate, convertDateTimeToStr, getLatestFocusDir


colorPallete = [(0.2980392156862745, 0.4470588235294118, 0.6901960784313725), (0.8666666666666667, 0.5176470588235295, 0.3215686274509804), (0.3333333333333333, 0.6588235294117647, 0.40784313725490196), (0.7686274509803922, 0.3058823529411765, 0.3215686274509804), (0.5058823529411764, 0.4470588235294118, 0.7019607843137254), (0.5764705882352941, 0.47058823529411764, 0.3764705882352941), (0.8549019607843137, 0.5450980392156862, 0.7647058823529411), (0.5490196078431373, 0.5490196078431373, 0.5490196078431373), (0.8, 0.7254901960784313, 0.4549019607843137), (0.39215686274509803, 0.7098039215686275, 0.803921568627451)]

# import seaborn as sns
# sns.set()
# sns.set_style("ticks")
# sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5, 'axes.facecolor': 'white',
#                                                 'patch.linewidth': 0.1, 'axis.linewidth': '.1'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process the inputs for the plotting function. Opens the latest focus directory for plotting.')
    parser.add_argument('modelName', help=Fore.GREEN + 'Name of the model to be initialiased.' + Style.RESET_ALL)
    parser.add_argument('modelCase', help=Fore.GREEN + 'Case to be handled.' + Style.RESET_ALL)
    # parser.add_argument('--CustomRun', default = None, help = 'Use flag to run custom user defined script.')

    # parser.add_argument('-oRF', help='Open the latest focus directory for plotting. Enable to true',
    #                     action="store_true")
    parser.add_argument('--targetResDir', default='', help='Open the specific result directory for plotting.')
    parser.add_argument('--chi2LowerBound', default=11.07, help='Default min chi2 value.', type=int)

    # axisMsg = 'Handle to specify if the axis are restricted. Set to string of the form e.g. "[100, 200]"'
    # parser.add_argument('--xAxisLim', help=axisMsg, type=str)
    # parser.add_argument('--yAxisLim', help=axisMsg, type=str)

    # ########################################################################################################
    argsPars = parser.parse_args()
    scanCard = vars(argsPars)

    modelName = scanCard['modelName']
    modelCase = scanCard['modelCase']
    chi2LowerBound = np.log10(scanCard['chi2LowerBound'])
    psDict = {}

    # if scanCard['micrOmegasName'] is None:
    micrOmegasName = modelName

    try:
        newModel = phaseScannerModel(modelName, modelCase, micrOmegasName=micrOmegasName, writeToLogFile=True)
    except Exception as e:
        print('🔥' + Fore.RED + '  No such model in the database   🚒')
        print(e)
        raise

    if scanCard['targetResDir'] == '':
        resDir = getLatestFocusDir(newModel)
    elif scanCard['targetResDir'] != '':
        resDir = 'Dicts/' + scanCard['targetResDir']

    genPlotDir = newModel.resultDir + resDir + 'GenRunPlots/'
    subprocess.call('mkdir ' + genPlotDir, shell=True,  stdout=FNULL, stderr=subprocess.STDOUT)

    plotNumber = 0
    legendLabels = []
    # from matplotlib.font_manager import FontProperties
    #
    # font = FontProperties()
    # font.set_family('serif')
    # font.set_name('Helvetica')
    # font.set_style('italic')

    from matplotlib import rc
    # rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    # # for Palatino and other serif fonts use:
    rc('font', **{'family': 'serif', 'serif': ['Latin Modern Roman']})
    fontSizeGlobal = 37
    plt.rc('font', size=fontSizeGlobal)
    plt.rc('text', usetex=True)

    fig, (axMin) = plt.subplots(1, 1, sharex=True, figsize=(20, 10))
    for fileName in os.listdir(newModel.resultDir + resDir):
        if '.dat' in fileName:
            threadNb = int(fileName.split('.dat')[0][-1:])

            spinner = Halo(text='Plotting and exporting ' + Fore.RED + 'ThreadNb ' + str(threadNb) + Style.RESET_ALL,
                           spinner='dots')
            spinner.start()

            genDict = {'GenList': [], 'MinList': [], 'MeanList': [], 'StdList': []}
            with open(newModel.resultDir + resDir + fileName, 'r') as fileIn:
                genDataLines = fileIn.readlines()

            for lineNb, line in enumerate(genDataLines):
                splitLine = line.replace(' ', '').split('||')

                genNb = int(splitLine[0].split('-')[1])
                minChi2 = float(splitLine[1].split(':')[1])
                meanChi2 = float(splitLine[2].split(':')[1])
                stdChi2 = float(splitLine[3].split(':')[1])

                for listKey, varName in zip(genDict.keys(), [genNb, minChi2, meanChi2, stdChi2]):
                    genDict[listKey].append(varName)

            pltColor = colorPallete[plotNumber % len(colorPallete)]

            # Subplot 1 containing the minimum chi2 progression
            axMin.plot(np.log10(genDict['GenList']), np.log10(genDict['MinList']), c=pltColor)

            # axMin.set_title('Thread Number ' + str(threadNb))
            # axMin.set(ylabel=r'$\log_{10} \chi^2_{G}$')
            # axMin.legend([r'$\min(\chi^2)$'])

            # Subplot 2 containing the mean ± σχ^2 for the generational progression
            # p1 = axMean.plot(genDict['GenList'], np.log10(genDict['MeanList']), c=pltColor)
            #
            # # meanMinusList = [max(0, np.log10(meanVal - stdVal)) for meanVal, stdVal in zip(genDict['MeanList'], genDict['StdList'])]
            # meanPlusList = [np.log10(meanVal + stdVal) for meanVal, stdVal in zip(genDict['MeanList'], genDict['StdList'])]
            #
            # axMean.fill_between(genDict['GenList'], np.log10(genDict['MeanList']), meanPlusList, alpha=0.5, color=pltColor)
            # p2 = axMean.fill(np.NaN, np.NaN, alpha=0.5, c=pltColor)
            # axMean.legend([(p2[0], p1[0]), ], [r'$\overline{\chi^2} + \sigma_{\chi^2}$'])
            #
            # axMean.set(ylabel=r'$\log_{10} \chi^2_{G}$')
            # axMean.set(xlabel=r'Generation Number')
            plt.tight_layout()

            plotNumber += 1
            plotName = 'GenPlot-ThreadNb-' + str(threadNb)
            legendLabels.append(r'$\min(\chi^2)$' + ' Thread ' + str(threadNb))

            # plt.savefig(genPlotDir + plotName + '.pdf')
            spinner.stop_and_persist(symbol=Fore.GREEN + '✔' + Style.RESET_ALL,
                                     text='Done with Thread Nb ' + str(threadNb))

    axMin.legend(legendLabels, loc=1, fontsize=27)
    axMin.set(xlabel=r'$\log_{10} (G)$ ')
    axMin.set(ylabel=r'$\log_{10} (\chi^2_{G})$')

    axMin.axhline(y=chi2LowerBound, color='black', linestyle=(0, (5, 5)), linewidth=1.0)
    axMin.text(0.1, 1.3, r'$\log_{10} (\chi^2_{Bound})$',
               {'color': 'black', 'fontsize': 30, 'ha': 'center', 'va': 'center'})
    plt.show()
    # exit()
