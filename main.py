import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os
import math
from random import random
from scipy.signal import savgol_filter
from scipy import interpolate

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
    
    
def quadratic(a,b,c):
    '''Litterally just solving the quadratic formula for x'''
    return (-b+np.sqrt(b**2-4*a*c))/(2*a),(-b-np.sqrt(b**2-4*a*c))/(2*a)


def tin_transition_pressure(Tc):
    '''Takes the Tc of the tin transition to determine the pressure'''
    return quadratic(3.9*10**-4,-4.95*10**-2,-Tc+3.732)


def smooth_data(V,N):
    '''This function just takes an average of the data over a given number
    of datapoints to make it easier to use a derivative on'''
    V = np.array(V[:-(len(V)%N)])
    return np.mean(V.reshape(-1,N),axis=1)


def plotting(x,y,x_label='CurrentH',y_label='HVoltage',legend='NA',color=False,scatter=False):
    '''This is more for directed plotting, only if you know what you want, you
    would need to use the changing_values function to see which voltages have
    actual values in it'''
    
    if not color:
        r = random()
        g = random()
        b = random()
        color=(r,g,b)
    if scatter:
        plt.scatter(x,y,label=legend,color=color)
    else:
        plt.plot(x,y,label=legend,color=color)
        
    plt.title('{} vs {}'.format(x_label,y_label))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    
def tin_plot(absolute,temps,FWHM=[],range_temps=(3,3.9)):
    '''Takes the abs and FWHM info, plots and makes a fit along with an
    average in between the two fits'''
    
    m, b = np.polyfit(temps,absolute,1)
    x = np.linspace(0,4,100)
    y = m*x+b
    m2, b2 = np.polyfit(temps,FWHM,1)
    y2 = m2*x+b2
    
    average = [(g + h) / 2 for g, h in zip(absolute,FWHM)]
    
    m3,b3 = np.polyfit(temps,average,1)
    y3 = m3*x+b3
    
    plotting(x,y,legend='',color='b')
    plotting(x,y2,legend='',color='r')
    plotting(x,y3,legend='Average',color='k')
    
    plotting(temps,absolute,x_label='Transition Tc (K)',y_label='Peak Height (V)',legend='absolute',color='b',scatter=True)
    if FWHM:
        plotting(temps,FWHM,x_label='Transition Tc (K)',y_label='Peak Height (V)',legend='FWHM',color='r',scatter=True)
    
    ax = plt.gca()
    ax.set_xlim(range_temps[0],range_temps[-1])
    ax.set_ylim(0,max(absolute))
    
    
def subtract_peak_heights(initial,subtractor,savgol=(0,0,0)):
    '''This function takes the data from 100mk and subtracts it from data of a
    different H range at higher temperatures and returns the subtracted value
    '''
    
    initial_start_H = round(float(initial['CurrentH'][0]),2)
    initial_end_H = round(float(initial['CurrentH'][-1]),2)
    
    start = np.argmin(np.abs(np.array(subtractor['CurrentH'][:])-initial_start_H))
    end = np.argmin(np.abs(np.array(subtractor['CurrentH'][:])-initial_end_H))
    
    sub = voltage_summing(subtractor['EVoltage'][start:end],subtractor['FVoltage'][start:end],savgol=savgol)
    ini = voltage_summing(initial['EVoltage'][:],initial['FVoltage'][:],savgol=savgol)
    
    try:
        f = interpolate.interp1d(subtractor['CurrentH'][start:end], sub, kind='nearest',fill_value="extrapolate")
    except ValueError:
        subs = subtractor['CurrentH'][end:start]
        sub = voltage_summing(subtractor['EVoltage'][end:start],subtractor['FVoltage'][end:start],savgol=savgol)
        f = interpolate.interp1d(subs, sub, kind='nearest',fill_value="extrapolate")
    
    returned_list = []
    counter=0
    for i in initial['CurrentH'][:]:
        
        returned_list.append(-ini[counter]+float(f(i)))
        counter+=1
    
    return np.array(returned_list)

