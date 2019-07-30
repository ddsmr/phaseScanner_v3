'''
    ADD DOCUMENTATION !!!
'''
import os
from collections import OrderedDict

from math import sin, cos
from scipy.special import jv as BesselJ
from scipy.special import yv as BesselY



# import platform
# sysInfo = platform.linux_distribution()
# mathScript = 'MathematicaScript'
# if '16.04' in sysInfo[1]:
#     mathScript = 'MathematicaScript'
# elif '18.04' in sysInfo[1]:
#     mathScript = 'wolframscript'
#
#
# runCMD = mathScript + ' -script SO11_Masses_v6.m'  ### ThreadNb-n where n=1,2, ...
# The directory of te Hosotani script
# engineDir = os.path.expanduser('~') + '/Documents/Hosotani_SO11/Mathematica'


genEngine = 'HosotaniSO11'
engVers = '6.0'

###############################     Dictionaries         ###########################################

paramDict = {
    'k': {
        'LaTeX': r'$k (GeV)$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'zL': {
        'LaTeX': r'$ z_L$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'c0': {
        'LaTeX': r'$ c_0$',
        'Constraint': {
            'Type': 'None'
        }
    },
    'c1': {
        'LaTeX': r'$ c_1$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'c2': {
        'LaTeX': r'$ c_2$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'c0Prime': {
        'LaTeX': r'$ c^{\prime}_0$',
        'Constraint': {
            'Type': 'None'

        }
    },

    'Mu1': {
        'LaTeX': r'$ \mu_{1}$',
        'Constraint': {
            'Type': 'None'

        }
    },

    'Mu11': {
        'LaTeX': r'$ \mu_{11}$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'Mu11Prime': {
        'LaTeX': r'$ \mu^{\prime}_{11} $',
        'Constraint': {
            'Type': 'None'

        }
    },

    'Mu2Tilde': {
        'LaTeX': r'$ \tilde{\mu_2}$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'Mu11': {
        'LaTeX': r'$ \mu_{11}$',
        'Constraint': {
            'Type': 'None'

        }
    },
    'Mu11Prime': {
        'LaTeX': r'$ \mu^{\prime}_{11} $',
        'Constraint': {
            'Type': 'None'

        }
    }



}
attrDict = {
'Higgs':  {
        'LaTeX': r'$m_H (GeV)$',
        'Marker': 'o',
        'Constraint': {
            'Type': 'CheckBounded',#'None'#
                    'ToCheck': {
                                'CentralVal': 125.18,
                                'TheorySigma': 1.25,
                                'ExpSigma': 0.16
                                }
                      }
              },

'mPsiDark':{
    'LaTeX': r'$m_{\psi_D} (GeV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None'#
                'ToCheck': {
                            'CentralVal': 2500.00,
                            'TheorySigma': 25.0,
                            'ExpSigma': 0.0
                            }
                  }
},
'mTau':{
    'LaTeX': r'$m_{\tau} (GeV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None', #
                'ToCheck': {
                            'CentralVal': 1.776,
                            'TheorySigma': 0.01776,
                            'ExpSigma': 0.00012
                            }
    }
},
###### NOTE THE NEUTRINO IS MEASURED IN eV directly from the script
'mNeutrino':{
    'LaTeX': r'$m_{\nu} (eV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None', #
                'ToCheck': {
                            'CentralVal': 0.1,
                            'TheorySigma': 1.0,
                            'ExpSigma': 0.0
                            }
    }
},
'mBottom':{
    'LaTeX': r'$m_{b} (GeV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None', #
                'ToCheck': {
                            'CentralVal': 4.18,
                            'TheorySigma': 0.0418,
                            'ExpSigma': 0.04
                            }
    }
},
'mTop':{
    'LaTeX': r'$m_{t} (GeV)$',
    'Marker': '^',
    'Constraint': {
        'Type': 'CheckBounded',#'None'#
                'ToCheck': {
                            'CentralVal':  172.44,
                            'TheorySigma': 1.724,
                            'ExpSigma': 0.9
                            }
                  }
},
'ThetaHiggs':{
    'LaTeX': r'$\langle \theta_H \rangle (rads)$',
    'Constraint': {
        'Type': 'None'
    }
},
'mZ0':{
    'LaTeX': r'$m_Z (GeV)$',
    'Constraint': {
        'Type': 'None',#'CheckBounded',#
                'ToCheck': {
                            'CentralVal': 91.1876,
                            'TheorySigma': 0.9118,
                            'ExpSigma': 0.0021
                            }
                  }
},
'mWpm':{
    'LaTeX': r'$m_{W^\pm} (GeV)$',
    'Constraint': {
        'Type': 'CheckBounded',#'None', #
                'ToCheck': {
                            'CentralVal': 80.379,
                            'TheorySigma': 0.8037,
                            'ExpSigma': 0.012
                            }
                  }

},
# 'Mu11': {
#     'LaTeX': r'$ \mu_{11}$',
#     'Constraint': {
#         'Type': 'None'
#
#     }
# },
# 'Mu11Prime': {
#     'LaTeX': r'$ \mu^{\prime}_{11} $',
#     'Constraint': {
#         'Type': 'None'
#
#     }
# },
'mZprime':{
    'LaTeX': r'''$m_{Z'} (GeV)$''',
    'Constraint': {
        'Type': 'HardCutMore',
        'ToCheck' : 2000
    }
},

