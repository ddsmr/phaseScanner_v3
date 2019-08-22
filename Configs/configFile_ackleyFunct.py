'''
    ADD DOCUMENTATION !!!
'''

# Test engine , can be used as a template.
genEngine = 'ackleyFunct'
engVers = '0.1'

# #################   Dictionaries         #################

paramDict = {
    'x': {
        'LaTeX': r'$x$',
        'Constraint': {
            'Type': 'None'
        }
    },
    'y': {
        'LaTeX': r'$y$',
        'Constraint': {
            'Type': 'None'
        }
        }

}
attrDict = {
    'fAckley': {
        'LaTeX': r'$f_{Ac}(x, y)$',
        'Constraint': {
            'Type': 'CheckBounded',  # 'None', #
                    'ToCheck': {
                                'CentralVal': 0,
                                'TheorySigma': 0.5,
                                'ExpSigma': 0.5
                                }
        }
    }

}
calcDict = {
    'ChiSquared': {
        'LaTeX': r'$\chi^2_G$',
        'Calc': {'Type': 'ChiSquared'},
        'Constraint': {
            'Type': 'None'
        }
    }
}

# ### Optional dictionaries #####
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
    'DummyCase': {}
}

defaultPlot = {'xAxis': 'x', 'yAxis': 'y', 'colorAxis': 'fAckley'}
dictMinMax = {
              'x':    {'Min': -30.0, 'Max': 30.0},
              'y':     {'Min': -30.0, 'Max': 30.0},
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
