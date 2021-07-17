import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os
import math
from random import random

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


def voltage_summing(x,y):
    '''Summing in and out of phase voltage in quatreture'''        
    return np.sqrt(x**2+y**2)


def plotting(x,y,x_label='CurrentH',y_label='HVoltage',legend='NA',color=False):
    '''This is more for directed plotting, only if you know what you want, you
    would need to use the changing_values function to see which voltages have
    actual values in it'''
    
    if not color:
        r = random()
        g = random()
        b = random()
        color=(r,g,b)
    
    plt.plot(x,y,label=legend,color=color)
        
    plt.title('{} vs {}'.format(x_label,y_label))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    

def main():
    
    directory = '../Sr327 metamagnetic transition/'
    
    if not os.path.exists('{}extras/'.format(directory)):
        sorting(directory)
    
    root01 = Dataset('{}2021_07_16_05_Sr327mmtnew_001.nc'.format(directory),'r')
    root02 = Dataset('{}2021_07_16_02_Sr327mmtnew_001.nc'.format(directory),'r')
    root03 = Dataset('{}2021_07_15_08_Sr327mmtnew_005.nc'.format(directory),'r')
    #changing_values(root)
    
    fig = plt.figure(figsize=[7,5])
    
    #plotting(root['CurrentH'][:],root['HVoltage'][:],'Field (T)','Voltage (V)','summed')
    
    plotting(root01['CurrentH'][:],voltage_summing(root01['EVoltage'][:],root01['GVoltage'][:]),'Field (T)','Total Voltage (V)','.1mA',color='b')
    plotting(root02['CurrentH'][:],voltage_summing(root02['EVoltage'][:],root02['GVoltage'][:])-1,'Field (T)','Total Voltage (V)','.2mA',color='g')
    plotting(root03['CurrentH'][:],voltage_summing(root03['EVoltage'][:],root03['GVoltage'][:])-6,'Field (T)','Total Voltage (V)','.5mA',color='r')
    
    plt.legend()
    
    ax = plt.gca()
    ax.set_xlim(7,12)
    ax.set_ylim(1.4,3.4)
    
    plt.show()
    
    #fig.savefig('../Sr327 metamagnetic transition/plots/comparing_currents.png',dpi=400,bbox_inches='tight')
    
main()