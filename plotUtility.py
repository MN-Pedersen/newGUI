# -*- coding: utf-8 -*-
"""

plotUtility: Module for preparing data for for plots

Martin N. Pedersen

2016

"""

import matplotlib.cm as cm

#%%

def prepare_merged_data(h5file, colorblind=False):
    labels = []
    with h5py.File(h5file):
        Q = f['Global/Data_set/IQ_curves'][:,0]
        IQ = f['Global/Data_set/IQ_curves'][:,1:]
        errors = f['Global/Data_set/Errorbars'][:,1:]
        
        
        for num, delay in f['Global/Averaged']:
            delay = delay.split(sep='_')[-1]
            outliers = f['Global/Averaged/'+delay+'/Outliers']
            inliers = f['Global/Averaged/'+delay+'/Selected_curves']
            
            num_outliers = np.shape(outliers)[1]-1 # -1 for Q
            num_inliers = np.shape(inliers)[1]-1 # -1 for Q
            
            if num_outliers == 1 and np.allclose(outliers[0,1], 0):
                num_outliers = 0
                
            total_number = num_outliers+num_inliers
            
            label = '{delay} ({inliers}/{total})'.format(delay=delay, inliers=num_inliers, total)
            labels.append(label)
                