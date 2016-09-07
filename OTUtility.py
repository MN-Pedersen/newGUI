# -*- coding: utf-8 -*-
"""

waxsStore: Module for storing azimuthally average files in .h5 format

Martin N. Pedersen

2016

"""

#from expUtility import get_thresshold
import numpy as np


#%%

def detect_outliers(data_set, number_multipliers, thresshold_as_outlier):
    """
    
    
    
    
    """

    
    median_curve = np.median(data_set, axis=1)
    std_all_data = np.std(data_set,axis=1)
    
    times_std = list(np.linspace(1.5,2.5,number_multipliers,dtype=float))
    index_outlier_curves = np.zeros((np.shape(data_set)[1],len(times_std)), dtype=bool)
    
    
    for num in range(np.shape(data_set)[1]):
        discrepancy = np.abs(data_set[:,num]-median_curve)
        
        for num2, multiplier in enumerate(times_std):
            points_over_thresshold = np.sum(discrepancy >= multiplier*std_all_data)
            
            if points_over_thresshold >= thresshold_as_outlier:
                index_outlier_curves[num, num2] = True
            
            #print('number of outliers for multiplier %i was %i\nindex used is %i and curve is %i' % (multiplier, np.sum(index_outlier_curves[:,num2]), num2, num))
    
    curves_averaged = []
    outliers = []
    means = []
    stds = []        
    explanation_string = []
    for num, multiplier in enumerate(times_std):
        if np.sum(~index_outlier_curves[:,num]) > 3:
            data = data_set[:,~index_outlier_curves[:,num]]
            curves_averaged.append(data)
            means.append(np.mean(data_set[:,~index_outlier_curves[:,num]],axis=1))
            stds.append(np.std(data_set[:,~index_outlier_curves[:,num]],axis=1)/np.sqrt(np.shape(data)[1])) # divide standard dev. by sqrt(n) to get stand Err.
            #print(len(curves_averaged))
        else:
            zero_vector = np.zeros(np.shape(median_curve)).T #np.atleast_2d(
            curves_averaged.append(zero_vector)
            means.append(zero_vector)
            stds.append(zero_vector)
        
        if np.sum(index_outlier_curves[:,num]) > 3:
            outliers.append(data_set[:,index_outlier_curves[:,num]])
        else:
            zero_vector = np.atleast_2d(np.zeros(np.shape(median_curve))).T
            outliers.append(zero_vector)
        #print('shapes during iteration')
        #print(np.shape(curves_averaged))
        
        formatted_string = 'number of outliers for multiplier %i is %i\nSummed std is %0.2f' % (multiplier, np.sum(index_outlier_curves[:,num]), np.sum(stds)) 
        explanation_string.append(np.string_(formatted_string))
        
        #
       
        
    # assertions
    #if np.shape(curves_averaged)[1] == 0:
    #    curves_averaged = np.string_('None')
    #if np.shape(outliers)[1] == 0:
    #    outliers = np.string_('None')
    #if np.shape(means)[1] == 0:
    #    means = np.string_('None')
    #if np.shape(stds)[1] == 0:
    #    stds = np.string_('None')

    list_of_variables = [curves_averaged, outliers, means, stds]
        #print(np.shape(list_of_variables))
        
    
    
    return list_of_variables #, explanation_string
    
    
#%%


