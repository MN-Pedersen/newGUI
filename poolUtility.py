# -*- coding: utf-8 -*-
"""

poolUtility: Utility module for merging data from different expeimental runs

Martin N. Pedersen

2016

"""
import h5py
import numpy as np
import re
from OTUtility import detect_outliers

#%%


def return_all_delays(h5file):

    #file_name = destination_folder + '\\' + h5name
    delay_list = []
    retrieve_string = []
    with h5py.File(h5file, 'a') as f:           
        for run in f:
            if run == 'Global':
                continue
            
            
            for delay_string in f[run+'/Reduced']:
                if delay_string != 'logs':
                    delay = delay_string.split(sep='_')[-1]
                    print(delay)
                    delay_list.append(delay)
                    retrieve_string.append(run+'/Reduced/'+delay_string)
                    
            unique_time_delays = list(np.unique(delay_list))
            time_units = ['ps','ns','us','ms']
            time_conversions = [1e-12,1e-9,1e-6,1e-3]
            time_seconds = np.zeros(np.shape(unique_time_delays))
            for idx1, delay in enumerate(unique_time_delays):
            # handle the case of off measurement
                if delay == 'off':
                    time_seconds[idx1] = -1e1
                    break
                else:
                    for idx2, unit in enumerate(time_units):
                        if delay.endswith(unit):
                            delay_number_float = float(re.findall("-?\d+\.?\d*",delay)[0])
                            time_seconds[idx1] = delay_number_float*time_conversions[idx2]
                            break # time in seconds have been calculated - go to next entry
                            
            index_array = np.argsort(time_seconds)
            time_seconds = np.array(time_seconds)[index_array]
            unique_time_delays = np.array(unique_time_delays)[index_array]
            grouped_retrive_strings = []
            for num, delay in enumerate(list(unique_time_delays)):
                index = delay == np.array(delay_list)
                grouped_retrive_strings.append(np.array(retrieve_string)[index])
                
                
                
    
    return grouped_retrive_strings, unique_time_delays, time_seconds 
    
    
    
#%%



#%%

#destination_folder = 'C:\\newWaxs_data\\dye2_test10\\'
#h5name = 'test.hdf5'    
    

#grouped_retrive_strings, time_seconds = return_all_delays(destination_folder, h5name)
#data_merger(destination_folder, h5name)
#merged_averager(destination_folder, h5name)                