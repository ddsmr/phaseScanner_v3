'''
    ADD DOCUMENTATION !!!
'''
import os

# Test engine , can be used as a template.
# engineDir = ''
# FSDir = ''
# runCMD = ''
genEngine = 'testEngine'
engVers = '6.0'

###############################     Dictionaries         ###########################################

paramDict = {
    'Lambda': {
        'LaTeX': r'$\lambda$',
        'Constraint': {
            'Type': 'None'
        }
    },
    'Kappa': {
        'LaTeX': r'$\kappa$',
        'Constraint': {
            'Type': 'None'
        }
    },
    'tanBeta': {
        'LaTeX': r'$ \tan \beta$',
        'Constraint': {
            'Type': 'HardCutMore',
            'ToCheck' : 0
        }

    }

}
attrDict = {
'mBottom':{
    'LaTeX': r'$m_{b} (GeV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None', #
                'ToCheck': {
                            'CentralVal': 4.18,
                            'TheorySigma': 0.005,
                            'ExpSigma': 0.04
                            }
    }
}

}
calcDict={
'ChiSquared':{
    'LaTeX': r'$\chi^2_G$' ,
    'Calc' : {'Type':'ChiSquared'},
    'Constraint': {
        'Type': 'None'
    }
},
'LogL':{
    'LaTeX': r'$\log L$' ,
    'Calc' : {'Type':'ChiSquared'},
    'Constraint': {
        'Type': 'None'
    }
},
'testCalc':{
    'LaTeX': r'$\Delta_{int}$' ,
    'Marker': 'X',
    'Calc' : {'Type':'InternalCalc',
              'ToCalc': {'ParamList':['Lambda', 'Kappa', 'tanBeta', 'mBottom'],
                         'Expression': "Lambda**2 + mBottom / 2 + Kappa * tanBeta"}
              },
    'Constraint': {
        'Type': 'None',#<<<<<
        'ToCheck': {
                        'CentralVal': 28.6E-10,
                        'TheorySigma': 800.0,
                        'ExpSigma': 0.0
                        }
                    }

},

'extTest':{
    'LaTeX': r'$\Delta a_{\mu}$' ,
    'Marker': 'O',
    'Calc' : {'Type':'ExternalCalc',
              'Routine': 'testExtCalc',
              'Method' : 'testRoutine',
              'ParamList': ['Lambda', 'Kappa', 'tanBeta']
              },


    'Constraint': {
        'Type': 'None',#<<<<<
        'ToCheck': {
                        'CentralVal': 100,
                        'TheorySigma': 1.0,
                        'ExpSigma': 0.0
                        }
                    }

}

}

#### Optional dictionaries #####
# noneAttr = []
# plotFormatting = {
#      'failPlot' : {'alpha':0.5, 'lw' :0, 's':100},
#      'passPlot' : {'alpha':1,   'lw' : 0.6, 's':240},
#      'fontSize' : 40
#
#       # 'failPlot' : {'alpha':0.1, 'lw' :0, 's':30},
#       # 'passPlot' : {'alpha':1,   'lw' : 0.17, 's':140}
#       # 'fontSize' : 30
#
# }

# from collections import OrderedDict

# rndDict = OrderedDict ([  ('Check-0', {'ToPick': ['Lambda', 'Kappa', 'tanBeta'],
#                                        'ToCheck': [],
#                                        'ToSet' : [],
#                                        'Pass' : 'Success',
#                                        'Fail' : 'Check-0'}
#                           )
#                         ])
# toSetDict = {}
# condDict = {}

replacementRules = {
'DummyCase' :{}
}

# rgflowDict ={
# }
dictMinMax = {
              'tanBeta':    {'Min': 10.0, 'Max': 40.0},
              'Lambda':     {'Min': 0.001, 'Max': 0.999},
              'Kappa':      {'Min': 0.001, 'Max': 0.999}
              }
# sigmasDict = {
#              'tanBeta': 1.5,
#              'Lambda':  0.05,
#              'Kappa':  0.05
#              }

#
# calcDict={
# 'ChiSquared':{
#     'LaTeX': r'$\chi^2_G$' ,
#     'Calc' : {'Type':'ChiSquared'},
#     'Constraint': {
#         'Type': 'None'
#     }
# },
# 'testCalc':{
#     'LaTeX': r'$\Delta a_{\mu}$' ,
#     'Marker': 'X',
#     'Calc' : {'Type':'InternalCalc',
#               'ToCalc': {'ParamList':['Lambda', 'Kappa', 'tanBeta', 'mBottom'],
#                          'Expression': "Lambda**2 + mBottom / 2 + Kappa * tanBeta"}
#               },
#     'Constraint': {
#         'Type': 'None',#<<<<<
#         'ToCheck': {
#                         'CentralVal': 28.6E-10,
#                         'TheorySigma': 800.0,
#                         'ExpSigma': 0.0
#                         }
#                     }
#
# }
#
# }

# particleDict = {
# 'mBottom':{
#     'LaTeX': r'$m_{b} (GeV)$',
#     'Constraint': {
#         'Type': 'CheckBounded',#'None', #
#                 'ToCheck': {
#                             'CentralVal': 4.18,
#                             'TheorySigma': 0.005,
#                             'ExpSigma': 0.04
#                             }
#     }
# }
# }



# classificationDict = {'Params': parameterDict,
#                       'Particles' : particleDict ,
#                       'Couplings' : rgflowDict ,
#                       'Calc' : calcDict
#                       }
