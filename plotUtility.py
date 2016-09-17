# -*- coding: utf-8 -*-
"""

plotUtility: Module for preparing data for for plots

Martin N. Pedersen

2016

"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import gridspec
import h5py
import numpy as np
import seaborn as sns
sns.set(font_scale=1.4,rc={'image.cmap': 'rainbow'})

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
        IQ = []
        errors = []
        for name in data_sets:
            errors = f[name+'Global/Data_set/Errorbars'][:,1:]
            for num, delay in enumerate(f['Global/Averaged']):
                file_names.append(delay.split(sep='_')[-1])
                outliers = f['Global/Averaged/'+delay+'/Outliers']
                inliers = f['Global/Averaged/'+delay+'/Selected_curves']
                Q = f['Global/Averaged/'+delay+'/Mean'][:,0]
                IQ.append(f['Global/Averaged/'+delay+'/Mean'][:,1])
                errors.append(f['Global/Averaged/'+delay+'/Errors'][:,1])
                num_outliers = np.shape(outliers)[1]-1 # -1 to account for Q-vector
                num_inliers = np.shape(inliers)[1]-1 # -1 to account for Q-vector
            
                if num_outliers == 1 and np.allclose(outliers[0,1], 0): # not a strong comparison
                    num_outliers = 0
                
                total_number = num_outliers+num_inliers
                
                legend = '{delay} ({inliers}/{total})'.format(delay=delay.split(sep='_')[-1], inliers=num_inliers, total=total_number)
                legends.append(legend)
            
            variables = [Q, np.array(IQ), np.array(errors), file_names, legends]
            names = ['Q', 'IQ', 'error', 'file_names', 'legends']
            plot_data= {}
            
            for num, name in enumerate(names):
                plot_data[name] = variables[num]
                
            individual_plot_data[name] = plot_data
            
    return individual_plot_data


#%%

def svd_differentials(h5file, delay, colorblind=False):
    num_comps = 4
    with h5py.File(h5file) as f:
        for entry in f['Global/Merged/']:
            if entry.split(sep='_')[-1] == delay:
                Q = f['Global/Merged/'+entry][:,0]
                IQ = f['Global/Merged/'+entry][:,1:]
                
        U, s, V = np.linalg.svd(IQ)
        
        
        figure = plt.figure(figsize=(14,10))
        gs = gridspec.GridSpec(2,2)
        
        axes = plt.subplot(gs[0,:])
        plt.title('SVD analysis of raw Differentials\nDelay = {delay}'.format(delay=delay))
        plt.xlabel('Q (1/A)')
        plt.ylabel('Component variance multiplied by Q')
        for num in range(num_comps):
            plt.plot(Q, np.tile(-num, len(Q)), '-k')
            plt.plot(Q, U[:,num]*Q-num, label='Comp. {num}'.format(num=num+1))
        plt.legend(loc='best')
        plt.ylim(-4,1)
        plt.xlim(0, max(Q)+2)
        plotbox =axes.get_position()
        axes.set_position([plotbox.x0, plotbox.y0, plotbox.width, plotbox.height*0.90])
            
        plt.subplot(gs[1,0])
        plt.xlabel('Frame')
        plt.ylabel('Scaled component weigth')
        for num in range(num_comps):
            plt.plot(np.tile(-num, len(V)), '-k')
            plt.plot(V[:,num]-num)
        
        plt.subplot(gs[1,1])
        plt.xlabel('Component')
        plt.ylabel('Singular Value Decomposition')
        plt.loglog(s[:-3], 'o')
        
        plt.show()
        
        
#%%

def cov_differentials(h5file, delay, colorblind=False):
    with h5py.File(h5file) as f:
        for entry in f['Global/Merged/']:
            if entry.split(sep='_')[-1] == delay:
                Q = f['Global/Merged/'+entry][:,0]
                IQ = f['Global/Merged/'+entry][:,1:]
    

    plt.figure(figsize=(14,10))

    plt.subplot(121)            
    covariance = np.cov(IQ)
    cov_transformed = np.log10(np.abs(covariance))
     
    plt.imshow(cov_transformed, interpolation='none', extent=[min(Q),max(Q),max(Q),min(Q)])
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.xlabel('Q (1/A)')
    plt.ylabel('Q (1/A)')
    
    
    plt.subplot(122)
    covariance = np.cov(IQ.T)
    cov_transformed = np.log10(np.abs(covariance))
    plt.imshow(cov_transformed, interpolation='none')
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.xlabel('Frame')
    plt.ylabel('Frame')
        
    plt.show()    

#%%                

def corr_differentials(h5file, delay, colorblind=False):
    with h5py.File(h5file) as f:
        for entry in f['Global/Merged/']:
            if entry.split(sep='_')[-1] == delay:
                Q = f['Global/Merged/'+entry][:,0]
                IQ = f['Global/Merged/'+entry][:,1:]
                
    
    plt.figure(figsize=(14,10))

    plt.subplot(121)            
    correlation = np.corrcoef(IQ)
     
    plt.imshow(correlation, interpolation='none', extent=[min(Q),max(Q),max(Q),min(Q)])
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.xlabel('Q (1/A)')
    plt.ylabel('Q (1/A)')
    
    
    plt.subplot(122)
    correlation = np.corrcoef(IQ.T)
    plt.imshow(correlation, interpolation='none')
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.xlabel('Frame')
    plt.ylabel('Frame')
        
    plt.show()    
    
    
 