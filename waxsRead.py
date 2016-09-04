# -*- coding: utf-8 -*-
"""

waxsRead: Module for reading data from the different time delays and subtract 
and average

Martin N. Pedersen

2016

"""


from OTUtility import detect_outliers
from poolUtility import return_all_delays
import numpy as np
import h5py


#%%

def create_lists(h5file):
    with h5py.File(h5file, 'a') as f: # 'a'
        curve_indices = []
        for run in f:
            if run == 'Global':
                continue
            frame_numbers = f[run+'/Raw_data/frame_numbers'][:]
            for delay in f[run+'/Raw_data/']:
                if delay == 'frame_numbers':
                    continue
                if  'file_numbers' in f[run+'/Raw_data/'+delay+'/']:
                    continue
                
                
                delay_indices = f[run+'/Raw_data/'+delay+'/file_indices'][:]
                
                #for what in f[run+'/Raw_data/'+delay+'/']:
                #    print(what)

                curve_indices.append(frame_numbers[delay_indices])
                f[run+'/Raw_data/'+delay+'/file_numbers'] = frame_numbers[delay_indices]
                
                
                
#    return curve_indices
                
            
            
#%%
            
#mypath = 'C:\\newWaxs_data\\DCM_heating1\\'
#logfile = 'run01.log'
#destination_folder = 'C:\\newWaxs_data\\DCM_heating1\\'
#h5name = 'test.hdf5'    

#create_lists(destination_folder, h5name)





#%% 

def subtract_data(data_file, reference_file, Qvector, Reduction_parameters):
    Qmin = Reduction_parameters['norm_Qmin']
    Qmax = Reduction_parameters['norm_Qmax']
    
    Qindex = (Qvector > Qmin) & (Qvector < Qmax)
    
    scale_data = np.trapz(data_file[Qindex], x=Qvector[Qindex])
    scale_reference = np.trapz(reference_file[Qindex], x=Qvector[Qindex])
    #print('scales are: %0.2f and %0.2f' %  (scale_data, scale_reference))
    #print('number of data points used is: %i' % np.sum(Qindex))
    difference = data_file/scale_data-reference_file/scale_reference
    return difference #,  data_file/scale_data, reference_file/scale_reference
    
    




#%%

