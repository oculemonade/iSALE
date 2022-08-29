import numpy as np
import matplotlib.pyplot as plt
import pySALEPlot as psp

Mass_P = 5.97e24  # kg
Radius = 6378  # km
# ===========================================================
#                    asteroid.imp Parameters
# ===========================================================
print('Extracting asteroid.inp Parameters')
ast_input = open('../asteroid.inp', 'r')
keywords = ['GRIDSPC', 'OBJRESH', 'DTSAVE', 'TR_SPCH', 'TR_SPCV', 'LAYPOS']
materials = ['LAYMAT']
ast_dict = {}
mat = []
for line in ast_input:
    word = line[0:16].replace(' ', '')
    if word == 'S_TYPE':
        Type = line[54:-1].replace(' ', '')
    value = '['+(line[54:-1].replace(' ', ''
                                     ).replace(':', ',')).replace('D', 'e')+']'
    if word in keywords:
        ast_dict[word] = eval(value)

lay3 = ast_dict['LAYPOS'][0]
lay2 = ast_dict['LAYPOS'][1]
lay1 = ast_dict['LAYPOS'][2]
spacing = (ast_dict['GRIDSPC'][0]) * .001  # (km)
dx = (ast_dict['TR_SPCH'][0]) * -spacing  # tracer spacing horizontal
dy = (ast_dict['TR_SPCV'][0]) * -spacing  # tracer spacing vertical
imp_dia = (ast_dict['OBJRESH'][0]) * spacing * 2  # Impactor diameter
print('Imports done, time to start finding Melt')
model = psp.opendatfile('../Sudbury/jdata.dat')  # open the data file now
model.setScale('km')  # next we can set the distance units to be km
step = model.readStep('TrP', model.nsteps - 1)
step0 = model.readStep('TrP', 0)
# ============================================================
#                  Alright, Plotting Time
# ===========================================================
dirname = 'Meltsheet Plot'  # Make an output directory
psp.mkdir_p(dirname)


