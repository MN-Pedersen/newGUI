# -*- coding: utf-8 -*-
"""

waxsStore: Module for storing azimuthally average files in .h5 format

Martin N. Pedersen

2016

"""



#%% Import libraries

import numpy as np
import os
import h5py
import re
import fabio
import pyFAI
import timeit
from expUtility import *

#%%

def read_log(storage_folder, logname, separator):
    """
    
    
    
    """
    print('Entering read_log')
    # variables to be returned for loop over logfile
    edf_paths = []
    time_delays = []
    SB_current = [] # single bunch current
    SR_current = [] # general storage ring current
    
    path_to_logfile = storage_folder + separator + logname
    for line in open(path_to_logfile):
        if line[0] is not '#':
            line_split = line.split()
            
            
            # append information
            edf_paths.append(storage_folder + separator + line_split[2] + '.edf')
            time_delays.append(line_split[3].replace(' - ','off'))
            SB_current.append(float(line_split[6]))
            SR_current.append(float(line_split[5]))
    
    unique_time_delays = np.unique(time_delays)
    
    
    return edf_paths, time_delays, np.array(SB_current), np.array(SR_current), unique_time_delays
    
    
#%%
    
def log_sorter(edf_paths, time_delays, unique_time_delays):
    """ 
    
    
    
    
    
    """
    print('entering log_sorter')
    
    
    # sort the time delays
    time_units = ['ps','ns','us','ms']
    time_conversions = [1e-12,1e-9,1e-6,1e-3]
    time_seconds = np.zeros(np.shape(unique_time_delays))
    
    
    # sort the unique time delays, so we from the beginning have them in order
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
    time_seconds = time_seconds[index_array]
    sorted_time_delays = unique_time_delays[index_array]
    
    # Now the different time points are sorted, time to list the paths in
    # time ordered fashion
    integration_paths = []
    int_indices = []
    
    for delay in sorted_time_delays:
        time_index = np.array(time_delays) == delay
        #print(time_index)
        #print(np.shape(time_index))
        #print(np.shape(edf_paths))
        sorted_edf_paths = np.array(edf_paths)[time_index]
        integration_paths.append(sorted_edf_paths)
        int_indices.append(time_index)

    return integration_paths, int_indices, sorted_time_delays, time_seconds         


#%% debugging
#mypath = 'C:\\newWaxs_data\\DCM_heating1\\'
#logfile = 'run01.log'
#destination_folder = 'C:\\newWaxs_data\\DCM_heating1\\'
#h5name = 'test.hdf5'

#edf_paths, time_delays, SB_current, SR_current, unique_time_delays = read_log(mypath, logfile)
    
#integration_paths, int_indices, sorted_time_delays, time_seconds =  log_sorter(edf_paths, time_delays, unique_time_delays)
    
#with h5py.File(destination_folder+'\debugging.hdf5', 'w') as f:
#    alphabet_example = ['zz9999', 'zz8888','aaaa9999','ZZ9999']
#    for name in alphabet_example:
#        group_string = 'testing/'+ name
#        f[group_string] = np.linspace(1,10,37)
        
#    real_example = ['50us','100us','200us','5ns','20ns','500ns']
#    data_for_example = [1,2,3,4,5,6]
#    for num, name in enumerate(real_example):
#        group_string = 'real/'+ name
#        f[group_string] = data_for_example[num]
        
    
#    for names in f['testing/']:
#        print(names)
    
#    print('\n')
    
#    for names in f['real/']:
#        print(names)
#        print(f['real/'+names].value)
#%%

#def get_integrator():
#    detector_dist, energy, beam_pos, pixel_size = experimental_info() 
#    integrator = pyFAI.AzimuthalIntegrator(dist=detector_dist,
#                                   poni1=beam_pos[1]*pixel_size, # Y center in units?
#                                   poni2=beam_pos[0]*pixel_size, # X center in units?
#                                   pixel1=pixel_size,
#                                   pixel2=pixel_size,
#                                   rot1=0,rot2=0,rot3=0,
#                                   wavelength=12.398425/energy*1e-10)
    
#    return integrator
    
    
    
