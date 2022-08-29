import pySALEPlot as psp
import numpy as np

model = psp.opendatfile('Sudbury/jdata.dat')  # Ensure path is correct
model.setScale('km')
for i in np.arange(0, model.nsteps+1, 20):
    step = model.readStep('Tmp', i)
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
        left_new[w] = step.ymark[min_x[w]]  # Array of left-most tracers
    crater_floor = np.amax(left_new)  # Highest of the left-most tracers
    depth = round((crater_tip - crater_floor), 2)  # Difference in height
    print('Crater Diameter is', crater_dia, 'km, Crater depth is', depth, 'km')

