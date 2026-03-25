import pySALEPlot as psp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

### The point of this code is to find the center of mass of a simulation in the
### PLANET mode. This assumes that "Den" has been included in VARLIST (see your
### .inp file). Rather than following specific tracers, this calulates the mass
### from the density field of the simulation. This may produce values different
### should this be calculated from "Trd". 

### This is for 2D simulations with iSALE, which means that the COM will lie on
### x = 0. This code calculates the volume of disks of the planet environment 
### to find the y-component of the COM. Images are made for further clarity. 

ast_input = open('../asteroid.inp', 'r')
keywords = ['GRIDSPC', 'OBJRESH', 'R_PLANET']
ast_dict = {}

for line  in ast_input:
    word = line[0:16].replace(' ', '')
    if word == 'S_TYPE':
        Type = line[54:-1].replace(' ', '')
    value = '['+(line[54:-1].replace(' ', '').replace(
                 ':', ',')).replace('D', 'e')+']'
    if word in keywords:
        ast_dict[word] = eval(value)

for i in range(len(ast_dict['OBJRESH'])):
    globals()["lay_{}".format(len(ast_dict['OBJRESH'])
                              - i)] = ast_dict['OBJRESH'][i]

spacing = (ast_dict['GRIDSPC'][0]) * .001
imp_rad = (ast_dict['OBJRESH'][0]) * spacing
R       = (ast_dict['R_PLANET'][0])/1000 # radius in km

### Ensure that the path for the jdata.dat file is in the right path!
model = psp.opendatfile('../Planet2D/jdata.dat')
model.setScale('km')
dirname = 'COM'
psp.mkdir_p(dirname)

### dx and dy is usually established in "TR_SPCH" and "TR_SPCV". However,
### material may move into the Low Resolution Zone, in which case these values 
### will change. dx_cell and dy_cell account for this
dx = np.diff(model.x[:, 0])
dy = np.diff(model.y[0, :]) 

fig = plt.figure(figsize=(9,10))
ax = fig.add_subplot(111, aspect = 'equal')
for i in np.arange(0, model.nsteps + 1, 1):
    ax.set_xlabel('Radial Distance [km]')
    ax.set_ylabel('Radial Distance [km]')
    ax.set_xlim(-(0.1 * R), (1.1 * R))
    ax.set_ylim(-(2.1 * R), (10 * imp_rad))
    step_iM  = model.readStep("TrM", i) # nth step of the sim for material
    center = np.round(np.min(step_iM.ymark)/2,2)
    ### Where is the center of the simulation? Occasionally the planet/simulated
    ### body will move after impact, but it should relax to the point where it 
    ### began. We can't consider the "top" of the planet to be the floor of the
    ### crater since the top will be sheared off from the impact.  
    step = model.readStep('Den', i)

    ### VARLIST positions aren't node centered so that is achieved here
    density = step.data[0]
    density = np.ma.filled(density.astype(float), fill_value = 0) # in kg/m^3
    x_centers = 0.5 * (model.x[:, :-1] + model.x[:, 1:])
    y_centers = 0.5 * (model.y[:-1, :] + model.y[1:, :])
    X = 0.5 * (x_centers[:-1, :] + x_centers[1:, :])
    Y = 0.5 * (y_centers[:, :-1] + y_centers[:, 1:])

    dV = 2 * np.pi * X * dx[:, None] * dy[None, :] * (1000**3) # cubic meters
    ### Since these simulations assume symmetry about the y-axis, we only care
    ### about the y-value of the center of mass. dV represents the volume of 
    ### disk sections of the sphere
    dm = density * dV
    total_mass = np.round(np.sum(dm), 3) 
    y_com = np.round((np.sum(Y * dm) / total_mass), 2)
    com = np.round((center - y_com), 2)
    print("Y Center of Mass distance from center (km):", com)
    for u in range(model.tracer_numu):
        tstart = model.tru[u].start
        tend = model.tru[u].end
        scat = ax.scatter(step_iM.xmark[tstart:tend], 
               step_iM.ymark[tstart:tend], c = step_iM.TrM[tstart:tend], s = 1, 
               vmin = 0, vmax = 5, cmap = 'spring', edgecolors = 'none')
        scat_cen = ax.scatter(0, center, s = 50, c = "black" ,  linewidth = 1)
        scat_com = ax.scatter(0, y_com,  s = 50, c = "fuchsia", linewidth = 1) 
        ax.set_aspect('equal', adjustable = 'box')
    minute = step_iM.time/60
    fig.suptitle('Time = {: 5.2f} min,\n'
                 'COM is below Moon center by {: 5.2f}km'.format(minute, com))
    fig.savefig('{}/diameter-{:05d}.png'.format(dirname, i), format = 'png',
                dpi =300)
    ax.cla()

