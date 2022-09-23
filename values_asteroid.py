import numpy as np

#  The Purpose of this code is to go into the numerous simulations you have
#  and provide information from the asteroid.inp that are in the form of
#  numbers, such as OBJVEL and LAYPOS. Upon finishing, it will print the values
#  in order of simulation/folder naming scheme, separated by asteroid.inp type.
#  !!! Before starting, ensure that you have an empty .dat file in the !!!
#  !!!        correct path before beginning running the scripts        !!!

size = 139  # This value will depend on how many simulations you have
start = 0

velocity_ = np.zeros((size, 1))
impactor_ = np.zeros((size, 1))
gridspace = np.zeros((size, 1))
CPPR_____ = np.zeros((size, 1))
laypos1__ = np.zeros((size, 1))
laypos2__ = np.zeros((size, 1))
laypos3__ = np.zeros((size, 1))

for i in np.arange(start, size, 1):
    ast_input = open('../Sudbury_run' + str(i+1) + '/asteroid.inp', 'r')
    keywords = ['GRIDSPC', 'OBJRESH', 'LAYPOS', 'OBJVEL']
    ast_dict = {}
    for line in ast_input:
        word = line[0:16].replace(' ', '')
        value = '['+(line[54:-1].replace(' ', '')
                     .replace(':', ',')).replace('D', 'e')+']'
        if word in keywords:
            ast_dict[word] = eval(value)

    velocity_[i][0] = ast_dict['OBJVEL'][0] * -.001
    gridspace[i][0] = ast_dict['GRIDSPC'][0] * .001
    CPPR_____[i][0] = ast_dict['OBJRESH'][0]
    laypos1__[i][0] = ast_dict['LAYPOS'][0]
    laypos2__[i][0] = ast_dict['LAYPOS'][1]
    laypos3__[i][0] = ast_dict['LAYPOS'][2]

file0 = open('list_asteroid_values.dat', 'r+')
file0.write('Velocity values\n')
file0.write('{}\n\n'.format(velocity_).replace(']', '').replace('[', '')
            .replace(' ', ''))
file0.write('Gridspace values\n')
file0.write('{}\n\n'.format(gridspace).replace(']', '').replace('[', '')
            .replace(' ', ''))
file0.write('CPPR values\n')
file0.write('{}\n\n'.format(CPPR_____).replace(']', '').replace('[', '')
            .replace(' ', ''))
file0.write('laypos1 values\n')
file0.write('{}\n\n'.format(laypos1__).replace(']', '').replace('[', '')
            .replace(' ', ''))
file0.write('laypos2 values\n')
file0.write('{}\n\n'.format(laypos2__).replace(']', '').replace('[', '')
            .replace(' ', ''))
file0.write('laypos3 values\n')
file0.write('{}\n\n'.format(laypos3__).replace(']', '').replace('[', '')
            .replace(' ', ''))

