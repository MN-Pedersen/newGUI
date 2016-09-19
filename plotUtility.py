# -*- coding: utf-8 -*-
"""

plotUtility: Module for preparing data for for plots

Martin N. Pedersen

2016

"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import gridspec
from random import randint
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
    Q, IQ = extract_data(h5file, delay) 
                
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
    Q, IQ = extract_data(h5file, delay) 

    fig = plt.figure(figsize=(10,10))
    
    covariance = np.cov(IQ)
    cov_transformed = np.log10(np.abs(covariance))
     
    plt.imshow(cov_transformed, interpolation='none', extent=[min(Q),max(Q),max(Q),min(Q)])
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.title('log10 of absolute covariance of Differentials\nDelay = {delay}'.format(delay=delay))
    plt.xlabel('Q (1/A)')
    plt.ylabel('Q (1/A)')   
    plt.show()    

#%%                

def corr_differentials(h5file, delay, colorblind=False):
    Q, IQ = extract_data(h5file, delay) 
                
    
    fig = plt.figure(figsize=(12,10))

    correlation = np.corrcoef(IQ)
     
    plt.imshow(correlation, interpolation='none', extent=[min(Q),max(Q),max(Q),min(Q)], vmin=-1, vmax=1) # difference from using plt.clim(-1,1)?
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.title('Correlations of raw Differentials\nDelay = {delay}'.format(delay=delay))
    plt.xlabel('Q (1/A)')
    plt.ylabel('Q (1/A)')
    plt.show()   
    
    
#%%
    
    
def hold_out_test(h5file, delay, colorblind=False):
    Q, IQ = extract_data(h5file, delay)
    num_curves = np.shape(IQ)[1]
    num_repetitions = int(5)
    mean_IQ = np.mean(IQ, axis=1)
    print(np.shape(IQ))
    
    chis_test = np.zeros((num_repetitions,1))
    chis_mean = []
    chis_std = []
    
    start = int(0.1*num_curves)
    stop = int(0.95*num_curves)
    sample_sizes = list(np.linspace(start, stop, stop-start+1, dtype='int'))
    for num in sample_sizes:
        #print('Sample size')
        #print(num)
        indices = [randint(0,num_curves-1) for pick in range(num_repetitions*num)]
        indices = np.array(indices).reshape(-1,num_repetitions)

        for pick in range(num_repetitions):
            #print(np.shape(IQ[:,indices[pick]]))
            #index_TF = np.linspace(0,num_curves-1) == indices[:,pick]
            sample = IQ[:,indices[:,pick]]
            sample_mean = np.mean(sample, axis=1)
            sample_std = np.std(sample, axis=1)
            chis_test[pick] = np.sum((mean_IQ-sample_mean)**2/sample_std**2)/(num-1)
            #print('Chis_test')
            #print(chis_test)
        
        chis_mean.append(np.mean(chis_test))
        chis_std.append(np.std(chis_test))
        
        if np.mod(num,start) == 0:
            print('Finished with sample size: {sample_size}\n{size_left} tests left'.format(sample_size=num, size_left=stop-num))


    chis_mean = np.array(chis_mean)
    chis_std = np.array(chis_std)
    fig = plt.figure()
    plt.title('Signal / Noise holdout test')
    plt.ylabel('Chi-test score')
    plt.xlabel('Sample test size')
    plt.plot(sample_sizes, chis_mean, label='Mean Chi-score (n={num_reps})'.format(num_reps=num_repetitions))
    plt.fill_between(sample_sizes, chis_mean+chis_std, chis_mean-chis_std, alpha=0.6)
    plt.legend(loc='best')
    plt.show()
    
    

#%%

def Low_rank_approx(h5file):
    num_comps = 4
    with h5py.File(h5file) as f:
        Q = f['Global/Data_set/IQ_curves'][:,0]
        IQ = f['Global/Data_set/IQ_curves'][:,1:]
    
    U, s, V = np.linalg.svd(IQ)
    residuals = []
    for comps in range(num_comps):
        S = np.zeros((len(U), len(V)))
        S[:comps, :comps] = np.diag(s[:comps])
        reconstruction = np.dot(U, np.dot(S, V))
        residuals.append(IQ-reconstruction)
        
        fig = plt.figure()
        plt.title('Low rank approximation Using {comps} components\nColour is % of maximum IQ'.format(comps=comps+1))
        plt.imshow((IQ-reconstruction)/np.max(IQ)*100, aspect='auto', extent=[1, len(V), max(Q), min(Q)])
        plt.colorbar()
        plt.ylabel('Q (1/A)')
        plt.xlabel('Data curve')
        plt.show()
        

    
        
        





#%%


def extract_data(h5file, delay):
    with h5py.File(h5file) as f:
        for entry in f['Global/Merged/']:
            if entry.split(sep='_')[-1] == delay:
                Q = f['Global/Merged/'+entry][:,0]
                IQ = f['Global/Merged/'+entry][:,1:]
    
    return Q, IQ
                 