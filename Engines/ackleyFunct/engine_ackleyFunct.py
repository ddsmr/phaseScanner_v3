from Utils.SmartRandomGenerator.smartRand import *
from time import gmtime, strftime
import math
from time import sleep
from random import uniform as randU


class engineClass:

    def __init__(self, phaseSpaceObj):
        '''
        '''

    def _getRequiredAttributes(self, paramsDict, threadNumber="0", runDict={}, pointKey=''):
        '''
        '''
        phaseSpaceDict = {}
        # pointKey = 'Point T' + threadNumber + "-" + str(int(random.uniform(1, 1000))) + strftime("-%d%m%Y%H%M%S", gmtime())
        phaseSpaceDict[pointKey] = paramsDict

        a_ct = 20
        b_ct = 0.2
        c_ct = 2 * math.pi

        auxSum1 = 0
        auxSum2 = 0
        d_ct = len(list(paramsDict.keys()))
        for modelParam in paramsDict.keys():
            auxSum1 += (paramsDict[modelParam])**2
            auxSum2 += math.cos(c_ct * paramsDict[modelParam])

        ackleyVal = -a_ct * math.exp(-b_ct * math.sqrt(auxSum1/d_ct)) - math.exp(auxSum2 / d_ct) + a_ct + math.exp(1)
        phaseSpaceDict[pointKey]['fAckley'] = ackleyVal

        # Put in a pause to simulate computational complexity
        time.sleep(0.5 * randU(0, 1))
        return phaseSpaceDict

    def _clean(self, threadNumber):
        '''
        '''
        return None

    def _check0Mass(self, phaseSpaceDict):
        '''
        '''
        return True

    def runPoint(self, paramsDict, threadNumber='0', debug=False):
        '''
        '''
        return None
