import pySALEPlot as psp
import matplotlib.pyplot as plt
from numpy import ma
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

# This example plotting script designed to ensure that the
# tracers for finding depth and diameter are in the right spot


def get_distances(s, line):  # distances between tracers
    x = s.xmark[line]
    y = s.ymark[line]
    return np.sqrt((x[:-1] - x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2)

maxsep = 3.  # Define the maximum separation allowed when plotting lines


def make_colorbar(ax, p, f):
    # Create axes either side of the plot to place the colorbars
    divider = make_axes_locatable(ax)
    cx = divider.append_axes("left", size="5%", pad=1.0)
    cb = fig.colorbar(p, cax=cx)
    cb.set_label(psp.longFieldName(f))
    cx.yaxis.tick_left()  # Need to set labels on the left for this colorbar
    cx.yaxis.set_label_position('left')

dirname = 'Diameter_Check'  # Make an output directory
psp.mkdir_p(dirname)
model = psp.opendatfile('../Sudbury/jdata.dat')  # Open the datafile
model.setScale('km')  # Set the distance units to km
fig = plt.figure(figsize=(17, 10))  # Set up a pylab figure
ax = fig.add_subplot(111, aspect='equal')

for i in np.arange(0, model.nsteps + 1, 40):  # Loop over timesteps
    ax.set_xlabel('r [km]')  # Set the axis labels
    ax.set_ylabel('z [km]')
    ax.set_xlim([-215, 215])  # Set the axis limits
    ax.set_ylim([-125, 130])
    step = model.readStep('Tmp', i)  # Read the time step 'i' from the datafile
    y_i = ((step.ymark))

    for u in range(len(y_i)):
        if y_i[u] > 100:
            y_i[u] = 0  # This gets rid of any pieces that is too high
    index_of_max_y = np.where(y_i == max(y_i))  # Index where y is maxed
    max_height = np.amin(index_of_max_y)  # This value also an index
    crater_rim = step.xmark[max_height]  # Horizon point where the max occurs
    crater_tip = step.ymark[max_height]  # Vertical point where the max occurs
    crater_dia = round((2 * crater_rim), 2)  # Diameter of crater
    left_array = (np.where(step.xmark < 2.5))  # Array of the indices
    min_x = left_array[0][:]  # Array of the minimum x-values
    left_new = np.zeros(len(min_x))

    for w in range(len(min_x)):
        left_new[w] = step.ymark[min_x[w]]
    crater_floor = np.amax(left_new)
    crater_floor_x = np.where(step.ymark == crater_floor)
    crater_floor_xx = np.amin(step.xmark[crater_floor_x])
    depth = round((crater_tip - crater_floor), 2)
    # The classic iSALEPlot mirrored setup, mirrored with negative x-values
    p1 = ax.pcolormesh(model.x, model.y, step.mat, cmap='Oranges',
                       vmin=1, vmax=model.nmat+1)
    p2 = ax.pcolormesh(-model.x, model.y, step.data[0], vmin=0, vmax=1500)
    # Material boundaries
    [ax.contour(model.xc, model.yc, step.cmc[mat], 1, colors='k',
                linewidths=0.5) for mat in [0, 1, 2]]
    [ax.contour(-model.xc, model.yc, step.cmc[mat], 1, colors='k',
                linewidths=0.5) for mat in [0, 1, 2]]

    for u in range(1, model.tracer_numu):  # Tracer lines
        tru = model.tru[u]
        # Plot the tracers in horizontal lines, every 5 lines
        for l in np.arange(0, len(tru.xlines), 5):
            # Get the distances between pairs of tracers in xlines
            dist = get_distances(step, tru.xlines[l])
            # Mask the xmark values if separation too big...
            # means the line won't be connected here
            ax.plot(ma.masked_array(step.xmark[tru.xlines[l]][:-1],
                    mask=dist > maxsep*tru.d[0]),
                    step.ymark[tru.xlines[l]][:-1], c='#808080', marker='None',
                    linestyle='-', linewidth=0.5)
    # These are the locations of the highed tracers
    scat1 = ax.scatter(crater_rim, crater_tip, s=15,
                       c="chartreuse", linewidths=0.5)
    scat2 = ax.scatter(crater_floor_xx, crater_floor, s=15,
                       c="cyan", linewidths=0.5)
    scat3 = ax.scatter(step.xmark, step.ymark, s=0.05,
                       c="red", linewidths=0)

    if i == 0:
        make_colorbar(ax, p2, step.plottype[0])  # Add colorbars

    ax.set_title('{: 5.2f} s'.format(step.time))
    fig.savefig('{}/Diameter_Check-{}.png'.format(dirname, i), dpi=300)
    ax.cla()  # Remove the field, ready for the next timestep to be plotted