#%%    
    
def average_and_write(data_path, logfile, run_name,  h5file, Reduction_parameters, separator):
    """


    """
    print('entering average_and_write')
    
    edf_paths, time_delays, SB_current, SR_current, unique_time_delays = read_log(data_path, logfile, separator)
    
    integration_paths, int_indices, sorted_time_delays, time_seconds =  log_sorter(edf_paths, time_delays, unique_time_delays)
    
    num_points = Reduction_parameters['num_points']
    

    with h5py.File(h5file, 'a') as f:
        if run_name in f:
            print(run_name)
            print('Data from {run} has already been averaged\nProceeding to reduction'.format(run=run_name))
        else:
            list_frames_string = '{run}/Raw_data/frame_numbers'.format(run=run_name)
            num_frames = len(int_indices[0])
            f[list_frames_string] = np.linspace(0,num_frames-1,num_frames, dtype='int')
        
            # hot fix for sorting
            sort_debug = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','x','y','z']
            for num, delay in enumerate(sorted_time_delays):
                start_time = timeit.default_timer()
                group_string = '{run}/Raw_data/{debug}_Raw_{delay}'.format(run=run_name, delay=delay, debug=sort_debug[num])
                SB_string =  group_string + '/SB_current'
                SR_string =  group_string + '/SR_current'
                f[SB_string] = SB_current
                f[SR_string] = SR_current
                indices_string = group_string + '/file_indices'
                f[indices_string] = int_indices[num]
            

                num_images = len(integration_paths[num])
                data_1D = np.zeros((num_points, num_images+1))
                mask = get_mask(Reduction_parameters)
                for count, path in enumerate(integration_paths[num]):
                    #mask_data = 'none' # for now mask=mask_data,
                    image = fabio.open(path).data
                    integrator = get_integrator(Reduction_parameters)
                    Q, IQ = integrator.integrate1d(image,npt=num_points,
                                                   correctSolidAngle=True,
                                                   polarization_factor=1,
                                                   unit='q_A^-1',
                                                   method='lut')
                    # subtract offset
                    IQ -= 10
                               
                    if count == 0:
                        two_theta, __ = integrator.integrate1d(image,npt=num_points,
                                                   correctSolidAngle=True,
                                                   polarization_factor=1,
                                                   unit='2th_deg',
                                                   method='lut')
                        
                        corrections = FunGetCorrections(two_theta)
                        IQ *= corrections
                        data_1D[:,:2]= np.array([Q, IQ]).T
                    else:
                        IQ *= corrections 
                        data_1D[:,count+1] = IQ.T
                
                data_string = group_string + '/1D'
                f[data_string] = data_1D
                correction_string = group_string + '/1D_correction'
                f[correction_string] = np.array([Q, corrections])
            # logging            
                elapsed = str((timeit.default_timer() - start_time)/60)
                print('finished with {delay} in {time}min'.format(delay=delay,time=elapsed[:4]))
                
                    
                    
                    
                    
                    
                    
                    

                    
        
        
        
        
#%% Development settings!  include in if main block


if __name__ == '__main__':
    mypaths = ['C:\\newWaxs_data\\run36\\', 'C:\\newWaxs_data\\run38\\', 'C:\\newWaxs_data\\run42\\']
    logfiles = ['run36.log','run38.log','run42.log']
    destination_folder ='C:\\newWaxs_data\\dye2_test10\\'
    h5name = 'test.hdf5'
    
#    def experimental_info():
#        detector_dist = 0.035
#        energy = 18 
#        beam_pos = [959.5, 954.5]
#        pixel_size = 88.54e-06
#        return detector_dist, energy, beam_pos, pixel_size

    for num, mypath in enumerate(mypaths):
        edf_paths, time_delays, SB_current, SR_current, unique_time_delays = read_log(mypath, logfiles[num])
    
        integration_paths, int_indices, sorted_time_delays, time_seconds =  log_sorter(edf_paths, time_delays, unique_time_delays)
    
        average_and_write(integration_paths, int_indices, sorted_time_delays, time_seconds, 
                      destination_folder, h5name, SB_current, SR_current, logfiles[num])