'Triviality':{
    'LaTeX': r'''$T$''',
    'Constraint': {
        'Type': 'None'
    }

}
# ,
# 'TopYukawa':{
#     'LaTeX': r'''$y_t$''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# },
# 'HiggsTrilin':{
#     'LaTeX': r'''$\tau_H$''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# }
#
# ,
# 'TrilinRescSM':{
#     'LaTeX': r'''$1 - \tau_H / \tau_H^{SM} $''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# },
# 'YukawaRescSM':{
#     'LaTeX': r'''$1 - \frac{y_t}{y_t^{SM}}$''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# }
# ,
# 'CrossSect':{
#     'LaTeX': r'''$\sigma(hh) (fb)$''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# },
# 'Error':{
#     'LaTeX': r'''$\Delta_{HH}$''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# }
# ,
# 'CrossSectRescSM':{
#     'LaTeX': r'''$\sigma(hh) / \sigma^{SM}(hh) $''',
#     'Constraint': {
#         'Type': 'None'
#     }
#
# }


}

######### To define a test measure e.g. χ^2 or Log L the attribute must be of Type:'ChiSquared'
calcDict = {
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
            }


# ,
# 'mTopTower' :{
#     'LaTeX' : r'$\Omega_c h^2$' ,
#     'Calc' : {'Type':'ExternalCalc',
#               'Routine':'mTopTower',
#               'Method' : 'findFirstSol',
#               'ParamList': ['zL', 'c0', 'ThetaHiggs', 'k'] },
#
#     'Constraint' : {
#         'Type': 'None'
#     }
# }

# ,'Zprime' :{
#     'LaTeX' : r'''$Z' (GeV)$''' ,
#     'Calc' : {'Type':'ExternalCalc',
#               'Routine':'mTopTower',
#               'Method' : 'findFirstSol',
#               'ParamList': ['zL', 'c0', 'ThetaHiggs', 'k'] },
#
#     'Constraint' : {
#         'Type': 'HardCutMore',
#         'ToCheck' : 1234
#     }
# }

}



