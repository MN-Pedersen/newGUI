# -*- coding: utf-8 -*-
"""

waxsStore: Module for storing azimuthally average files in .h5 format

Martin N. Pedersen

2016

"""

import pyFAI

#%%

def experimental_info():
    detector_dist = 0.035
    energy = 18 
    #beam_pos = [959.5, 954.5] DCM
    beam_pos = [949.5, 923.5]
    pixel_size = 88.54e-06
    return detector_dist, energy, beam_pos, pixel_size
    
    

#%%
    
def get_integrator(Reduction_parameters):
    detector_dist = Reduction_parameters['detector_dist']
    energy = Reduction_parameters['Xray_energy']
    beam_pos = Reduction_parameters['Xray_position']
    pixel_size = 4.427e-05*float(Reduction_parameters['detector_bin'][0]) 
    integrator = pyFAI.AzimuthalIntegrator(dist=detector_dist,
                                   poni1=float(beam_pos[1])*pixel_size, # Y center in units?
                                   poni2=float(beam_pos[0])*pixel_size, # X center in units?
                                   pixel1=pixel_size,
                                   pixel2=pixel_size,
                                   rot1=0,rot2=0,rot3=0,
                                   wavelength=12.398425/energy*1e-10)
    
    return integrator



#%%

def FunGetCorrections(two_theta, use_sample_abs, use_phos_abs, sample_thickness, sample_mu):

    cv = np.cos(np.deg2rad(tth)) # cos value
    if use_sample_abs:
        sample_coeff = sample_thickness*sample_mu # coef sample
        T = 1/csa*cv/(1-cv)*(np.exp(-csa)-np.exp(-csa/cv))
        T0 = np.exp(-csa)
        SampleCor = T0/T
    else:
        SampleCor = np.ones(cv.shape)
        
    if vval['UsePhosAbs']:
        phosphor_coeff = 40e-6*0.928    # phosphor width*phosphor mu.    
        PhosCor = (1-np.exp(-phosphor_coeff))/(1-np.exp(-phosphor_coeff/cv))
    else:
        PhosCor = np.ones(cv.shape)

    Corrections = PhosCor*SampleCor
    return Corrections, PhosCor, SampleCor