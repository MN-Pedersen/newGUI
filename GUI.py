# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 10:48:40 2016

@author: mpederse
"""

# PyQT4
from PyQt4.uic import loadUiType
from PyQt4 import QtCore   
from PyQt4.QtCore import SIGNAL

# numerical libraries
import numpy as np

# HDF5 libraries
#import h5py

# different merger utilities/numerical functions
from waxsStore import *
from waxsRead import *
from poolUtility import *
from expUtility import *
from OTUtility import *
#%% 
    
ui_file = 'C:\\Users\\mpederse\\Documents\\Python_scripts\\new_waxsGUI\\main_window.ui'
Ui_PlotWindow, QPlotWindow = loadUiType(ui_file )
separator = '\\'   

# *** TO DOs ***
#
# 1) add compatability with previous hdf5 files
# ['-100ps', '-3ns', '-3ns_2nd', '100ps', '100ps_2nd', '1us', '1us_2nd'] - Merger does not work correctly




class Main(QPlotWindow, Ui_PlotWindow):
    def __init__(self):
        #QtGui.QWidget.__init__(self)  from Denis program
        super(Main, self).__init__()
        self.setupUi(self)
        
        # experimental runs
        #self.connect(self.ButtonPathSelect_1, SIGNAL("clicked()"), self.ActionPathSelect1)
        
        # mask
        self.connect(self.Select_mask, SIGNAL("clicked()"), self.ActionMaskSelect)

        
        # other path settings
        #self.connect(self.ButtonPathSolute, SIGNAL("clicked()"), self.solute_select)

        # write data
        self.connect(self.gogogo, SIGNAL("clicked()"), self.Data_reduction)
        
        
        # set default values / behavior
        #self.Raw_SVD_cap.setText(str(20))
        #self.lowRankCap.setText(str(4))
        #self.Destination_folder.setText('C:\\Users\\mpederse\\Documents\\Python_scripts\\Gui_general')
        self.inp_data_folders.setText('C:\\newWaxs_data\\run36, C:\\newWaxs_data\\run38, C:\\newWaxs_data\\run42') #, C:\\newWaxs_data\\run38, C:\\newWaxs_data\\run42')
        self.inp_sample_name.setText('test3')
        self.inp_logfiles.setText('Ru3CO12.log')
        self.inp_detector_dist.setText('0.035')
        self.inp_det_binning.setText('2x2')
        self.inp_energy.setText('18')
        self.inp_beam_pos.setText('949.5, 923.5')
        self.inp_sample_thick.setText('1')
        self.inp_solvent_abs.setText('1')
        self.inp_Qmin.setText('6')
        self.inp_Qmax.setText('8')
        self.inp_reference_flag.setText('-3ns')
        self.inp_num_outl.setText('10')
        self.inp_scan_width.setText('5')
        #self.inputList.setText('100ps, 1us')
        #self.refDelay.setText('-3ns')
        #self.includeFirstLast.setCheckState(QtCore.Qt.Checked)
        
        
    
        
        
    def Data_reduction(self):
        Reduction_parameters = self.get_all_parameters()
        list_folders = self.data_folders.replace(' ','').split(sep=',')
        run_names = [directory.split(sep=separator)[-1] for directory in list_folders]        
        list_logfiles = self.log_files.replace(' ','').split(sep=',')
       
        
        if len(list_folders) > len(list_logfiles):
            if len(list_logfiles) == 1:
                list_logfiles = np.tile(list_logfiles, len(list_folders))
            else:
                raise ValueError('Please insure that logfiles are specified correctly\nEither one for all folders or one for each folder')
            
        if self.hdf5_append == '':
            destination_folder = list_folders[-1]
        else:
            destination_folder = self.hdf5_append
        h5file = destination_folder + separator + self.sample_name
        
        for num, directory in enumerate(list_folders):
            average_and_write(directory, list_logfiles[num], run_names[num], h5file, Reduction_parameters)
        
        reduce_data(h5file, Reduction_parameters)
        
    def ActionMaskSelect(self):
        folder = str(QtGui.QFileDialog.getOpenFileName())
        self.inp_detector_mask.setText(folder)
    
    def get_all_parameters(self):
        
        # variables for packing
        detector_dist = float(self.inp_detector_dist.text())
        detector_bin = str(self.inp_det_binning.text())
        Xray_energy = float(self.inp_energy.text())
        Xray_position = str(self.inp_beam_pos.text()).replace(' ','').split(sep=',')
        sample_thickness = float(self.inp_sample_thick.text())
        solvent_abs = float(self.inp_solvent_abs.text())
        norm_Qmin = float(self.inp_Qmin.text())
        norm_Qmax = float(self.inp_Qmax.text())
        reference_flag = str(self.inp_reference_flag.text())
        num_outliers = float(self.inp_num_outl.text())
        scan_width = int(self.inp_scan_width.text())
        num_points = 1200
        
        # non-packed variables
        #self.laser_spot = str(self.inp_laser_spot.text())
        #self.laser_fluence = str(self.inp_laser_fluence.text())        
        #self.sample_conc = str(self.inp_sample_conc.text())        
        self.sample_name = str(self.inp_sample_name.text()) + '.hdf5'
        self.data_folders = str(self.inp_data_folders.text())
        self.log_files = str(self.inp_logfiles.text())
        self.hdf5_append = str(self.inp_append_hdf5.text())
        #self.numb_outliers = str(self.inp_num_outl.text())
        #self.scan_width = str(self.inp_scan_width.text())
        
        exp_variable_names = ['detector_dist', 'detector_bin', 'Xray_energy', 'Xray_position',
                              'sample_thickness', 'solvent_abs', 'norm_Qmin', 'norm_Qmax', 'reference_flag', 
                              'num_outliers', 'scan_width', 'num_points']
        exp_variables = [detector_dist, detector_bin, Xray_energy, Xray_position, sample_thickness,
                         solvent_abs, norm_Qmin, norm_Qmax, reference_flag, num_outliers, scan_width,
                         num_points]
        Reduction_parameters = {}
        
        for num, name in enumerate(exp_variable_names):
            Reduction_parameters[name] = exp_variables[num]
            
        return Reduction_parameters




#%% test function 

if __name__ == '__main__':
    import sys, os
    from PyQt4 import QtGui

    
    
    
    
    app = QtGui.QApplication(sys.argv)
    main = Main()
    main.show()
    
    
    sys.exit(app.exec_())   