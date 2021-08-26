import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os
import math
from random import random
from scipy.signal import savgol_filter

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


def voltage_summing(x,y,savgol=(0,0,0)):
    '''Summing in and out of phase voltage in quatreture and smoothing'''     
    if savgol[0]!=0:
        return savgol_filter(np.sqrt(x**2+y**2),savgol[1],savgol[2])
    else:
        return np.sqrt(x**2+y**2)


def smooth_data(V,N):
    '''This function just takes an average of the data over a given number
    of datapoints to make it easier to use a derivative on'''
    V = np.array(V[:-(len(V)%N)])
    return np.mean(V.reshape(-1,N),axis=1)


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
    
    directory ="../Sr327 metamagnetic transition/"
    #directory = '../Lingyun-data/Oct2017_327_nematic/'
    
    if not os.path.exists('{}extras/'.format(directory)):
        sorting(directory)
    
    root01 = Dataset('{}2021_08_09_05_Sr327mmtnew_002.nc'.format(directory),'r')
    root02 = Dataset('{}2021_08_09_05_Sr327mmtnew_004.nc'.format(directory),'r')
    root03 = Dataset('{}2021_08_09_05_Sr327mmtnew_006.nc'.format(directory),'r')
    root04 = Dataset('{}2021_08_10_01_Sr327mmtnew_002.nc'.format(directory),'r')
    root05 = Dataset('{}2021_08_10_01_Sr327mmtnew_004.nc'.format(directory),'r')
    root06 = Dataset('{}2021_08_10_01_Sr327mmtnew_006.nc'.format(directory),'r')
    root07 = Dataset('{}2021_08_10_02_Sr327mmtnew_002.nc'.format(directory),'r')
    #root08 = Dataset('{}2021_07_28_05_Sr327mmtSn_004.nc'.format(directory),'r')

    #changing_values(root06)
    
    N=250
    
    #smoothed_field01 = smooth_data(root01['CurrentH'][:],N)
    #smoothed_field02 = smooth_data(root02['CurrentH'][:],N)
    #smoothed_field03 = smooth_data(root03['CurrentH'][:],N)
    
    #smoothed_voltage01 = smooth_data(voltage_summing(root01['EVoltage'][:],root01['FVoltage'][:]),N)
    #smoothed_voltage02 = smooth_data(voltage_summing(root02['EVoltage'][:],root02['FVoltage'][:]),N)
    #smoothed_voltage03 = smooth_data(voltage_summing(root03['EVoltage'][:],root03['FVoltage'][:]),N)
    
    fig = plt.figure(figsize=[7,5])
    
    #plotting(root06['CurrentH'][:],root06['GVoltage'][:],'Field (T)','Voltage (V)',color='k')
        
    #linear_offset_voltage = voltage_summing(root01['HVoltage'][:],root01['GVoltage'][:])*np.linspace(1,.981,len(root01['CurrentH'][:]))
        
    para = [.5,.24,.15]
    perp = [1.02,.2,.03]
    pressure = [0,4.85,7.18]
    params = (1,55,5)
    
    plt.plot(root06['CurrentH'][:len(root01['EVoltage'])],voltage_summing(root06['EVoltage'][:len(root01['FVoltage'])],root06['FVoltage'][:len(root01['HVoltage'])])-voltage_summing(root01['EVoltage'][:],root01['FVoltage'][:]))
    
    #plotting(pressure,para,x_label='Pressure (kbar)',y_label='Peak Height (abs.)',legend='parallel',color='b')
    #plotting(pressure,perp,x_label='Pressure (kbar)',y_label='Peak Height (abs.)',legend='perpendicular',color='r')
    
    #plotting(root01['CurrentH'][:],voltage_summing(root01['EVoltage'][:],root01['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','100mK')
    #plotting(root02['CurrentH'][:],voltage_summing(root02['EVoltage'][:],root02['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','200mK')
    #plotting(root03['CurrentH'][:],voltage_summing(root03['EVoltage'][:],root03['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','300mK')
    #plotting(root04['CurrentH'][:],voltage_summing(root04['EVoltage'][:],root04['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','400mK')
    #plotting(root05['CurrentH'][:],voltage_summing(root05['EVoltage'][:],root05['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','500mK')
    #plotting(root06['CurrentH'][:],voltage_summing(root06['EVoltage'][:],root06['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','600mK')
    #plotting(root07['CurrentH'][:],voltage_summing(root07['EVoltage'][:],root07['FVoltage'][:])*2\
    #         ,'Field (T)','Total Voltage (V)','60mK')
    
    plt.legend(loc='upper right')
    #plt.title("Lingyun's data Peak height with changing pressure Sept-Oct 2017")
    ax = plt.gca()
    #ax.set_xlim(8,12.2)
    #ax.set_ylim(6.1,6.145)
    
    plt.show()
    
    #fig.savefig('../Sr327 metamagnetic transition/plots/August 26/100mKminus700mK_parallel.png',dpi=400,bbox_inches='tight')
    
main()