import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os

from remove_unwanted import sorting


def changing_values(root):
    '''This function finds the arrays that change over time, even if it is
    a small amount'''
    
    changing_dict = {}
    
    for i in root.variables:
    
        if len(root[i][:])<2:
            continue
        elif not np.all(root[i][:]==root[i][0]):
            print('{} is at thing'.format(i))
            changing_dict[i]=root[i][:]
            
    return changing_dict


def main():
    
    directory = '../327Data_Oct_2018/'
    
    if not os.path.exists('{}extras/'.format(directory)):
        sorting(directory)
    
    root = Dataset('{}2018_12_07_01_327_004.nc'.format(directory),'r')
    changing_values(root)
    
    x_label = 'CurrentH'
    y_label = 'HVoltage'
    
    fig = plt.figure(figsize=[10,7])
    plt.plot(root[x_label][:],root[y_label][:])
        
    plt.title('{} vs {}'.format(x_label,y_label))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.show()
    
    root.close()
    
main()