def calculate_differences(h5file, Reduction_parameters):
    """ 
    
    
    if image number i and j are two references i taken before the non reference image k, and j taken after, the reference to use for image k was:
    I_i + (I_j-I_i)/(j-i)*(k-i). This minimize the effect of slow drifts.
    
    
    """

    
    
    sort_debug = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','x','y','z']
    ref_flag = Reduction_parameters['reference_flag']
    with h5py.File(h5file, 'a') as f: 
        #debugging = []
        for run in f:
            if 'Reduced/' in f[run]:
                del f['{run}/Reduced/'.format(run=run)]
            if run == 'Global':
                continue
            
            for num, delay in enumerate(f[run+'/Raw_data']):
                reduction_text = []
                difference_curves = []
                #scaled_data = []
                #references = []
                if delay.endswith(ref_flag):
                    for item in f[run+'/Raw_data/'+delay]:
                        print(item)
                    #print(run+'/Raw_data/'+delay+'/file_numbers')
                    refence_numbers = f[run+'/Raw_data/'+delay+'/file_numbers'][:]
                    reference_data = f[run+'/Raw_data/'+delay+'/1D'][:,1:]
                    Qvector =  f[run+'/Raw_data/'+delay+'/1D'][:,0]
                    continue
                
                elif delay.startswith('frame'):
                    print('not doing anything')
                    continue
                
                else:
                    #print(run+'/Raw_data/'+delay+'/file_numbers')
                    data_numbers = f[run+'/Raw_data/'+delay+'/file_numbers'][:]
                    data = f[run+'/Raw_data/'+delay+'/1D'][:,1:]
                    difference_curves.append(Qvector)
                    #print('Shape of data is:')
                    #print(np.shape(data))
                    

                
                #print(delay)
                for num2, file_number in enumerate(data_numbers):
                    try:
                        reference_before_number = refence_numbers[refence_numbers < file_number][-1]
                    except IndexError:
                        reference_before_number = 0
                        
                        
                    try:
                        reference_after_number = refence_numbers[refence_numbers > file_number][0]
                    except IndexError:
                        reference_after_number = reference_before_number
                        
                    
                    
                    #print('Reference curves used for curve %i are %i and %i'
                    #                      % (file_number, reference_before_number, reference_after_number))
                    reduction_text.append('Reference curves used for curve %i are (%i and %i)\n'
                                          % (file_number, reference_before_number, reference_after_number))
                    
                    before_reference = reference_data[:,refence_numbers == reference_before_number]
                    after_reference = reference_data[:,refence_numbers == reference_after_number]
                    

                    if reference_before_number != reference_after_number:
                        local_reference_curve = before_reference-\
                                             (after_reference-before_reference)/\
                                             (reference_after_number-reference_before_number)*\
                                             (file_number-reference_before_number)
                    else:
                        local_reference_curve = before_reference
                   
                    #print('here')
                    # logic taking care of normalization
                    local_reference_curve = np.squeeze(local_reference_curve)  
                    difference_curve = subtract_data(data[:,num2], local_reference_curve, Qvector, Reduction_parameters)

                    #scaled_data.append(data_curve)
                    #references.append(scaled_reference)                   
                    difference_curves.append(difference_curve)
                
                
                #debugging.append([scaled_data, references, difference_curves])
                #print(np.shape(difference_curves))
                reduced_data_string = '{run}/Reduced/{debug}_difference_{delay}'.format(run=run, debug=sort_debug[num], delay=delay[6:])
                reduction_log_string = '{run}/Reduced/logs/{debug}_log_{delay}'.format(run=run, debug=sort_debug[num], delay=delay[6:])
                f[reduced_data_string] = np.array(difference_curves).T
                f[reduction_log_string] =  np.string_(reduction_text).T
    #return debugging 

#%%

def calculate_references(h5file, Reduction_parameters):
    reference_flag = Reduction_parameters['reference_flag']
    with h5py.File(h5file, 'a') as f: 
        #debugging = []
        for run in f:
            if run == 'Global':
                continue
            references = []
            for delay in f[run+'/Raw_data/']:
                if delay.endswith(reference_flag):
                    #print(delay)
                    Qvector = f[run+'/Raw_data/'+delay+'/1D'][:,0]
                    IQ = f[run+'/Raw_data/'+delay+'/1D'][:,1:]
                    file_numbers = f[run+'/Raw_data/'+delay+'/file_numbers']
                    references.append(Qvector)
                    #print(references)
                    
                    
                    for num, file_number in enumerate(list(file_numbers)):
                        if num == 0:
                            difference_curve = subtract_data(IQ[:,num], IQ[:,num+1], Qvector, Reduction_parameters)
                            references.append(difference_curve)
                        elif num == (len(file_numbers)-1):
                            difference_curve = subtract_data(IQ[:,num], IQ[:,num-1], Qvector, Reduction_parameters)
                            references.append(difference_curve)
                        else:
                            scale = (file_numbers[num+1]-file_numbers[num-1])*(file_number-file_numbers[num-1])
                            local_reference = IQ[:,num-1]-(IQ[:,num+1]-IQ[:,num-1])/scale
                            difference_curve = subtract_data(IQ[:,num], local_reference, Qvector, Reduction_parameters)
                            references.append(difference_curve)
                    data_string = '{run}/Reduced/a_reference_{delay}'.format(run=run, delay=delay.split(sep='_')[2])
                    f[data_string] = np.array(references).T
                            


#%%

