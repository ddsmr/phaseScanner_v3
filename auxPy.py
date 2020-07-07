import json
import numpy as np

resPath = 'Results/SO11Hosotani_DummyCase/Dicts/TempDicts/ScanResults.SO11Hosotani_DummyCase_22-06-2020_16:29:55.json'

with open(resPath, 'r') as fileIn:
    psDict = json.load(fileIn)


attrsAdd = ['CrossSect', 'Error', 'LambdaMax', 'sin2ThWLambda', 'sin2ThWMKK5', 'a1YinvMKK5', 'a2LinvMKK5',
            'a3CinvMKK5', 'a4CinvLambda', 'a2LinvLambda', 'a2RinvLambda', 'sin2ThW']

for pointID in psDict.keys():
    for attrToAdd in attrsAdd:
        psDict[pointID][attrToAdd] = np.random.uniform()

# rndPoint = psDict[list(psDict.keys())[0]]

with open('fixedJson_2.json', 'w') as jsonOut:
    json.dump(psDict, jsonOut)
