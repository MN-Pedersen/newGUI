# -*- coding: utf-8 -*-
"""

waxsStore: Module for storing azimuthally average files in .h5 format

Martin N. Pedersen

2016

"""

import pyFAI
import numpy as np
import fabio

#%%

def experimental_info():
    detector_dist = 0.035
    energy = 18 
    #beam_pos = [959.5, 954.5] DCM
    beam_pos = [949.5, 923.5]
    pixel_size = 88.54e-06
    return detector_dist, energy, beam_pos, pixel_size
    
    
#%%

def get_mask(Reduction_parameters):
    if Reduction_parameters['mask_path']:
        mask_path = Reduction_parameters['mask_path']
        mask = fabio.open(mask_path).data
    else:
        dimension =  int(3840/int(Reduction_parameters['detector_bin'][0]))
        mask = np.ones((dimension, dimension))
    
    return 1-mask




#%%
    
def get_integrator(Reduction_parameters):
    detector_dist = Reduction_parameters['detector_dist']
    energy = Reduction_parameters['Xray_energy']
    beam_pos = Reduction_parameters['Xray_position']
    #print(detector_dist)
    #print(energy)
    #print(beam_pos)
    pixel_size = 4.427e-05*float(Reduction_parameters['detector_bin'][0]) 
    integrator = pyFAI.AzimuthalIntegrator(dist=detector_dist,
                                   poni1=float(beam_pos[1])*pixel_size, # Y center in units?
                                   poni2=float(beam_pos[0])*pixel_size, # X center in units?
                                   pixel1=pixel_size,
                                   pixel2=pixel_size,
                                   rot1=0,rot2=0,rot3=0,
                                   wavelength=12.398425/energy*1e-10)
    #print(integrator)
    return integrator



#%%

def FunGetCorrections(two_theta):
    cos = np.cos(np.deg2rad(two_theta)) # cos value

    #sample_coeff = sample_thickness/1000/10*sample_mu # coef sample, given in um and 1/cm resp.
    #T = 1/sample_coeff*cos/(1-cos)*(np.exp(-sample_coeff)-np.exp(-sample_coeff/cos))
    #T0 = np.exp(-sample_coeff)
    #SampleCor = T0/T
        

    phosphor_coeff = 40e-6*0.928    # phosphor width*phosphor mu.    
    PhosCor = (1-np.exp(-phosphor_coeff))/(1-np.exp(-phosphor_coeff/cos))


    Corrections = PhosCor #*SampleCor
    return Corrections
    
    
#%%


    