def main():
    
    directory ="../Sr327 metamagnetic transition/Tin/"
    #directory = '../Lingyun-data/Oct2017_327_nematic/'
    
    if not os.path.exists('{}extras/'.format(directory)):
        sorting(directory)
    
    root01 = Dataset('{}2021_08_08_02_Sr327mmtSn_001.nc'.format(directory),'r')
    root02 = Dataset('{}2021_08_08_02_Sr327mmtSn_002.nc'.format(directory),'r')
    root03 = Dataset('{}2021_08_08_02_Sr327mmtSn_003.nc'.format(directory),'r')
    root04 = Dataset('{}2021_08_08_02_Sr327mmtSn_004.nc'.format(directory),'r')
    root05 = Dataset('{}2021_08_08_02_Sr327mmtSn_005.nc'.format(directory),'r')
    root06 = Dataset('{}2021_08_08_02_Sr327mmtSn_006.nc'.format(directory),'r')

    #changing_values(root06)
    
    N=250
    
    #smoothed_field01 = smooth_data(root01['CurrentH'][:],N)
    #smoothed_field02 = smooth_data(root02['CurrentH'][:],N)
    #smoothed_field03 = smooth_data(root03['CurrentH'][:],N)
    
    #smoothed_voltage01 = smooth_data(voltage_summing(root01['EVoltage'][:],root01['FVoltage'][:]),N)
    #smoothed_voltage02 = smooth_data(voltage_summing(root02['EVoltage'][:],root02['FVoltage'][:]),N)
    #smoothed_voltage03 = smooth_data(voltage_summing(root03['EVoltage'][:],root03['FVoltage'][:]),N)
    
    fig = plt.figure(figsize=[9,7])
    
    #plotting(root01['CurrentH'][:],root01['GVoltage'][:],'Field (T)','Voltage (V)',color='k')
        
    #linear_offset_voltage = voltage_summing(root01['HVoltage'][:],root01['GVoltage'][:])*np.linspace(1,.981,len(root01['CurrentH'][:]))

    params = (1,35,5)
    
    abs_ = [.46,.3,.2]
    FWHM = [9.5,7.5,5,2.75]
    temps = [0,1.96,3.89]
    
    m, b = np.polyfit([3.89,1.96],[.74,.9],1)
    x = np.linspace(0,8,100)
    y = m*x+b
    m2, b2 = np.polyfit([0,4.85,7.18],[1.02,.2,.03],1)
    y2 = m2*x+b2
    
    #tin_plot(abs_,temps,FWHM,range_temps=(3.095,3.7))
    
    #plt.scatter([3.89,1.96],[.74,.9],label='Our Data')
    #plt.scatter([0,4.85,7.18],[1.02,.2,.03],label='Lingyuns Data')
    #plt.plot(x,y)
    #plt.plot(x,y2)
    
    #plus,minus = tin_transition_pressure(3.545)
    #print(plus,minus)
    
    #plotting(x,y,legend='',color='b')
    #plotting(x2,y2,legend='',color='r')
    #plotting(temp,para,x_label='Pressure (kbar)',y_label='Peak Height (V)',legend='parallel',color='b',scatter=True)
    #plotting(temp,perp,x_label='Pressure (kbar)',y_label='Peak Height (V)',legend='perpendicular',color='r',scatter=True)
    
    plotting(root01['CurrentH'][:],voltage_summing(root01['GVoltage'][:],root01['HVoltage'][:],params)-2.25\
             ,'Field (T)','Total Voltage (V)','3550mK',color='b')
    plotting(root02['CurrentH'][:],voltage_summing(root02['GVoltage'][:],root02['HVoltage'][:],params)-2.25\
             ,'Field (T)','Total Voltage (V)','',color='b')
    plotting(root03['CurrentH'][:],voltage_summing(root03['GVoltage'][:],root03['HVoltage'][:],params)-2.25\
             ,'Field (T)','Total Voltage (V)','3300mK',color='r')
    plotting(root04['CurrentH'][:],voltage_summing(root04['EVoltage'][:],root04['FVoltage'][:],params)\
             ,'Field (T)','Total Voltage (V)','',color='r')
    plotting(root05['CurrentH'][:],voltage_summing(root05['EVoltage'][:],root05['FVoltage'][:],params)\
             ,'Field (T)','Total Voltage (V)','3100mK',color='g')
    plotting(root06['CurrentH'][:],voltage_summing(root06['EVoltage'][:],root06['FVoltage'][:],params)\
             ,'Field (T)','Total Voltage (V)','',color='g')
    #plotting(root07['CurrentH'][:],voltage_summing(root07['EVoltage'][:],root07['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','700mK')
    
    plt.title("Tin Transition Widths")
    #plt.ylabel('Signal Differences (arb.)')
    #plt.xlabel('Magnetic Field (T)')
    ax = plt.gca()
    ax.set_xlim(.017,.038)
    #ax.set_ylim(-.01,.17)
    
    #ax.spines['right'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1],loc='lower right')
    
    plt.show()
    
    fig.savefig('../Sr327 metamagnetic transition/plots/September 7/Tin_transition_example.png',dpi=400,bbox_inches='tight')
    
main()