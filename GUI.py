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
import seaborn as sns
sns.set(font_scale=1.4,rc={'image.cmap': 'rainbow'})
# HDF5 libraries
#import h5py

# different merger utilities/numerical functions
from waxsStore import *
from waxsRead import *
from poolUtility import *
from expUtility import *
from OTUtility import *
from plotUtility import * 
from plot1 import PlotWindow
from plot3 import CompWindow
#%% 
    
ui_file = 'main_window.ui'  
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
        
        # standard plot
        self.connect(self.plot_standard, SIGNAL("clicked()"), self.produce_standard_plot)
        
        # SVD analysis
        self.connect(self.plot_SVD_comp, SIGNAL("clicked()"), self.produce_SVD_comps)
        
        # Signal / Noise
        self.connect(self.plot_holdanal, SIGNAL("clicked()"), self.produce_holdout)
        
        # Tranding analysis
        self.connect(self.plot_SVD_diffs, SIGNAL("clicked()"), self.produce_SVD_diffs)
        self.connect(self.plot_Cov, SIGNAL("clicked()"), self.produce_cov)
        self.connect(self.plot_Corr, SIGNAL("clicked()"), self.produce_corr)
        
        # set default values / behavior
        #self.Raw_SVD_cap.setText(str(20))
        #self.lowRankCap.setText(str(4))
        #self.Destination_folder.setText('C:\\Users\\mpederse\\Documents\\Python_scripts\\Gui_general')
        #self.inp_data_folders.setText('C:\\newWaxs_data\\run38, C:\\newWaxs_data\\run42') #, C:\\newWaxs_data\\run38, C:\\newWaxs_data\\run42')C:\\newWaxs_data\\run36
        self.inp_data_folders.setText('C:\\data\\run38, C:\\data\\run42')       
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
        self.inp_delays_diffs.setText('-3ns')
        self.inp_delays_SN.setText('-3ns')
        #self.inp_scan_width.setText('5')
        #self.inputList.setText('100ps, 1us')
        #self.refDelay.setText('-3ns')
        #self.includeFirstLast.setCheckState(QtCore.Qt.Checked)
        
        
        # preparing global variables
        self.Reduction_parameters = self.get_all_parameters()
        if self.hdf5_append == '':
            destination_folder = self.data_folders[-1]
        else:
            destination_folder = self.hdf5_append
        self.h5file = destination_folder + separator + self.sample_name        
        
        
        
    
        
        
    def Data_reduction(self):
        #list_folders = [string.replace(' ','').split(sep=',') for string in self.data_folders]
        run_names = [directory.split(sep=separator)[-1] for directory in self.data_folders]        
        list_logfiles = self.log_files.replace(' ','').split(sep=',')
       
        
        if len(run_names) > len(list_logfiles):
            if len(list_logfiles) == 1:
                list_logfiles = np.tile(list_logfiles, len(run_names))
            else:
                raise ValueError('Please insure that logfiles are specified correctly\nEither one for all folders or one for each folder')
            
        for num, directory in enumerate(self.data_folders):
            average_and_write(directory, list_logfiles[num], run_names[num], self.h5file, self.Reduction_parameters)
        
        reduce_data(self.h5file, self.Reduction_parameters)
        
    def produce_standard_plot(self):
        #if self.individual_datasets.checkState():
        #    data_sets = str(self.inp_individual_datasets.text).replace(' ','')
        #    data_sets = data_sets.split(sep=',')
        #    individual_plot_data = prepare_individual_data(self.h5file, data_sets)
            
        if self.merged_plots_selected.checkState():
            plot_data = prepare_merged_data(self.h5file)
            self.plot = PlotWindow(plot_data) # new plot window set up to reviece at dictionary with entry 'path'
            self.plot.Data_reader(plot_data)
            self.plot.Add_plot()
            self.plot.show()
            
            
    def produce_SVD_comps(self):
        self.plot = CompWindow(self.h5file) # new plot window set up to reviece at dictionary with entry 'path'
        self.plot.PlotListUpdate()
        self.plot.show()
        
    def produce_SVD_diffs(self):
        self.trending_diffs_delay =  str(self.inp_delays_diffs.text())
        svd_differentials(self.h5file, self.trending_diffs_delay)
        
    def produce_cov(self):
        self.trending_diffs_delay =  str(self.inp_delays_diffs.text())
        cov_differentials(self.h5file, self.trending_diffs_delay)
    
    def produce_corr(self):
        self.trending_diffs_delay =  str(self.inp_delays_diffs.text())
        corr_differentials(self.h5file, self.trending_diffs_delay)
        
    def produce_holdout(self):
        self.delay_SN = str(self.inp_delays_SN.text())
        hold_out_test(self.h5file, self.delay_SN)
        
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
        #scan_width = int(self.inp_scan_width.text())
        num_points = 800
        
        # non-packed variables
        #self.laser_spot = str(self.inp_laser_spot.text())
        #self.laser_fluence = str(self.inp_laser_fluence.text())        
        #self.sample_conc = str(self.inp_sample_conc.text())        
        self.sample_name = str(self.inp_sample_name.text()) + '.hdf5'
        self.data_folders = str(self.inp_data_folders.text()).replace(' ','').split(sep=',')
        self.log_files = str(self.inp_logfiles.text())
        self.hdf5_append = str(self.inp_append_hdf5.text())
        #self.numb_outliers = str(self.inp_num_outl.text())
        #self.scan_width = str(self.inp_scan_width.text())
        
        exp_variable_names = ['detector_dist', 'detector_bin', 'Xray_energy', 'Xray_position',
                              'sample_thickness', 'solvent_abs', 'norm_Qmin', 'norm_Qmax', 'reference_flag', 
                              'num_outliers', 'num_points'] #'scan_width'
        exp_variables = [detector_dist, detector_bin, Xray_energy, Xray_position, sample_thickness,
                         solvent_abs, norm_Qmin, norm_Qmax, reference_flag, num_outliers,
                         num_points] # scan_width
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