def store_averaged(h5file, Reduction_parameters):
    iterations = ['a_First', 'b_Second', 'c_Third', 'd_Fourth', 'e_Fifth']
    num_outliers = Reduction_parameters['num_outliers']/100*Reduction_parameters['num_points'] 
    num_multipliers = Reduction_parameters['scan_width']
    with h5py.File(h5file, 'a') as f:           
        for run in f:
            if 'Averaged/' in f[run]:
                del f['{run}/Averaged/'.format(run=run)]
            if run == 'Global':
                continue
                
            for reduced_data in f[run+'/Reduced']:
                if reduced_data == 'logs':
                    continue
                
                else:
                    Qvector = np.atleast_2d(f[run+'/Reduced/'+reduced_data][:,0]).T
                    difference_curves = f[run+'/Reduced/'+reduced_data][:,1:]
                    variables = detect_outliers(difference_curves, num_multipliers, num_outliers)
                    #print(np.shape(variables))
                    variable_names = ['Selected_curves', 'Outliers', 'Means', 'Stds']
                    
                    for num, name in enumerate(variable_names):
                        if (name == 'Selected_curves') or (name == 'Outliers'):
                            for num2 in range(num_multipliers):
                                data_string = '{run}/Averaged/{delay}/{variable_name}/{iteration}'.format(
                                                run=run, delay=reduced_data, variable_name=name, iteration=iterations[num2])
                                data = variables[num][num2]
                                data_with_Q = np.column_stack((Qvector,data))
                                f[data_string] = data_with_Q
                        else:
                            data_string = '{run}/Averaged/{delay}/{variable_name}'.format(
                                                run=run, delay=reduced_data, variable_name=name)
                            data = np.array(variables[num]).T
                            data_with_Q = np.column_stack((Qvector,data))
                            f[data_string] = data_with_Q

                
                print('Finished with {delay}'.format(delay=reduced_data))
                
#%%
                
def data_merger(h5file, Reduction_parameters):
    reference_flag = Reduction_parameters['reference_flag']
    sort_debug = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','x','y','z', 'zz', 'zzz','zzzz',
                  'zzzzz','zzzzzz'] # reference is always first
    grouped_retrive_strings, unique_time_delays, time_seconds = return_all_delays(destination_folder, h5name)
    with h5py.File(h5file, 'a') as f:
        if 'Global' in f:
            del f['Global']
        for num, string_group in enumerate(grouped_retrive_strings):
            data_set = f[grouped_retrive_strings[num][0]][:,0]
            for string in string_group:
                IQ_data = f[string][:,1:]
                data_set = np.column_stack((data_set,IQ_data))
                delay = string.split(sep='_')[-1]
            if string.endswith(reference_flag):
                 group_path = 'Global/Merged/{debug}_reference_{delay}'.format(debug=sort_debug[num], delay=delay)
            else:
                group_path = 'Global/Merged/{debug}_difference_{delay}'.format(debug=sort_debug[num], delay=delay)
            f[group_path] = data_set
    f['Global/Merged/Time_seconds'] = time_seconds
                
    

#%%

def merged_averager(h5file, Reduction_parameters):
    iterations =  ['a_First', 'b_Second', 'c_Third', 'd_Fourth', 'e_Fifth']
    num_multipliers = Reduction_parameters['scan_width']
    num_outliers = Reduction_parameters['num_outliers']
    with h5py.File(h5file, 'a') as f:
        for num, delay in enumerate(f['Global/Merged/']):
            if delay == 'Time_seconds':
                continue
            
            Qvector = f['Global/Merged/'+delay][:,0]
            IQ = f['Global/Merged/'+delay][:,1:]
            variables = detect_outliers(IQ, num_multipliers, num_outliers)
            variable_names = ['Selected_curves', 'Outliers', 'Means', 'Stds']
                    
            for num, name in enumerate(variable_names):
                if (name == 'Selected_curves') or (name == 'Outliers'):
                    for num2 in range(num_multipliers):
                        data_string = 'Global/Averaged/{delay}/{variable_name}/{iteration}'.format(
                                                delay=delay, variable_name=name, iteration=iterations[num2])
                        data = variables[num][num2]
                        data_with_Q = np.column_stack((Qvector,data))
                        f[data_string] = data_with_Q
                else:
                    data_string = 'Global/Averaged/{delay}/{variable_name}'.format(
                                                delay=delay, variable_name=name)
                    data = np.array(variables[num]).T
                    data_with_Q = np.column_stack((Qvector,data))
                    f[data_string] = data_with_Q