############### Min Max / Replacement Rules #
dictMinMax  = {
# 'Mu1':      {'Min':0.0, 'Max': 100.0},
# 'Mu2Tilde':  {'Min':0.0, 'Max': 100.0},
#
# 'Mu11':     {'Min':0.0, 'Max': 100.0},
# 'Mu11Prime': {'Min':0.0, 'Max': 100.0},
#
#
# 'c0':        {'Min': 0.0, 'Max': 1.0},
# 'c0Prime':   {'Min': 0.0, 'Max': 1.0},
# 'c1':        {'Min': 0.0, 'Max': 2.0},
# 'c2':       {'Min':  -3.0, 'Max': 3.0},
#
# 'k':        {'Min': 1000.0, 'Max': 10000000.0},
# 'zL':        {'Min': 10.0, 'Max': 2500.0}
###### Uncomment below to obtain the original solution #####
# 'Mu1':      {'Min': 11.7911, 'Max': 11.9747},
# 'Mu2Tilde':  {'Min': 0.7147, 'Max': 0.7190},
#
# 'Mu11':      {'Min': 0.1115, 'Max': 0.119},
# 'Mu11Prime': {'Min': 0.1228, 'Max': 0.1277},
#
#
# 'c0':        {'Min': 0.32176, 'Max': 0.3333},
# 'c0Prime':  {'Min': 0.5138, 'Max': 0.5331},
# 'c1':        {'Min': 0.0, 'Max': 0.0},
# 'c2':       {'Min': -0.6811, 'Max': -0.67135},
#
# 'k':        {'Min': 88462.008, 'Max': 88955.77},
# 'zL':        {'Min': 34.632, 'Max': 34.6673}
########### Restricted parameter range #############
'Mu1':      {'Min': 11.0, 'Max': 13.0},
'Mu2Tilde':  {'Min': 0.0, 'Max': 1.5},

'Mu11':      {'Min': 0.0, 'Max': 0.5},
'Mu11Prime': {'Min': 0.0, 'Max': 0.5},


'c0':        {'Min': 0.1, 'Max': 0.5},
'c0Prime':   {'Min': 0.4, 'Max': 0.7},
'c1':        {'Min': 0.0, 'Max': 0.2},
'c2':        {'Min': -1.0, 'Max': -0.5},

'k':         {'Min': 100000.0, 'Max': 300000.00},
'zL':        {'Min': 33.0, 'Max': 37.0}

}
replacementRules = {
'DummyCase' :{}
}


# classificationDict = {'Params': parameterDict,
#                       'Particles' : particleDict ,
#                       'Couplings' : rgflowDict ,
#                       'Calc' : calcDict
#                       }



plotFormatting = {
     'failPlot' : {'alpha':0.5, 'lw' :0,   's':100},
     'passPlot' : {'alpha':1,    'lw' : 0.6, 's':240},
     'fontSize' : 40

      # 'failPlot' : {'alpha':0.1, 'lw' :0, 's':30},
      # 'passPlot' : {'alpha':1,   'lw' : 0.17, 's':140}
      # 'fontSize' : 30

}
##############################################################################################################################

rndDict = OrderedDict ([  ('Check-0', {'ToPick': ['k', 'zL'],
                                       'ToCheck': ['mKK'],
                                       'ToSet' : [],
                                       'Pass' : 'Check-1',
                                       'Fail' : 'Check-0'}
                          ),
                          ('Check-1', {'ToPick' : ['c0', 'c0Prime', 'c2', 'Mu2Tilde', 'Mu11Prime', 'c1', 'Mu1',  'Mu11'],
                                       'ToCheck': [],
                                       'ToSet' : [],
                                       'Pass' : 'Success',
                                       'Fail' : 'Check-0'}
                          )
                          # ,
                          # ('Check-2', {'ToPick' : ['c0Prime'],
                          #              'ToSet' : [],
                          #              'ToCheck': [],#['cosThdiv2']
                          #              'Pass' : 'Check-3',
                          #              'Fail' : 'Check-0'}
                          # ),
                          # ('Check-3', {'ToPick' : ['c2', 'Mu2Tilde', 'Mu11Prime'],
                          #             'ToSet' : [],
                          #              'ToCheck': ['sinThdiv2-3'],
                          #              'Pass' : 'Check-4',
                          #              'Fail' : 'Check-1'}
                          # ),
                          # ('Check-4', {'ToPick' : ['c1', 'Mu1',  'Mu11'],
                          #              'ToSet' : [],
                          #              'ToCheck': ['sinThdiv2-4'],
                          #              'Pass' : 'Success',
                          #              'Fail' : 'Check-1'}
                          # )


                          # ('Check-5', {'ToPick' : [],
                          #              'ToSet' : [],
                          #              'ToCheck': ['FinalCond-Mu11Prime'],
                          #              'Pass' : 'Check-6',
                          #              'Fail' : 'Check-4'}
                          # ),
                          # ('Check-6', {'ToPick' : [],
                          #              'ToSet' : [],
                          #              'ToCheck': ['FinalCond-Mu11'],
                          #              'Pass' : 'Success',
                          #              'Fail' : 'Check-3'}
                          # )
                        ])

