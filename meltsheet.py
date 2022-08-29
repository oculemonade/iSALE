import numpy as np
import matplotlib.pyplot as plt
import pySALEPlot as psp
#============================================================
#                      Input Parameters 
#============================================================
print('Extracting Input Parameters') 
rho_imp = 2940; rho_top = 2600; rho_mid = 2940; rho_bot = 3320 #kg/m^3
Mass_P  = 5.97e24; Radius  = 6378 #kg; km
#============================================================
#                    asteroid.imp Parameters 
#============================================================
print('Extracting asteroid.inp Parameters') 
ast_input = open('asteroid.inp', 'r') 
keywords = ['GRIDSPC', 'OBJRESH', 'OBJVEL', 'DTSAVE', 'TR_SPCH', 'TR_SPCV','LAYPOS']
ast_dict = {}
mat = []
for line in ast_input:
    word  = line[0:16].replace(' ','')
    if word == 'S_TYPE':
        Type = line[54:-1].replace(' ','')
    value = '['+(line[54:-1].replace(' ','').replace(':',',')).replace('D','e')+']'    
    if word in keywords:
        ast_dict[word] = eval(value)

lay3 = ast_dict['LAYPOS'][0]; lay2 = ast_dict['LAYPOS'][1]; lay1 = ast_dict['LAYPOS'][2]
spacing    = (ast_dict['GRIDSPC'][0])* .001         # (km)
dx         = (ast_dict['TR_SPCH'][0])* -spacing     # tracer spacing horizontal
dy         = (ast_dict['TR_SPCV'][0])* -spacing     # tracer spacing vertical
imp_dia    = (ast_dict['OBJRESH'][0])* spacing * 2  # Impactor diameter

print('Imports done, time to start finding Melt') 
#============================================================
#                  Alright, Melt Finding Time
#============================================================
model = psp.opendatfile('Sudbury/jdata.dat') #open the data file now
model.setScale('km') #next we can set the distance units to be km
step     = model.readStep('TrP', model.nsteps - 1)
step0    = model.readStep('TrP', 0)

#------------All Melt------------------------
indices  = np.where(step.TrP > 6e10)
melt_index = indices[0][:]
melt_x = np.zeros(len(melt_index)); melt_y = np.zeros(len(melt_index)); melt_P = np.zeros(len(melt_index))
total_melt = 0
for i in range(len(melt_index)): 
    melt_x[i] = step0.xmark[melt_index[i]]    
    melt_y[i] = step0.ymark[melt_index[i]]  
    melt_P[i] = step0.TrP[melt_index[i]]
for j in range(len(melt_x)):
    volume = 2 * np.pi * dx * dy * melt_x[j] *((Radius + melt_y[j]) / Radius) 
    total_melt += (volume)
total_melt = round(total_melt, 3)
#------------All Melt------------------------
#----------Impactor Melt---------------------
impactor = np.where(melt_y >= 0)
impactor_index   = impactor[0][:]
impact_x = np.zeros(len(impactor_index)); impact_y = np.zeros(len(impactor_index))
impactor_melt = 0
for k in range(len(impactor_index)): #impactor contribution
    impact_x[k] = melt_x[impactor_index[k]]
    impact_y[k] = melt_y[impactor_index[k]]
for l in range(len(impact_x)):
    volume = 2 * np.pi * dx * dy * impact_x[l] *((Radius + impact_y[l]) / Radius)
    impactor_melt += volume
impactor_melt = round(impactor_melt, 3)
#----------Impactor Melt---------------------
#---------Upper Crust Melt-------------------
layer1   = np.where((melt_y <= 0) & (melt_y >= -(lay1-lay2)*spacing))
uppercrust_index = layer1[0][:]
upper_x = np.zeros(len(uppercrust_index)); upper_y = np.zeros(len(uppercrust_index))
uppercrust_melt = 0 
for k in range(len(uppercrust_index)): #top layer contribution
    upper_x[k] = melt_x[uppercrust_index[k]]
    upper_y[k] = melt_y[uppercrust_index[k]]
for l in range(len(upper_x)):
    volume = 2 * np.pi * dx * dy * upper_x[l] *((Radius + upper_y[l]) / Radius)
    uppercrust_melt += volume
uppercrust_melt = round(uppercrust_melt,3)
#---------Upper Crust Melt-------------------
#---------Lower Crust Melt-------------------
layer2   = np.where((melt_y <= -(lay1-lay2)*spacing) & (melt_y > -(lay1-lay3)*spacing))
lowercrust_index = layer2[0][:]
lower_x = np.zeros(len(lowercrust_index)); lower_y = np.zeros(len(lowercrust_index))
lowercrust_melt = 0 
for k in range(len(lowercrust_index)): #layer 2 contribution
    lower_x[k] = melt_x[lowercrust_index[k]]
    lower_y[k] = melt_y[lowercrust_index[k]]
for l in range(len(lower_x)):
    volume = 2 * np.pi * dx * dy * lower_x[l] *((Radius + lower_y[l]) / Radius)
    lowercrust_melt += volume
lowercrust_melt = round(lowercrust_melt,3)
#---------Lower Crust Melt-------------------
#------------Mantle Melt--------------------
layer3 = np.where(melt_y <= -(lay1-lay3)*spacing)
mantle_index = layer3[0][:]
mantle_x = np.zeros(len(mantle_index)); mantle_y = np.zeros(len(mantle_index))
mantle_melt = 0
for k in range(len(mantle_index)): #mantle contribution
    mantle_x[k] = melt_x[mantle_index[k]]
    mantle_y[k] = melt_y[mantle_index[k]]
for l in range(len(mantle_x)):
    volume = 2 * np.pi * dx * dy * mantle_x[l] *((Radius + mantle_y[l]) / Radius)
    mantle_melt += volume
mantle_melt = round(mantle_melt,3)
#------------Mantle Melt--------------------
print("Total melt       =", total_melt,     "km^3")
print('Impactor melt    =', impactor_melt,  'km^3')
print('Uppercrust melt  =', uppercrust_melt,'km^3')
print('Lowercrust melt  =', lowercrust_melt,'km^3')
print('Mantle melt      =', mantle_melt,    'km^3')