#%%

def select_curves(h5file, Reduction_parameters):
    selected_curves = []
    selected_curves_std = []
    with h5py.File(h5file, 'a') as f:           
        for run in f:
            if run == 'Global':
                if 'Data_set' in f[run]:
                    del f[run+'/Data_set']
                
                for num, delay in enumerate(f[run+'/Averaged']):
                    Qvector = f[run+'/Averaged/'+delay+'/Stds'][:,0]
                    if num == 0:
                        selected_curves.append(Qvector)
                        selected_curves_std.append(Qvector)
                    
                    std_data = f[run+'/Averaged/'+delay+'/Stds'][:,1:]
                    mean_data =  f[run+'/Averaged/'+delay+'/Means'][:,1:]
 
                    # assume to begin with that curveis the one
                    # with the lowest overall std. The do a numerical comparison
                    # and select the curve with highest amount curves included
                    # could throw away low Q out for this work
                    numbers_scan = Reduction_parameters['scan_width']
                    summed_std = [np.sum(std_data[:,num]) for num in range(numbers_scan)]
                    min_std_index = np.argmin(summed_std)
                    data_comparisons = [np.allclose(mean_data[:,min_std_index], mean_data[:,num]) for num in range(numbers_scan)]
                    
                    best_index = np.nonzero(data_comparisons)[-1]
                    selected_curves.append(np.squeeze(mean_data[:,best_index]))
                    selected_curves_std.append(np.squeeze(std_data[:,best_index]))
                    
                    
                mean_write_string = run+'/Data_set/IQ_curves'
                std_write_string = run+'/Data_set/Std_curves'
                f[mean_write_string] = np.array(selected_curves).T
                f[std_write_string] = np.array(selected_curves_std).T    


#%%


def reduce_data(h5file, Reduction_parameters):
    create_lists(h5file)
    calculate_differences(h5file, Reduction_parameters)
    calculate_references(h5file, Reduction_parameters)
    data_merger(h5file, Reduction_parameters)
    store_averaged(h5file, Reduction_parameters)
    merged_averager(h5file, Reduction_parameters)
    select_curves(h5file, Reduction_parameters)




#%%
                    
                    
#calculate_differences(destination_folder, h5name)                    
#store_averaged(destination_folder, h5name)

#%%



#%%
#import matplotlib.pyplot as plt
#ps100 = np.array(debugging[2][0]).T
#reference = np.array(debugging[2][1]).T

#num_invest = 5
#fig = plt.figure()
#plt.plot(ps100[:,num_invest])
#plt.plot(reference[:,num_invest])

#fig = plt.figure()
#plt.plot(ps100[:,num_invest]-reference[:,num_invest])


#scale  = np.linalg.lstsq(np.atleast_2d(ps100[:,num_invest]).T,reference[:,num_invest])

#fig = plt.figure()
#plt.plot(ps100[:,num_invest]*scale[0]-reference[:,num_invest])




#%% 


if __name__ == '__main__':
    mypaths = ['C:\\newWaxs_data\\dye2_test8\\', 'C:\\newWaxs_data\\dye2_test9\\', 'C:\\newWaxs_data\\dye2_test10\\']
    logfiles = ['run08.log','run09.log','run10.log']
    destination_folder ='C:\\newWaxs_data\\dye2_test10\\'
    h5name = 'test.hdf5'
    
    
    import numpy as np
    import h5py
#    def experimental_info():
#        detector_dist = 0.035
#        energy = 18 
#        beam_pos = [959.5, 954.5]
#        pixel_size = 88.54e-06
#        return detector_dist, energy, beam_pos, pixel_size
    for num, mypath in enumerate(mypaths):
        create_lists(destination_folder, h5name)
        calculate_differences(destination_folder, h5name)
        calculate_references(destination_folder, h5name)
        data_merger(destination_folder, h5name)
        store_averaged(destination_folder, h5name)
        merged_averager(destination_folder, h5name)
        print('finished')
        

    

    