toSetDict = {
            # 'Mu11' :   {
            #            'ParamList' : ['zL', 'c0', 'c1', 'Mu1'],
            #            'ToSetExpr' : ' (4.18 / 172.44) * Mu1 * ( 1/(zL**(c0-c1)) ) * sqrt( (1+2*c0)/(1+2*c1) )'
            #            },
            # 'Mu11Prime':{
            #             'ParamCaseCheck' : {'ParamList' : ['c0', 'c2'],
            #                                 'Cases' : {'c0 < 0.5 and c2 < 0.5':   'Case-1',
            #                                            'c0 < 0.5 and c2 > 0.5':   'Case-2',
            #                                            'c0 > 0.5 and c2 < 0.5':   'Case-3',
            #                                            'c0 > 0.5 and c2 > 0.5':   'Case-4'}
            #                                 },
            #             'ParamList' : ['zL', 'c0', 'c2', 'Mu2Tilde'],
            #             'ToSetExpr' : {'Case-1':'(1.776 / 172.44) * ( 1/(zL**(c2-c0))  ) * Mu2Tilde * sqrt( (1-2*c2)/(1-2*c2) )',
            #                            'Case-2':'(1.776 / 172.44) * ( 1/(zL**(1/2-c0)) ) * Mu2Tilde * sqrt( (1-2*c0)/(2*c2-1) )',
            #                            'Case-3':'(1.776 / 172.44) * ( 1/(zL**(c2-1/2)) ) * Mu2Tilde * sqrt( (2*c0-1)/(1-2*c2) )',
            #                            'Case-4':'(1.776 / 172.44) *                        Mu2Tilde * sqrt( (2*c0-1)/(2*c2-1) )'}
            #
            # }
}


betaH = 0.0
alphaH = 10.0
tryCountLimit = 5