def get_distances(s, line):  # distances between tracers
    x = s.xmark[line]
    y = s.ymark[line]
    return np.sqrt((x[:-1]-x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2)


maxsep = 3.  # Define the maximum separation allowed when plotting lines
fig = plt.figure(figsize=(15, 9))  # Set up figure
ax = fig.add_subplot(111, aspect='equal')
for i in np.arange(00, model.nsteps + 1, 40):
    ax.set_xlabel('r [km]')  # Set the axis labels
    ax.set_ylabel('z [km]')
    ax.set_xlim([-220, 220])  # Set the axis limits
    ax.set_ylim([-125, 150])
    stepi = model.readStep("TrP", i)  # Read the time step i from the datafile
    p1 = ax.pcolormesh(model.x, model.y, stepi.mat, cmap='bone',
                       vmin=1, vmax=model.nmat + 1)
    p2 = ax.pcolormesh(-model.x, model.y, stepi.mat, cmap='bone',
                       vmin=1, vmax=model.nmat + 1)
    [ax.contour(model.xc, model.yc, stepi.cmc[mat], 1, colors='k',
                linewidths=0.5) for mat in [0, 1, 2]]  # Material boundaries
    [ax.contour(-model.xc, model.yc, stepi.cmc[mat], 1, colors='k',
                linewidths=0.5) for mat in [0, 1, 2]]

for u in range(1, model.tracer_numu):  # Tracer lines
    tru = model.tru[u]
    for u in range(model.tracer_numu):
        tstart = model.tru[u].start
        tend = model.tru[u].end
        # ------------All Melt------------------------
        indices = np.where(step.TrP > 6e10)
        melt_index = indices[0][:]
        melt_x = np.zeros(len(melt_index))
        melt_y = np.zeros(len(melt_index))
        melt_xi = np.zeros(len(melt_index))
        melt_yi = np.zeros(len(melt_index))
        total_melt = 0
        for h in range(len(melt_index)):
            melt_x[h] = step0.xmark[melt_index[h]]
            melt_y[h] = step0.ymark[melt_index[h]]
            melt_xi[h] = stepi.xmark[melt_index[h]]
            melt_yi[h] = stepi.ymark[melt_index[h]]
        for j in range(len(melt_x)):
            volume = (2 * np.pi * dx * dy * melt_x[j]
                      * ((Radius + melt_y[j]) / Radius))
            total_melt += (volume)
        total_melt = round(total_melt, 3)
        # -----------All Melt------------------------
        # ---------Impactor Melt---------------------
        impactor = np.where(melt_y >= 0)
        impactor_index = impactor[0][:]
        impact_x = np.zeros(len(impactor_index))
        impact_y = np.zeros(len(impactor_index))
        impact_xi = np.zeros(len(impactor_index))
        impact_yi = np.zeros(len(impactor_index))
        for k in range(len(impactor_index)):  # Impactor contribution
            impact_x[k] = melt_x[impactor_index[k]]
            impact_y[k] = melt_y[impactor_index[k]]
            impact_xi[k] = melt_xi[impactor_index[k]]
            impact_yi[k] = melt_yi[impactor_index[k]]
        # ---------Impactor Melt---------------------
        # --------Upper Crust Melt-------------------
        layer1 = np.where((melt_y <= 0) & (melt_y >= -(lay1 - lay2) * spacing))
        uppercrust_index = layer1[0][:]
        upper_x = np.zeros(len(uppercrust_index))
        upper_y = np.zeros(len(uppercrust_index))
        upper_xi = np.zeros(len(uppercrust_index))
        upper_yi = np.zeros(len(uppercrust_index))
        for k in range(len(uppercrust_index)):  # Upper Crust contribution
            upper_x[k] = melt_x[uppercrust_index[k]]
            upper_y[k] = melt_y[uppercrust_index[k]]
            upper_xi[k] = melt_xi[uppercrust_index[k]]
            upper_yi[k] = melt_yi[uppercrust_index[k]]
        # --------Upper Crust Melt-------------------
        # --------Lower Crust Melt-------------------
        layer2 = np.where((melt_y <= -(lay1 - lay2) * spacing) &
                          (melt_y > -(lay1 - lay3) * spacing))
        lowercrust_index = layer2[0][:]
        lower_x = np.zeros(len(lowercrust_index))
        lower_y = np.zeros(len(lowercrust_index))
        lower_xi = np.zeros(len(lowercrust_index))
        lower_yi = np.zeros(len(lowercrust_index))
        for k in range(len(lowercrust_index)):  # Lower Crust contribution
            lower_x[k] = melt_x[lowercrust_index[k]]
            lower_y[k] = melt_y[lowercrust_index[k]]
            lower_xi[k] = melt_xi[lowercrust_index[k]]
            lower_yi[k] = melt_yi[lowercrust_index[k]]
        # --------Lower Crust Melt-------------------
        # -----------Mantle Melt--------------------
        layer3 = np.where(melt_y <= -(lay1 - lay3) * spacing)
        mantle_index = layer3[0][:]
        mantle_x = np.zeros(len(mantle_index))
        mantle_y = np.zeros(len(mantle_index))
        mantle_xi = np.zeros(len(mantle_index))
        mantle_yi = np.zeros(len(mantle_index))
        for k in range(len(mantle_index)):  # Mantle contribution
            mantle_x[k] = melt_x[mantle_index[k]]
            mantle_y[k] = melt_y[mantle_index[k]]
            mantle_xi[k] = melt_xi[mantle_index[k]]
            mantle_yi[k] = melt_yi[mantle_index[k]]
        # ------------Mantle Melt--------------------
        # --------------------------------------
        scat = ax.scatter(melt_xi, melt_yi, s=0.3, c="red",
                          linewidths=0.0)  # locations of the marked tracers
        scat2 = ax.scatter(-mantle_xi, mantle_yi, s=0.3, c="white",
                           linewidths=0)  # Pieces of the Mantle
        scat3 = ax.scatter(-lower_xi, lower_yi, s=0.3, c="green",
                           linewidths=0)  # Pieces of the Lower Crust
        scat4 = ax.scatter(-upper_xi, upper_yi, s=0.3, c="blue",
                           linewidths=0)  # Pieces of the Upper Crust
        scat5 = ax.scatter(-impact_xi, impact_yi, s=0.3, c="yellow",
                           linewidths=0)  # Pieces of the Impactor
        # -------------------------------------
    ax.set_title('t = {: 5.2f} s, total Melt = {} km^3'
                 .format(step.time, total_melt))
    fig.savefig('{}/Melt-{:05d}.png'.format(dirname, i), format='png', dpi=400)
    ax.cla()

