# -*- coding: utf-8 -*-
"""
Created on Thu Jan 07 16:22:47 2016

@author: MPEDERSE
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
import re

#%%

ui2_file = 'replot_three.ui'
# my_path = # used only in the dummy version 
Ui_PlotWindow, QPlotWindow = loadUiType(ui2_file )
# info_dict = {'path': my_path} # used only in the dummy version



class PlotWindow(QPlotWindow, Ui_PlotWindow):
    def __init__(self, info_dict):
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
            
        # make the connections
        self.connect(self.dsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.qdsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.qqdsq,SIGNAL("clicked()"),self.Add_plot)
        self.connect(self.CurvesToPlot,SIGNAL("itemChanged (QListWidgetItem*)"), self.PlotListUpdate)
        self.connect(self.ButtonUpdate,SIGNAL("clicked()"),self.Update)
        self.connect(self.ResetZoom,SIGNAL("clicked()"),self.ZoomReset)
        self.connect(self.Errorbars,SIGNAL("clicked()"), self.ChangeErrorbars)
        
        # *** Various settings used to configure the settings ***
        self.my_path = info_dict['path']
        self.Use_errorbars = False
        
        # Avoid reading the y and x axis limits on first pass. This is necessary
        # because PlotListUpdate is passed before Add_plot due to the 
        # CurvesToPlot-PlotListUpdate connection above
        self.First_round_check = True
        # and for changes in dsq/qdsq - does not work
        #self.Axis_round_check = 0
    
    # plot the data
    def Add_plot(self):
 #       print 'Add_plot'
        self.figure.clear()
        plt.title(self.my_path)
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
                for k in range(len(self.legends)): # loop necessary to assign label :(
                    self.axes.plot(self.Q_plot[:,k],self.IQ_plot[:,k],label=self.legends[k],color = self.curve_color[k],lw=2)
            elif self.dsq_state == 2:
                for k in range(len(self.legends)): # loop necessary to assign label :(
                    self.axes.plot(self.Q_plot[:,k],self.IQ_plot[:,k]*self.Q_plot[:,k],label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 3:
                for k in range(len(self.legends)): # loop necessary to assign label :(
                    self.axes.plot(self.Q_plot[:,k],self.IQ_plot[:,k]*self.Q_plot[:,k]**2,label=self.legends[k], color = self.curve_color[k],lw=2)
        else:
            # error bars
            if self.dsq_state == 1:
                for k in range(len(self.legends)): # loop necessary to assign label :(
                    self.axes.errorbar(self.Q_plot[:,k],self.IQ_plot[:,k],self.std_plot[:,k],label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 2:
                for k in range(len(self.legends)):
                    self.axes.errorbar(self.Q_plot[:,k],self.IQ_plot[:,k]*self.Q_plot[:,k],self.std_plot[:,k]*self.Q_plot[:,k],label=self.legends[k], color = self.curve_color[k],lw=2)
            elif self.dsq_state == 3:
                for k in range(len(self.legends)): # loop necessary to assign label :(
                    self.axes.errorbar(self.Q_plot[:,k],self.IQ_plot[:,k]*self.Q_plot[:,k]**2,self.std_plot[:,k]*self.Q_plot[:,k]**2,label=self.legends[k], color = self.curve_color[k],lw=2)

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
#        print 'SetAxisLabels'
#        # define the plot settings
#        if self.Axis_round_check > self.CurvesToPlot.count(): 
#            print 'Axis_round_check is True!'
#            self.y_range = self.axes.get_ylim()
#           self.x_range = self.axes.get_xlim()
#            self.replot = True  
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

        
    # update plot
    def PlotListUpdate(self):
        # print 'reads'
        # empty variables
        IQ_plot = []
        Q_plot = []
        std_plot = []
        legends = []
        curve_color = [] # sorry UK
        # design colormap - do it here so they are local. This step is fast, so it can be repeated
        num_files = len(self.file_names)
#        print num_files
        colors = [cm.jet(k/float(num_files),1) for k in range(num_files)]
        for k in range(self.CurvesToPlot.count()):
            if self.CurvesToPlot.item(k).checkState() == 2:
                Q_plot.append(self.Q[k,:])
                IQ_plot.append(self.IQ[k,:])
                std_plot.append(self.std[k,:])
                legend_string = self.file_names[k] + ' ' + self.accepted[k]
                legends.append(legend_string)
                curve_color.append(colors[k])
        # define the data
        self.Q_plot = np.array(Q_plot).T
        self.IQ_plot = np.array(IQ_plot).T
        self.std_plot = np.array(std_plot).T
        self.legends = legends
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


    # buttons
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
    def Load_data(self):
        self.Q, self.IQ, self.std, self.accepted, self.file_names = self.Data_reader()
        self.data_sorter()
        for k, item in enumerate(self.file_names):
            self.CurvesToPlot.addItem(item)
            self.CurvesToPlot.item(k).setCheckState(QtCore.Qt.Checked)
 #       print self.CurvesToPlot.count()
                
    # load the data  
    def Data_reader(self):
        Q = []
        IQ = []
        std = []
        accepted = []
        file_names = []
        files = os.listdir(self.my_path)
        for f in files:
            if f.startswith('diff_av'):
                data = np.genfromtxt(self.my_path+'/'+f,comments='#')
                Q.append(data[:,0])
                IQ.append(data[:,1])
                std.append(data[:,2])
                file_names.append(str(f[8:-4]))
                # logic to get the string formatted
                with open(self.my_path+'/'+f) as read_file:
                    first_line = read_file.readline()
                    Num_accepted = re.search('(?<= = )\d*/\d*',first_line)
                    accepted.append(Num_accepted.group(0))
        return np.array(Q), np.array(IQ), np.array(std), accepted, file_names

    def data_sorter(self):
        time_units = ['ps','ns','us','ms']
        time_conversions = [1e-12,1e-9,1e-6,1e-3]
        time_seconds = np.zeros(np.shape(self.file_names))
        for idx1, file_str in enumerate(self.file_names):
            if file_str.split()[0] == 'off': # slow but readable. 
                delay_number = '1e3ms'
            else:
                delay_number = file_str.split()[0]
            for idx2, unit in enumerate(time_units):
#                print delay_number
#                print type(delay_number)
                if delay_number.endswith(unit):
                    delay_number_float = float(re.findall("-?\d+\.?\d*",delay_number)[0])
                    time_seconds[idx1] = delay_number_float*time_conversions[idx2]
                    break
                    
                
        # sort the arrays
        index_array = np.argsort(time_seconds)
        self.file_names = np.array(self.file_names)[index_array]
        self.accepted = np.array(self.accepted)[index_array]
        self.Q = self.Q[index_array,:] 
        self.IQ = self.IQ[index_array,:]
        self.std = self.std[index_array,:]

        

 
if __name__ == '__main__':
    import sys, os
    from PyQt4 import QtGui
    import numpy as np
    app = QtGui.QApplication(sys.argv)
#    main = PlotWindow(info_dict)
#    
#
#    main.Load_data()
#    main.Add_plot()
#    main.show()
    sys.exit(app.exec_())
    
# !!! check code not use

#        print 'the shape of std_plot is:'
#        print np.shape(self.std_plot)
#        print 'the shape of IQ_plot is:'
#        print np.shape(self.IQ_plot)    
