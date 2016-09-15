# -*- coding: utf-8 -*-
"""

plotUtility: Module for preparing data for for plots

Martin N. Pedersen

2016

"""

import matplotlib.cm as cm
import h5py
import numpy as np

#%%

def prepare_merged_data(h5file, colorblind=False):
    legends = []
    file_names = []
    with h5py.File(h5file) as f:
        Q = f['Global/Data_set/IQ_curves'][:,0]
        IQ = f['Global/Data_set/IQ_curves'][:,1:]
        errors = f['Global/Data_set/Errorbars'][:,1:]
        
        for num, delay in enumerate(f['Global/Averaged']):
            file_names.append(delay.split(sep='_')[-1])
            outliers = f['Global/Averaged/'+delay+'/Outliers']
            inliers = f['Global/Averaged/'+delay+'/Selected_curves']
            
            num_outliers = np.shape(outliers)[1]-1 # -1 for Q
            num_inliers = np.shape(inliers)[1]-1 # -1 for Q
            
            if num_outliers == 1 and np.allclose(outliers[0,1], 0): # not a strong comparison
                num_outliers = 0
                
            total_number = num_outliers+num_inliers
            
            legend = '{delay} ({inliers}/{total})'.format(delay=delay.split(sep='_')[-1], 
                                                        inliers=num_inliers, total=total_number)
            legends.append(legend)
            
    variables = [Q, IQ, errors, file_names, legends]
    names = ['Q', 'IQ', 'errors', 'file_names', 'legends']
    plot_data= {}
        
    for num, name in enumerate(names):
        plot_data[name] = variables[num]
    
    return plot_data
    
    
#%% 
    
def prepare_individual_data(h5file, data_sets, colorblind=False):
    individual_plot_data = {}
    
    with h5py.File(h5file) as f:
        legends = []
        file_names = []
        for name in data_sets:
            Q = f[name+'/Data_set/IQ_curves'][:,0]
            IQ = f[name+'/Data_set/IQ_curves'][:,1:]
            errors = f[name+'Global/Data_set/Errorbars'][:,1:]
            for num, delay in enumerate(f['Global/Averaged']):
                file_names.append(delay.split(sep='_')[-1])
                outliers = f['Global/Averaged/'+delay+'/Outliers']
                inliers = f['Global/Averaged/'+delay+'/Selected_curves']
            
                num_outliers = np.shape(outliers)[1]-1 # -1 for Q
                num_inliers = np.shape(inliers)[1]-1 # -1 for Q
            
                if num_outliers == 1 and np.allclose(outliers[0,1], 0): # not a strong comparison
                    num_outliers = 0
                
                total_number = num_outliers+num_inliers
                
                legend = '{delay} ({inliers}/{total})'.format(delay=delay.split(sep='_')[-1], inliers=num_inliers, total=total_number)
                legends.append(legend)
            
            variables = [Q, IQ, errors, file_names, legends]
            names = ['Q', 'IQ', 'error', 'file_names', 'legends']
            plot_data= {}
            
            for num, name in enumerate(names):
                plot_data[name] = variables[num]
                
            individual_plot_data[name] = plot_data
            
    return individual_plot_data
        