import numpy as np

#  The Purpose of this code is to go into the numerous simulations you have
#  and provide information from the asteroid.inp that are in the form of words,
#  such as OBJMAT and LAYMAT. Upon finishing, it will print the values in order
#  of the simulation/folder naming scheme, separated by asteroid.inp type.
#  !!! Before starting, ensure that you have an empty .dat file in the !!!
#  !!!        correct path before beginning running the scripts        !!!

start = 0
size = 139  # This value will depend on how many simulations you have
impactor = ['Sudbury'] * (size)
uppercrt = ['Sudbury'] * (size)
lowercrt = ['Sudbury'] * (size)
mantle__ = ['Sudbury'] * (size)

for i in np.arange(start, size, 1):
    ast_input = open('../Sudbury_run' + str(i+1) + '/asteroid.inp', 'r')
    # !!! Ensure path is correct !!!
    keywords = ['OBJMAT', 'LAYMAT']
    ast_dict = {}
    for line in ast_input:
        word = line[0:16].replace(' ', '')
        if word == 'S_TYPE':
            Type = line[54:-1].replace(' ', '')
        value = (line[54:-1].replace(' ', '').replace(':', ','))
        if word in keywords:
            ast_dict[word] = (value)

    materials__ = ast_dict['LAYMAT'].split(',')  # list of all layer materials
    impactor[i] = ast_dict['OBJMAT']  # list of all impactor types
    uppercrt[i] = materials__[2]
    lowercrt[i] = materials__[1]
    mantle__[i] = materials__[0]
    ast_input.close()

file0 = open('list_asteroid_words.dat', 'r+')  # !!! Ensure path is correct !!!
file0.write('Impactor Material\n')
for j in np.arange(start, size, 1):
    file0.write('{}\n'.format(impactor[j]))
file0.write('Upper Crust Material\n')
for k in np.arange(start, size, 1):
    file0.write('{}\n'.format(uppercrt[k]))
file0.write('Lower Crust Material\n')
for m in np.arange(start, size, 1):
    file0.write('{}\n'.format(lowercrt[m]))
file0.write('Mantle Material\n')
for n in np.arange(start, size, 1):
    file0.write('{}\n'.format(mantle__[n]))

