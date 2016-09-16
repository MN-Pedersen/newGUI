# -*- coding: utf-8 -*-
"""

Plot windows 2: plot window for individual data sets

Martin N. Pedersen

2016

"""

from PyQt4.uic import loadUiType
import os 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
 
from PyQt4 import QtCore   
from PyQt4.QtCore import SIGNAL    
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

#%%

ui2_file = 'standard_plot_ind.ui'
# my_path = # used only in the dummy version 
Ui_PlotWindow, QPlotWindow = loadUiType(ui2_file )
# info_dict = {'path': my_path} # used only in the dummy version



class PlotWindow(QPlotWindow, Ui_PlotWindow):
    def __init__(self, individual_plot_data, data_sets):
        super(PlotWindow, self).__init__()
        self.setupUi(self)
        # make a plot
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        #self.axes = self.figure.add_subplot(111)
        self.plot_vl.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas,
                self.plot, coordinates=True)
        self.plot_vl.addWidget(self.toolbar)
        self.replot = False

        self.connect(self.dsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.qdsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.qqdsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.CurvesToPlot,SIGNAL("itemChanged (QListWidgetItem*)"), self.PlotListUpdate)
        self.connect(self.Data_sets,SIGNAL("itemChanged (QListWidgetItem*)"), self.DataSetUpdate)
        self.connect(self.ButtonUpdate,SIGNAL("clicked()"),self.Update)
        self.connect(self.ResetZoom,SIGNAL("clicked()"),self.ZoomReset)
        self.connect(self.Errorbars,SIGNAL("clicked()"), self.ChangeErrorbars)

        # *** Various settings used to configure the settings ***
        #self.my_path = info_dict['path']
        self.Use_errorbars = False
        
        
        # Avoid reading the y and x axis limits on first pass. This is necessary
        # because PlotListUpdate is passed before Add_plot due to the 
        # CurvesToPlot-PlotListUpdate connection above
        self.First_round_check = True
        
        
        
        
    def DataSetUpdate(self):
        use_data_sets = []
        for num in range(self.Data_sets.count()):
            if self.Data_sets.item(num).checkState() == 2:
                use_data_sets.append(data_sets[num])
                

        
        
        
    def Data_reader(self, individual_plot_data):
        self.Q = individual_plot_data[]['Q']
        self.IQ = individual_plot_data[]['IQ']
        self.err = individual_plot_data[]['errors']
        self.file_names = individual_plot_data[]['file_names']
        self.legends = individual_plot_data[]['legends']
            
        for k, item in enumerate(self.file_names):
            self.CurvesToPlot.addItem(item)
            self.CurvesToPlot.item(k).setCheckState(QtCore.Qt.Checked)