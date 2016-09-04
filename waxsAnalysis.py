# -*- coding: utf-8 -*-
"""

waxsAnalysis: Module for analysing azimuthally averaged and subtracted files
from .h5 file

Martin N. Pedersen

2016

"""
import numpy as np
import h5py

#%%

def compute_svd(h5file):
    with h5py.File(h5file, 'a') as f:
        Qvector = f['Global/Data_set/IQ_curves'][:,0]
        IQ =  f['Global/Data_set/IQ_curves'][:,1:]
        U, s, V = np.linalg.svd(IQ)
        f['Global/Analysis/SVD/Singular_values'] = s
        f['Global/Analysis/SVD/Left_sing_vectors'] = np.column_stack(Qvector, U)
        f['Global/Analysis/SVD/Left_sing_vectors'] = V            

                    
                    
#%%
                    
h5file = 'C:\\newWaxs_data\\run42\\Ru3CO12.hdf5'

select_curves(h5file, 'lol')
