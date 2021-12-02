import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os
import math
from random import random
from scipy.signal import savgol_filter
from scipy import interpolate
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import pandas as pd

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


def voltage_summing(x,y,savgol=(0,0,0,0)):
    '''Summing in and out of phase voltage in quatreture and smoothing'''     
    if savgol[0]!=0:
        return savgol_filter(np.sqrt(x**2+y**2),savgol[1],savgol[2],savgol[3])
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
        plt.plot(x,y,label=legend,color=color,linewidth=1)
        
    plt.title('{} vs {}'.format(x_label,y_label))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    
def tin_plot(absolute,temps,FWHM=[],range_temps=(3,3.9),abs_err=[],FWHM_err=[]):
    '''Takes the abs and FWHM info, plots and makes a fit along with an
    average in between the two fits'''
    
    m, b = np.polyfit(temps,absolute,1)
    x = np.linspace(0,4,100)
    y = m*x+b
    if FWHM:
        m2, b2 = np.polyfit([3,3.2,3.4,3.5,3.55,3.3,3.1],FWHM,1)
        y2 = m2*x+b2
    
        #average = [(g + h) / 2 for g, h in zip(absolute,FWHM)]
        
        #m3,b3 = np.polyfit(temps,average,1)
        #y3 = m3*x+b3
    
    plotting(x,y,legend='',color='b')
    if FWHM:
        plotting(x,y2,legend='',color='r')
        #plotting(x,y3,legend='Average',color='k')
    
    if abs_err:
        plt.errorbar(temps,absolute,yerr=abs_err, fmt='.b',label='Internal Tin')
        if FWHM_err:
            plt.errorbar([3,3.2,3.4,3.5,3.55,3.3,3.1],FWHM,yerr=FWHM_err, fmt='.r',label='External Tin')
    else:
        plotting(temps,absolute,x_label='Transition Tc (K)',y_label='Peak Height (V)',legend='Internal Tin',color='b',scatter=True)
        if FWHM:
            plotting([3,3.2,3.4,3.5,3.55,3.3,3.1],FWHM,x_label='Transition Tc (K)',y_label='Peak Height (V)',legend='External Tin',color='r',scatter=True)
    
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


def remove_extra_data(root01,root02,params=(0,0,0),perp=True):
    '''This funciton will take two netcdf files, the original with the H range
    you want the the other that will be cutoff including savgol smoothing'''
    
    Hrange = root01['CurrentH'][:]
    if perp:
        total_voltage = voltage_summing(root02['GVoltage'][:],root02['HVoltage'][:],params)
    else:
        total_voltage = voltage_summing(root02['EVoltage'][:],root02['FVoltage'][:],params)
    
    start = (np.abs(root02['CurrentH'][:]-Hrange[0])).argmin()
    end = (np.abs(root02['CurrentH'][:]-Hrange[-1])).argmin()
    
    return root02['CurrentH'][start:end],total_voltage[start:end]


def normalize_curves(dataset1,dataset2):
    '''This function takes two datasets and normalizes the zero field
    resistance to try and compare the two curves more directly and applies the
    same linear offset present in dataset1 to dataset2'''
    
    x = 'EVoltage'
    linear_offset = np.linspace(1,dataset1[x][-1]/dataset2[x][-1],len(dataset2[x][:]))
    
    return linear_offset
    

def transfer_offset(baseline,offset_dataset,subsequent):
    '''Takes the previous run that goes from 0-12T and gets the linear offset 
    and returns both the offset and the dataset of the subsequent file, which 
    is over the important field range'''
    
    root_baseline = Dataset(baseline,'r')
    root_offset_data = Dataset(offset_dataset,'r')
    root_subsequent = Dataset(subsequent,'r')
    
    linear_offset = normalize_curves(root_baseline,root_offset_data)
    
    return root_subsequent,linear_offset


