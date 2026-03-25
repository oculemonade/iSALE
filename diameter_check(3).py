import pySALEPlot as psp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

### This code calculates the crater diameter using (1) the crater rim, defined
### as the tracer that is highest above the surface and (2) the excavation
### boundary of the crust. It should be noted that (a) the crater rim has a
### tendency to move as the simulation relaxes as does the (b) excavation
### boundary. Results should be visually checked, averaged and considered as
### an approximations. Results should not be considered until after the
### simulation has relaxed.
### This code also creates a folder where plots of the impact are made, in these
### plots show where the crater rim and excavation boundary is.

### !!! Ensure that the path for the asteroid.inp file is correct!
ast_input = open('../asteroid.inp', 'r')
keywords = ['GRIDSPC', 'OBJRESH', 'R_PLANET']
ast_dict = {}
mat = []

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
crust   = ((ast_dict['OBJRESH'][1])-(ast_dict['OBJRESH'][2]))*spacing

### Ensure that the path for the jdata.dat file is in the right path!
model = psp.opendatfile('../Planet2D/jdata.dat')
model.setScale('km')
step  = model.readStep('TrP', model.nsteps - 1) # nth step of the simulation
step0 = model.readStep('TrP', 0) # first step of the simulation
dirname = 'Diameter_Check'
psp.mkdir_p(dirname)

fig = plt.figure(figsize=(9,10))
ax = fig.add_subplot(111, aspect = 'equal')
for i in np.arange(0, model.nsteps + 1, 1):
    ax.set_xlabel('Radial Distance [km]')
    ax.set_ylabel('Radial Distance [km]')
    ax.set_xlim(-(0.1 * R), (1.1 * R))
    ax.set_ylim(-(2.1 * R), (10 * imp_rad))
    step_i   = model.readStep("TrP", i) # nth step of the sim for pressure
    step_iM  = model.readStep("TrM", i) # nth step of the sim for material
    distance = np.zeros(len(step_i.xmark))
### Occasionally the planet will shift through the mesh. "center" will find
### the center of the planet despite the shift
    ymin = np.min(step_iM.ymark)
    bottom = np.min(step_iM.ymark[step_iM.ymark > ymin])
    center = np.round(bottom/2,2)

### Here we are "looking" for the crater rim. This will be defined as the tracer
### that is furthest away from the planet's center. Of course, this means that
### it can read airborne tracers as the crater rim. The solution for this is (1)
### apply a height filter and (2) visual check. Also, sometimes tracers get 
### stuck on the Low Resolution Zone bottom if the planet gets pushed 
### significantly by the impactor. That is the purpose of "bottom"

    dx = step_iM.xmark
    dy = step_iM.ymark - center
    r = np.sqrt(dx**2 + dy**2)
    mat = step_iM.TrM
    rim_mask = ((r < 1.01*R) & (r > R))
### Positional true or false in the array for whether or not a tracer is above
### the surface, but so far where the tracer is ejecta
    rim_indices = np.where(rim_mask)[0]
### This loop locates the highest tracer, which represents the crater rim
    if len(rim_indices) > 0:
        rim_r = r[rim_mask]
        imax = np.argmax(rim_r)
        rim_loc = rim_indices[imax]
    x_rim = dx[rim_loc]
    y_rim = dy[rim_loc]
    theta = np.arctan2(x_rim, y_rim) # angle (in radians) of the crater rim
    crater_dia = 2 * R * theta # theta is just center to right rim, so * 2
    crust_mask = ((r > (R-crust)) & (r < (1.01 * R)))
    theta2 = np.arctan2(dx, dy)
    nbins = 91
    theta_bins = np.linspace(0, np.pi, nbins)
### theta_bins is an array which subtends an angle from 0 to pi radians. We are
### looking at wedges of the crust, so nbins basically says how many slices
### there will be. The first slice is at theta = 0 and finishes at theta = pi.
### Be careful with the value of nbins. If there are too few, then the range a 
### bin spans is large and is not representative of the excavation rim, if its 
### too small, then it might pick up a region that happens to have a lot of 
### crust tracers.
    crust_frac = np.full(nbins - 1, np.nan)  # array of nan
    mean_y = np.full(nbins - 1, np.nan)      # array of nan
    for j in range(nbins - 1):
        in_bin = (crust_mask & (theta2 >= theta_bins[j]) &
                              (theta2 < theta_bins[j+1]))
### in_bin is an array of true and false statements, where its looking for the
### above statement to be true. Is the position of the tracer within the space
### defined by "crust_mask", is it within the angle's defined by the jth bin?
        if np.sum(in_bin) > 0:
            crust_frac[j] = np.mean(mat[in_bin] == 2)
            mean_y[j]= np.mean(dy[in_bin])

    boundary = crust_frac > 0.75
### This is the fraction of tracers that must be achieved in a bin for it to be
### considered for the excavation rim. This value is probably arbitrary but
### should be greater than .5 and less than 1. Just be consistent
    good_pairs = boundary[:-1] & boundary[1:]
### This is one last stipulation that basically requires 2 consecutive bins must
### achieve boundary in order for it to be considered
    if not np.any(good_pairs):
       continue

### Next we need to find the highest bin where the boundary condition is
### satisfied. The idea here is that the excavation rim is defined as such. 
    valid_bins = np.where(good_pairs)[0]
    j_highest = valid_bins[np.argmax(mean_y[valid_bins])]
    in_highest_bin = (crust_mask & (theta2 >= theta_bins[j_highest]) & 
                     (theta2 < theta_bins[j_highest + 1]))
    x_bin = dx[in_highest_bin]
    y_bin = dy[in_highest_bin]
    imax = np.argmax(y_bin)
    x_excav = x_bin[imax]
    y_excav = y_bin[imax] + center
    theta_excav_dia = np.arctan2(x_excav, (y_excav-center))
    excav_dia = np.round(2 * theta_excav_dia * R, 2)
    area = np.round(2 * np.pi * R * np.abs(y_excav),2)
### Theoretically, the surface area "above" this rim is all excavated material, 
### whether or not it is melted material. Thus, this region should not have much
### crustal material at all. 
    for u in range(model.tracer_numu):
        tstart = model.tru[u].start
        tend = model.tru[u].end
        scat = ax.scatter(step_iM.xmark[tstart:tend], 
               step_iM.ymark[tstart:tend], c = step_iM.TrM[tstart:tend], s = 1, 
               vmin = 0, vmax = 5, cmap = 'spring', edgecolors = 'none')
        scat_rim = ax.scatter(step_iM.xmark[rim_loc], step_iM.ymark[rim_loc],
                              s = 50, c = "purple", linewidth = 1)
        circle1 = Circle((0, center), (R - crust), fill = False, 
                         color = 'green', linewidth = .5)
        circle2 = Circle((0, center), (R), fill = False, color = 'green',
                         linewidth = .5)
        scatbottom = ax.scatter(0, bottom, s = 5, c = "blue")
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        ax.set_aspect('equal', adjustable = 'box')       
        excav_rim= ax.scatter(x_excav, y_excav, s = 50, c = "red",linewidth = 1)   
    minute = step_iM.time/60
    fig.suptitle('Time = {: 5.2f} min and Crater Diameter = {: 5.2f} km \n' 
                'Excavtion Diameter is = {: 5.2f} km \n' 
                'Exposed surface area is = {:5.2e} km^2'.format(minute,
                 crater_dia, excav_dia, area))
    fig.savefig('{}/diameter-{:05d}.png'.format(dirname, i), format = 'png',
                dpi =300)
    ax.cla()