# print(-(cos( *0.1/2) )**2 , -(cos( alphaH*0.1/2) )**2 )
# exit()
condDict = {
            'mKK': {
                    'ParamList' : ['k', 'zL'],
                    'ToCheckExpr' : "(3.14159 * k ) / (zL - 1)",
                    'ToCheckMinBound' : 4100,
                    'ToCheckMax' : None,
                    'Description' : 'Should be above the LHC KK mass limit for RS1.'
                    },
            'sinTh2': {
                    'ParamList' : ['k', 'zL'],
                    'ToCheckExpr' : "-2*(- ((80.379 / k) * 1 * sin( (80.379 / k) *(1- zL) )) )*((1 + 1/( ((80.379 / k)**2)* zL ) ) * sin( (80.379 / k) *(1- zL) ) + ( 1 / (80.379 / k) - 1/((80.379 / k) * zL) ) * cos( (80.379 / k) *(1- zL) )  )/ (80.379 / k)",
                    'ToCheckMinBound' : (sin (betaH*0.1))**2 ,
                    'ToCheckMax' : (sin(alphaH*0.1))**2,
                    'Description' : 'Check that the W boson mass can be achieved with the right <θH>.'
                    },
            'sinThdiv2-2': {
                    'ParamList' : ['k', 'zL', 'c0'],
                    'ToCheckExpr' : "-(- ( (1/2) * np.pi * sqrt(1 * zL) * (172.44 / k) * ( - BesselJ(0.5+c0, (172.44 / k) * zL) * BesselY(0.5 + c0, 1 * (172.44 / k)) + BesselJ(0.5 + c0, 1 * (172.44 / k)) * BesselY(0.5 + c0, (172.44 / k) * zL) )  ))*(((1/2) * np.pi * sqrt(1 * zL) * (172.44 / k) * (  - BesselJ(-0.5 + c0, (172.44 / k) * zL) * BesselY(-0.5 + c0, 1 * (172.44 / k)) + BesselJ(-0.5 + c0, 1 * (172.44 / k)) * BesselY(-0.5 + c0, (172.44 / k) * zL) )   ))",
                    'ToCheckMinBound' : (sin (betaH*0.1/2))**2 ,
                    'ToCheckMax' : (sin(alphaH*0.1/2))**2,
                    'Description' : 'Check that the Top mass can be achieved with the right <θH>.'
                    },
            'sinThdiv2-3': {
                    'ParamList' : ['k', 'zL', 'c0', 'Mu2Tilde', 'Mu11Prime', 'c2'],
                    'ToCheckExpr' : "-((- ( (1/2) * np.pi * sqrt(1 * zL) * (1.776 / k)  * ( - BesselJ(0.5+c0, (1.776 / k)  * zL) * BesselY(0.5 + c0, 1 * (1.776 / k) ) + BesselJ(0.5 + c0, 1 * (1.776 / k) ) * BesselY(0.5 + c0, (1.776 / k)  * zL) )  ))*(((1/2) * np.pi * sqrt(1 * zL) * (1.776 / k)  * (  - BesselJ(-0.5 + c0, (1.776 / k)  * zL) * BesselY(-0.5 + c0, 1 * (1.776 / k) ) + BesselJ(-0.5 + c0, 1 * (1.776 / k) ) * BesselY(-0.5 + c0, (1.776 / k)  * zL) )   ))+(Mu2Tilde**2) * (- ( (1/2) * np.pi * sqrt(1 * zL) * (1.776 / k)  * ( - BesselJ(0.5+c0, (1.776 / k)  * zL) * BesselY(0.5 + c0, 1 * (1.776 / k) ) + BesselJ(0.5 + c0, 1 * (1.776 / k) ) * BesselY(0.5 + c0, (1.776 / k)  * zL) )  ))*( (1/2) * np.pi * sqrt(1 * zL) * (1.776 / k) * ( BesselJ(0.5+c0, (1.776 / k)*1 ) * BesselY( -0.5+c0, zL*(1.776 / k) )  - BesselJ(-0.5+c0,  (1.776 / k)*zL) *  BesselY(0.5+c0, 1*(1.776 / k) )) )*((1/2) * np.pi * sqrt(1 * zL) * (1.776 / k)  * (  - BesselJ(-0.5 + c2, (1.776 / k)  * zL) * BesselY(-0.5 + c2, 1 * (1.776 / k) ) + BesselJ(-0.5 + c2, 1 * (1.776 / k) ) * BesselY(-0.5 + c2, (1.776 / k)  * zL) )   )*( (1/2) * np.pi * sqrt(1 * zL) * (1.776 / k) * ( BesselJ(0.5+c2, (1.776 / k)*1 ) * BesselY( -0.5+c2, zL*(1.776 / k) )  - BesselJ(-0.5+c2,  (1.776 / k)*zL) *  BesselY(0.5+c2, 1*(1.776 / k) )) )/ ((Mu11Prime**2)*(( (1/2) * np.pi * sqrt(1 * zL) * (1.776 / k) * ( BesselJ(0.5+c2, (1.776 / k)*1 ) * BesselY( -0.5+c2, zL*(1.776 / k) )  - BesselJ(-0.5+c2,  (1.776 / k)*zL) *  BesselY(0.5+c2, 1*(1.776 / k) )) )**2)-(((1/2) * np.pi * sqrt(1 * zL) * (1.776 / k)  * (  - BesselJ(-0.5 + c2, (1.776 / k)  * zL) * BesselY(-0.5 + c2, 1 * (1.776 / k) ) + BesselJ(-0.5 + c2, 1 * (1.776 / k) ) * BesselY(-0.5 + c2, (1.776 / k)  * zL) )   )**2)))",
                    'ToCheckMinBound' : (sin (betaH*0.1/2))**2 ,
                    'ToCheckMax' : (sin(alphaH*0.1/2))**2,
                    'Description' : 'Check that the tau lepton mass can be achieved with the right <θH>.'
                    },
            'sinThdiv2-4': {
                    'ParamList' : ['k', 'zL', 'c0', 'Mu1', 'Mu11', 'c1'],
                    'ToCheckExpr' : "-((- ( (1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * ( - BesselJ(0.5+c0, (4.18 / k)  * zL) * BesselY(0.5 + c0, 1 * (4.18 / k) ) + BesselJ(0.5 + c0, 1 * (4.18 / k) ) * BesselY(0.5 + c0, (4.18 / k)  * zL) )  ))*(((1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * (  - BesselJ(-0.5 + c0, (4.18 / k)  * zL) * BesselY(-0.5 + c0, 1 * (4.18 / k) ) + BesselJ(-0.5 + c0, 1 * (4.18 / k) ) * BesselY(-0.5 + c0, (4.18 / k)  * zL) )   ))+(Mu1**2) * (((1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * (  - BesselJ(-0.5 + c0, (4.18 / k)  * zL) * BesselY(-0.5 + c0, 1 * (4.18 / k) ) + BesselJ(-0.5 + c0, 1 * (4.18 / k) ) * BesselY(-0.5 + c0, (4.18 / k)  * zL) )   ))*(- ((1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * (- BesselJ(0.5+c0, (4.18 / k)*zL) * BesselY(-0.5 + c0, 1*(4.18 / k) ) + BesselJ(- 0.5 + c0, 1 * (4.18 / k) ) * BesselY(0.5 + c0, (4.18 / k)*zL) )  ))*(- ( (1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * ( - BesselJ(0.5+c1, (4.18 / k)  * zL) * BesselY(0.5 + c1, 1 * (4.18 / k) ) + BesselJ(0.5 + c1, 1 * (4.18 / k) ) * BesselY(0.5 + c1, (4.18 / k)  * zL) )  ))*(- ((1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * (- BesselJ(0.5+c1, (4.18 / k)*zL) * BesselY(-0.5 + c1, 1*(4.18 / k) ) + BesselJ(- 0.5 + c1, 1 * (4.18 / k) ) * BesselY(0.5 + c1, (4.18 / k)*zL) )  ))/ ((Mu11**2)*((- ((1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * (- BesselJ(0.5+c1, (4.18 / k)*zL) * BesselY(-0.5 + c1, 1*(4.18 / k) ) + BesselJ(- 0.5 + c1, 1 * (4.18 / k) ) * BesselY(0.5 + c1, (4.18 / k)*zL) )  ))**2)-((- ( (1/2) * np.pi * sqrt(1 * zL) * (4.18 / k)  * ( - BesselJ(0.5+c1, (4.18 / k)  * zL) * BesselY(0.5 + c1, 1 * (4.18 / k) ) + BesselJ(0.5 + c1, 1 * (4.18 / k) ) * BesselY(0.5 + c1, (4.18 / k)  * zL) )  ))**2)))",
                    'ToCheckMinBound' : (sin (betaH*0.1/2))**2 ,
                    'ToCheckMax' : (sin(alphaH*0.1/2))**2,
                    'Description' : 'Check that the Bottom mass can be achieved with the right <θH>.'
                    },

            'cosThdiv2': {
                    'ParamList' : ['k', 'zL', 'c0Prime'],
                    'ToCheckExpr' : "(- ( (1/2) * np.pi * sqrt(1 * zL) * (5300 / k) * ( - BesselJ(0.5+c0Prime, (5300 / k) * zL) * BesselY(0.5 + c0Prime, 1 * (5300 / k)) + BesselJ(0.5 + c0Prime, 1 * (5300 / k)) * BesselY(0.5 + c0Prime, (5300 / k) * zL) )  ))*((1/2) * np.pi * sqrt(1 * zL) * (5300 / k) * (  - BesselJ(-0.5 + c0Prime, (5300 / k) * zL) * BesselY(-0.5 + c0Prime, 1 * (5300 / k)) + BesselJ(-0.5 + c0Prime, 1 * (5300 / k)) * BesselY(-0.5 + c0Prime, (5300 / k) * zL) )   )",
                    'ToCheckMinBound' : -(cos( betaH*0.1/2) )**2 ,
                    'ToCheckMax' : -(cos( alphaH*0.1/2))**2,
                    'Description' : 'Check that the W boson mass can be achieved with the right <θH>.'
                    }


            # 'sinThdiv2-3': {
            #                     'ParamList' : ['k', 'zL', 'c0', 'c1', 'Mu1'],
            #                     'ParamCaseCheck' : {'ParamList' : ['c0'],
            #                                         'Cases' : {'c0 < 0.5': 'Case-1',
            #                                                    'c0 > 0.5' : 'Case-2'}
            #                                         },
            #                     'ToCheckExpr' : {"Case-1" : "4.18 / (k * (zL**(c0-c1-1))* ( (  (4.18/172.44) * Mu1 * (1/(zL**(c0 - c1)))    )  /Mu1) * sqrt( (1-2*c0)*(1+2*c1) )  )  ",
            #                                      "Case-2" : "4.18 / (k * (zL**(-c1-1/2))* (Mu11/Mu1) * sqrt( (2*c0-1)*(2*c1+1) )  )" },
            #                     'ToCheckMinBound' : sin (betaH*0.1/2) ,
            #                     'ToCheckMax' :      sin (alphaH*0.1/2),
            #                     'Description' : 'Check that the Top mass can be achieved with the right <θH>.'
            #                     },
            # 'sinThdiv2-4': {
            #                     'ParamList' : ['k', 'zL', 'c0', 'c2', 'Mu11Prime', 'Mu2Tilde'],
            #                     'ParamCaseCheck' : {'ParamList' : ['c2'],
            #                                         'Cases' : {'c2 < 0.5': 'Case-1',
            #                                                    'c2 > 0.5' : 'Case-2'}
            #                                         },
            #                     'ToCheckExpr' : {"Case-1" : "1.7776 / (k * (zL**(-1+c2-c0))* (Mu11Prime/Mu2Tilde) * sqrt( (2*c0+1)*(1-2*c2) )  )  ",
            #                                      "Case-2" : "1.7776 / (k * (zL**(-1/2-c0))* (Mu11Prime/Mu2Tilde) * sqrt( (2*c0+1)*(2*c2-1) )  )  " },
            #                     'ToCheckMinBound' : sin (betaH*0.1/2) ,
            #                     'ToCheckMax' :      sin(alphaH*0.1/2),
            #                     'Description' : 'Check that the Top mass can be achieved with the right <θH>.'
            #                         },
            # 'FinalCond-Mu11Prime': {
            #                     'ParamList' : ['Mu11Prime'],
            #
            #                     'ToCheckExpr' : "Mu11Prime" ,
            #                     'ToCheckMinBound' : 0.0,
            #                     'ToCheckMax' :      100.0,
            #                     'Description' : 'Check Mu11Prime has a reasonable value'
            #                     },
            # 'FinalCond-Mu11': {
            #                     'ParamList' : ['Mu11'],
            #
            #                     'ToCheckExpr' : "Mu11" ,
            #                     'ToCheckMinBound' : 0.0,
            #                     'ToCheckMax' :      100.0,
            #                     'Description' : 'Check Mu11 has a reasonable value'
            #                     },
}
