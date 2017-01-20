# -*- coding: utf-8 -*-
"""

plot 3: plot for visualizing the componets from SVD

Martin N. Pedersen

2016

"""

from PyQt5.uic import loadUiType
import os 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from PyQt5 import QtCore   
from PyQt5.QtCore import pyqtSignal as SIGNAL    
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import gridspec
import numpy as np
import h5py

#%%

ui2_file = 'svd_comp.ui'
Ui_PlotWindow, QPlotWindow = loadUiType(ui2_file )

class CompWindow(QPlotWindow, Ui_PlotWindow):
    def __init__(self, h5file):
        super(CompWindow, self).__init__()
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

        self.dsq.clicked.connect(self.Add_plot)
        self.qdsq.clicked.connect(self.Add_plot)
        self.qqdsq.clicked.connect(self.Add_plot)
        self.CompsToPlot.itemChanged.connect(self.PlotListUpdate)
        self.ResetZoom.clicked.connect(self.ZoomReset)

        # *** Various settings used to configure the settings ***
        self.Use_errorbars = False
        self.h5file = h5file
        self.num_comps = 10
        self.prepare_data()
        
        
        # Avoid reading the y and x axis limits on first pass. This is necessary
        # because PlotListUpdate is passed before Add_plot due to the 
        # CurvesToPlot-PlotListUpdate connection above
        self.First_round_check = True
        
        
    def Add_plot(self):
        self.figure.clear()
        #plt.title('Merged Data Curves')
        #plt.grid(b=True, which=u'major', axis=u'both')
        # set axis
        gs = gridspec.GridSpec(2, 2) 
        self.axes = self.figure.add_subplot(gs[0,:])
        plt.title('Left singular vectors')
        plt.xlabel('Q (1/A)')
        y_axis = self.SetAxisLabels()
        plt.ylabel(y_axis)
        plt.grid(b=True, which=u'major', axis=u'both')
        for num in range(len(self.legends)):
            plt.plot(self.Q, np.tile(-num*2, len(self.Q)), '-k', lw=2)
            
            if self.dsq_state == 1:
                plt.plot(self.Q, self.U_plot[:,num]-num*2, color=self.plot_colours[num], label=self.legends[num],lw=2)
            elif self.dsq_state == 2:
                plt.plot(self.Q, self.U_plot[:,num]*self.Q-num*2, color=self.plot_colours[num], label=self.legends[num],lw=2)
            elif self.dsq_state == 3:
                 plt.plot(self.Q, self.U_plot[:,num]*self.Q**2-num*2, color=self.plot_colours[num], label=self.legends[num],lw=2)
            
        plotbox = self.axes.get_position()
        self.axes.set_position([plotbox.x0, plotbox.y0, plotbox.width * 0.97, plotbox.height])
        self.axes.legend(loc='upper left', bbox_to_anchor=(1, 1.01))

            
            
            
        self.axes = self.figure.add_subplot(gs[1,0])
        plt.title('Right singular vectors')
        plt.xlabel('Delay (seconds)')
        plt.ylabel('Weigth')
        plt.grid(b=True, which=u'major', axis=u'both')
        for num in range(len(self.legends)):
            plt.semilogx(self.time_seconds, np.tile(-num*2, len(self.time_seconds)), '-k', lw=2)
            plt.semilogx(self.time_seconds, self.V_plot[:,num]-num*2, color=self.plot_colours[num], lw=2)
        plotbox = self.axes.get_position()
        self.axes.set_position([plotbox.x0, plotbox.y0, plotbox.width*0.95, plotbox.height*0.95])
            
        self.axes = self.figure.add_subplot(gs[1,1])
        plt.title('Singular values')
        plt.xlabel('Component')
        plt.ylabel('Singular value')
        plt.grid(b=True, which=u'major', axis=u'both')
        num_frames = np.linspace(1,len(self.V),len(self.V))
        plt.loglog(num_frames, self.s,'o')
        count = 0
        for num in self.comp_num:
            plt.loglog(num_frames[num], self.s[num], 'o', color=self.plot_colours[count])
            count += 1
        
        plotbox = self.axes.get_position()
        self.axes.set_position([plotbox.x0, plotbox.y0, plotbox.width*0.95, plotbox.height*0.95])
        
        self.canvas.draw()
        
        
    def PlotListUpdate(self):
        colours = [cm.brg(k/float(self.num_comps),1) for k in range(self.num_comps)]
        
        Uvectors = []
        Vvectors = []
        legends = []
        plot_colours = []
        comp_num = []
        
        for num in range(self.CompsToPlot.count()):
            if self.CompsToPlot.item(num).checkState() == 2:
                Uvectors.append(self.U[:,num])
                Vvectors.append(self.V[num,:])
                plot_colours.append(colours[num])
                legends.append('Comp. {num}'.format(num=num+1))
                comp_num.append(num)
        self.U_plot = np.array(Uvectors).T
        self.V_plot = np.array(Vvectors).T
        self.legends = legends
        self.plot_colours = plot_colours
        self.comp_num = comp_num
        self.Add_plot()

        #if not self.First_round_check:
        #    self.replot = True
        #    self.y_range = self.axes.get_ylim()
        #    self.x_range = self.axes.get_xlim()
               
                

    def prepare_data(self):    
        with h5py.File(self.h5file) as f:
            self.Q = f['Global/Data_set/IQ_curves'][:,0]
            IQ = f['Global/Data_set/IQ_curves'][:,1:]
            time_seconds =  f['Global/Merged/Time_seconds'][:]
            negative_idx = time_seconds < 0
            self.time_seconds = time_seconds[~negative_idx]            
            
            
            self.U, self.s, self.V = np.linalg.svd(IQ[:,~negative_idx])


        
        for num in range(self.num_comps):
            item = 'Component {num}'.format(num=num+1)
            self.CompsToPlot.addItem(item)
            if num <= 2:
                self.CompsToPlot.item(num).setCheckState(QtCore.Qt.Checked)
            else:
                self.CompsToPlot.item(num).setCheckState(QtCore.Qt.Unchecked)

    def ZoomReset(self):
        self.replot = False
        self.Add_plot()
        
    def SetAxisLabels(self):
        # configure axises
        if self.dsq.checkState():
            y_axis = 'dS(q, t), a.u.'
            self.dsq_state = 1
        if  self.qdsq.checkState():
           y_axis = 'q*dS(q, t), a.u.'
           self.dsq_state = 2
        if  self.qqdsq.checkState():
           y_axis = 'q**2*dS(q, t), a.u.'
           self.dsq_state = 3
        return y_axis
        
        
            
