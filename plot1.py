# -*- coding: utf-8 -*-
"""

waxsStore: Plot utility for plotting the 

Martin N. Pedersen

2016

"""

#%%

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

ui2_file = 'standard_plot.ui'
# my_path = # used only in the dummy version 
Ui_PlotWindow, QPlotWindow = loadUiType(ui2_file )
# info_dict = {'path': my_path} # used only in the dummy version



class PlotWindow(QPlotWindow, Ui_PlotWindow):
    def __init__(self, plot_data):
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
        
        
    def Add_plot(self):
 #       print 'Add_plot'
        self.figure.clear()
        plt.title('Merged Data Curves')
        plt.grid(b=True, which=u'major', axis=u'both')
        # set axis
        self.axes = self.figure.add_subplot(111)
        x_axis, y_axis = self.SetAxisLabels()
        self.axes.set_xlabel(x_axis)
        self.axes.set_ylabel(y_axis)
        # plot data
        if not self.Use_errorbars:
            # no error bars
            if self.dsq_state == 1:
                for k in range(len(self.legends_plot)): # loop necessary to assign label :(
                    self.axes.plot(self.Q,self.IQ_plot[:,k],label=self.legends[k],color = self.curve_color[k],lw=2)
            elif self.dsq_state == 2:
                for k in range(len(self.legends_plot)): # loop necessary to assign label :(
                    self.axes.plot(self.Q,self.IQ_plot[:,k]*self.Q,label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 3:
                for k in range(len(self.legends_plot)): # loop necessary to assign label :(
                    self.axes.plot(self.Q,self.IQ_plot[:,k]*self.Q**2,label=self.legends[k], color = self.curve_color[k],lw=2)
        else:
            # error bars
            if self.dsq_state == 1:
                for k in range(len(self.legends_plot)): # loop necessary to assign label :(
                    self.axes.errorbar(self.Q,self.IQ_plot[:,k],self.err_plot[:,k],label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 2:
                for k in range(len(self.legends_plot)):
                    self.axes.errorbar(self.Q,self.IQ_plot[:,k]*self.Q,self.err_plot[:,k]*self.Q,label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 3:
                for k in range(len(self.legends_plot)): # loop necessary to assign label :(
                    self.axes.errorbar(self.Q,self.IQ_plot[:,k]*self.Q**2,self.err_plot[:,k]*self.Q**2,label=self.legends[k], color = self.curve_color[k],lw=2)

        # adjust axis'
        self.First_round_check = False # first pass of PlotListUpdate complete
        #self.Axis_round_check += 1
        if self.replot:
#            print 'replot plotting'
            plt.ylim(self.y_range)
            plt.xlim(self.x_range)

        box = self.axes.get_position()
        self.axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        self.axes.legend(loc='upper left', bbox_to_anchor=(1, 1)) # produce legend
        self.canvas.draw()
        
        
    def SetAxisLabels(self):
        # configure axises
        x_axis = 'q, A^{-1}'
        if self.dsq.checkState():
            y_axis = 'dS(q, t), a.u.'
            self.dsq_state = 1
        if  self.qdsq.checkState():
           y_axis = 'q*dS(q, t), a.u.'
           self.dsq_state = 2
        if  self.qqdsq.checkState():
           y_axis = 'q**2*dS(q, t), a.u.'
           self.dsq_state = 3
        return x_axis, y_axis

    def PlotListUpdate(self):
        # print 'reads'
        # empty variables
        IQ_plot = []
        #Q_plot = []
        err_plot = []
        legends_plot = []
        curve_color = [] # sorry UK
        # design colormap - do it here so they are local. This step is fast, so it can be repeated
        num_files = len(self.file_names)
#        print num_files
        colors = [cm.jet(k/float(num_files),1) for k in range(num_files)]
        for num in range(self.CurvesToPlot.count()):
            if self.CurvesToPlot.item(num).checkState() == 2:
               # Q_plot.append(self.Q)
                IQ_plot.append(self.IQ[:,num])
                err_plot.append(self.err[:,num])
                legends_plot.append(self.legends[num])
                curve_color.append(colors[num])
        # define the data
        #self.Q_plot = selnp.array(Q_plot).T
        self.IQ_plot = np.array(IQ_plot).T
        self.err_plot = np.array(err_plot).T
        self.legends_plot = legends_plot
        self.curve_color = curve_color
        # sort the data
#        self.data_sorter()        
#        print  'curvecolor shape'
#        print np.shape(self.curve_color)
#        print 'PlotListUpdate'
        # define the plot settings
        if not self.First_round_check:
            self.replot = True
            self.y_range = self.axes.get_ylim()
            self.x_range = self.axes.get_xlim()
        self.Add_plot()
        
        
    def Update(self):
        self.CurvesToPlot.clear() 
        self.Load_data()
        self.Add_plot()

    def ZoomReset(self):
        self.replot = False
        self.Add_plot()

    def ChangeErrorbars(self):
        if self.Errorbars.checkState() == 2:
            self.Use_errorbars = True
        if self.Errorbars.checkState() == 0:
            self.Use_errorbars = False
        self.y_range = self.axes.get_ylim()
        self.x_range = self.axes.get_xlim()
        self.replot = True
        self.Add_plot()
        
    # Initials stuff = run only once! 
    # *** FIX FIX FIX ***            
    # load the data  
    def Data_reader(self, plot_data):
        self.Q = plot_data['Q']
        self.IQ = plot_data['IQ']
        self.err = plot_data['errors']
        self.file_names = plot_data['file_names']
        self.legends = plot_data['legends']
            
        for k, item in enumerate(self.file_names):
            self.CurvesToPlot.addItem(item)
            self.CurvesToPlot.item(k).setCheckState(QtCore.Qt.Checked)
        
        