import matplotlib as mpl
import pySALEPlot as psp
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

# This code plots the right side of a simulation environment, showing damage 
# (from 0, no damage, to 1 complete damage) as a color mesh and Peak Pressure tracers
# based on their melt fraction. 0% melted is for tracers experiencing less than 
# 46 GPa, and 100% melted is >=60 GPa.
# Code written 08/10/2024

try:
    plt.set_cmap('viridis')
except Exception:
    plt.set_cmap('YlGnBu_r')

dirname = "MeltFraction"
psp.mkdir_p(dirname)
model = psp.opendatfile('../Sudbury/jdata.dat')  # Own path here
model.setScale('km')
fig = plt.figure(figsize=(7, 5))
ax = fig.add_subplot(111)

def make_colorbar(ax, p, f):
    """Create a colorbar on the left side of the plot."""
    divider = make_axes_locatable(ax)
    cx = divider.append_axes("left", size="5%", pad=0.8)
    cb = fig.colorbar(p, cax=cx)
    cb.set_label(psp.longFieldName(f))
    # Set the labels on the left for this colorbar
    cx.yaxis.tick_left()
    cx.yaxis.set_label_position('left')

ax.set_xlabel('r [km]')
ax.set_ylabel('z [km]')
ax.set_aspect('equal')

for i in np.arange(0, model.nsteps + 1, 40):
    ax.clear()
    ax.set_xlabel('Radius [km]')
    ax.set_ylabel('Z [km]')
    ax.set_xlim([0, 220])
    ax.set_ylim([-125, 150])
    step_TrP = model.readStep('TrP', i)
    step_Dam = model.readStep('Dam', i)

    # Damage colormesh
    p1 = ax.pcolormesh(model.x, model.y, step_Dam.data[0], vmin=0, vmax=1)

    # Material boundaries
    [ax.contour(model.xc, model.yc, step_Dam.cmc[mat], 1, colors='k',
                linewidths=0.5) for mat in [0, 1, 2]]

    for u in range(model.tracer_numu):
        tstart = model.tru[u].start
        tend = model.tru[u].end
        indices = np.where(step_TrP.TrP >= 4.6e10)  # 46 GPa as start of melt
        melt_index = indices[0][:]
        melt_x = np.zeros(len(melt_index))
        melt_y = np.zeros(len(melt_index))
        TrP = np.zeros(len(melt_index))

        for h in range(len(melt_index)):
            melt_x[h] = step_TrP.xmark[melt_index[h]]
            melt_y[h] = step_TrP.ymark[melt_index[h]]
            TrP[h] = ((step_TrP.TrP[melt_index[h]] * 1e-9) - 46) / 0.14  # 60 GPa as 100% melted

        scat_right = ax.scatter(
            melt_x[tstart:tend], melt_y[tstart:tend],
            c=TrP[tstart:tend], vmin=0, vmax=100,
            cmap='Oranges', s=0.5, linewidths=0
        )

    if i == 0:
        cb = fig.colorbar(scat_right)
        make_colorbar(ax, p1, step_Dam.plottype[0])

    cb.set_label('Melt Fraction %')
    ax.set_title('t = {:5.2f} s'.format(step_Dam.time))
    fig.savefig('{}/Melt-{:05d}.png'.format(dirname, i), format='png', dpi=400)