def main():
    
    directory ="../Sr327 metamagnetic transition/"
    directory_ = '../Lingyun-data/Oct2017_327_nematic/'
    
    if not os.path.exists('{}extras/'.format(directory)):
        sorting(directory)
    
    root01 = Dataset('{}2021_07_29_01_Sr327mmtnew_002.nc'.format(directory),'r')
    #root02 = Dataset('{}2021_07_29_01_Sr327mmtnew_003.nc'.format(directory),'r')
    #root03 = Dataset('{}2021_07_29_01_Sr327mmtnew_005.nc'.format(directory),'r')
    root04 = Dataset('{}2021_07_30_01_Sr327mmtnew_002.nc'.format(directory),'r')
    #root05 = Dataset('{}2021_07_30_01_Sr327mmtnew_003.nc'.format(directory),'r')
    #root06 = Dataset('{}2021_07_30_02_Sr327mmtnew_001.nc'.format(directory),'r')
    #root07 = Dataset('{}2021_07_30_02_Sr327mmtnew_003.nc'.format(directory),'r')
    #root08 = Dataset('{}2021_07_15_08_Sr327mmtnew_006.nc'.format(directory),'r')
    #root09 = Dataset('{}2021_07_15_08_Sr327mmtnew_005.nc'.format(directory),'r')
    
    #root01,linear_offset = transfer_offset(directory+'2021_07_30_01_Sr327mmtnew_001.nc',directory+'2021_07_29_01_Sr327mmtnew_001.nc',directory+'2021_07_29_01_Sr327mmtnew_002.nc')
    
    fig = plt.figure(figsize=[9,7])
    
    params = (1,125,7,0)
    
    #abs_ = [15,11.1,6.9,2.55,4.8,3.6,9.1,13.3]
    #abs_err = [0.1,.2,.2,.1,.2,0,.2,.4]
    #FWHM = [15.1,10.9,6.3,3.7,1.25,7.8,12.5]
    #FWHM_err = [0,.1,.2,.4,.35,.2,.1]
    #temps = [3,3.2,3.4,3.6,3.5,3.55,3.3,3.1]
    
    #df = pd.read_csv('lingyun_mmt_transition.csv')
    #x_1 = df['x']
    #y_1 = df['y']
    
    #m, b = np.polyfit(x_1,y_1,1)
    #x = np.linspace(-.5,8,100)
    #y = m*x+b
    #m2, b2 = np.polyfit([0,4.85,7.18],[1.02,.2,.03],1)
    #y2 = m2*x+b2
    
    #tin_plot(abs_,temps,FWHM,range_temps=(3.095,3.8),abs_err=abs_err,FWHM_err=FWHM_err)
      
    #plt.plot([100,200,300,400,500,600,700],np.array([1.095,1.098,1.104,1.112,1.12,1.28,1.38])/1.095,color=(1,0,0),label='para peak @7.65T')
    #plt.plot([100,200,300,400,500,600,700],np.array([1.003,1.005,1.008,1.017,1.025,1.038,1.052])/1.003,color=(1,.5,0.5),label='para far right @8.2')
    #plt.plot([100,200,300,400,500,600,700],np.array([.961,.964,.969,.977,.986,.996,1.01])/.961,color=(1,0,.5),label='para dip @7.4T')
    
    #plt.scatter([100,200,300,400,500],np.array([8.32,8.28,8.36,8.43,8.55])/8.32,color=(0,0,1),label='perp peak @9.35T')
    #plt.scatter([1000,1000,1500,2000,2500,3000,3500,4000],np.array([7.42,7.5,8.48,9.85,11.14,12.45,13.68,15.2])/6.08,color=(0,0,1),label='')
    #plt.plot([100,200,300,400,600],np.array([5.87,5.9,6,6.08,6.35])/5.87,color=(.4,0,1),label='perp dip @8.2T')
    
    #plt.errorbar(x_2,y_2, yerr=[.002]*7, fmt='o',label='Low T, slow sweep',color='r')
    #plt.errorbar(x_1,y_1, yerr=[.028]*8, fmt='o',color='b',label='High T, fast sweep')
    
    #tin_plot(abs_,temps,range_temps=(0,3),abs_err=abs_err)

    #plt.scatter([3.89,1.96],[.74,.9],label='Our Data')
    #plt.scatter([0,4.85,7.18],[1.02,.2,.03],label='Lingyuns Data')
    #plt.scatter(x_1,y_1,color='b')
    #plt.scatter(-.56,7.65,color='r')
    #plt.plot(x,y,color='g')
    
    #plus,minus = tin_transition_pressure(3.76)
    #print(plus,minus)
    
    #plotting(x,y,legend='',color='b')
    #plotting(x2,y2,legend='',color='r')
    #plotting(temp,para,x_label='Pressure (kbar)',y_label='Peak Height (V)',legend='parallel',color='b',scatter=True)
    #plotting(temp,perp,x_label='Pressure (kbar)',y_label='Peak Height (V)',legend='perpendicular',color='r',scatter=True)
    
    x = 'GVoltage'
    y = 'HVoltage'
    
    plotting(root01['CurrentH'][:],voltage_summing(root01[x][:],root01[y][:],params)*np.linspace(1,root04[x][-1]/root01[x][-1],len(root01[x][:]))\
             ,'Field (T)','Total Voltage (V)','100mK',color='b')
    #plotting(root02['CurrentH'][:],voltage_summing(root02[x][:],root02[y][:],params)*np.linspace(1,root04[x][-1]/root02[x][-1],len(root02[x][:]))\
    #         ,'Field (T)','Total Voltage (V)','200mK',color='r')
    #plotting(root03['CurrentH'][:],voltage_summing(root03[x][:],root03[y][:],params)*np.linspace(1,root04[x][-1]/root03[x][-1],len(root03[x][:]))\
    #         ,'Field (T)','Total Voltage (V)','300mK',color='g')
    plotting(root04['CurrentH'][:],voltage_summing(root04[x][:],root04[y][:],params)\
             ,'Field (T)','Total Voltage (V)','400mK',color='r')
    #plotting(root05['CurrentH'][:],voltage_summing(root05[x][:],root05[y][:],params)*np.linspace(1,root04[x][-1]/root05[x][-1],len(root05[x][:]))\
    #         ,'Field (T)','Total Voltage (V)','500mK',color='m')
    #plotting(root06['CurrentH'][:],voltage_summing(root06[x][:],root06[y][:],params)*np.linspace(1,root04[x][-1]/root06[x][-1],len(root06[x][:]))\
    #         ,'Field (T)','Total Voltage (V)','600mK',color='c')
    #plotting(root07['CurrentH'][:],voltage_summing(root07[x][:],root07[y][:],params)*np.linspace(1,root04[x][-1]/root07[x][-1],len(root07[x][:]))\
    #         ,'Field (T)','Total Voltage (V)','700mK',color='brown')
    #plotting(root08['CurrentH'][:],voltage_summing(root08['EVoltage'][:],root08['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','150mK',color='k')
    #plotting(root09['CurrentH'][:],voltage_summing(root09['EVoltage'][:],root09['FVoltage'][:],params)\
    #         ,'Field (T)','Total Voltage (V)','100mK',color='slategray')
    
    fontsize=30
    
    plt.title("Tin Transition with Pressure",fontsize=25)
    #plt.grid()
    #plt.yticks([0,2,4,6,8,10,12,14],fontsize=fontsize)
    #plt.xticks([3.2,3.4,3.6,3.8],fontsize=fontsize)
    
    ax = plt.gca()
    #ax.set_ylim(1.4,2.1)
    #ax.set_xlim(7.5,10.2)
    plt.rcParams.update({'font.size': 23})
    
    #ax.xaxis.set_major_locator(MultipleLocator(.05))
    #ax.yaxis.set_major_locator(MultipleLocator(.005))
    #ax.grid(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xlabel('Pressure (kbar)',fontsize=30)
    ax.set_ylabel('Transitions Field (T)',fontsize=30)
    
    handles, labels = ax.get_legend_handles_labels()
    #plt.legend(handles[::1], labels[::1],loc='lower right')
    
    plt.show()
    
    #fig.savefig('../Sr327 metamagnetic transition/plots/Figure3.png',dpi=400,bbox_inches='tight')
    
main()