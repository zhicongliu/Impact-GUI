#!/usr/bin/env python
#This code is to plot the result from ImpactZ
#Zhicong@21/10/2016
#Input : fort.xx
#Output: figures about beam size and emittance
# plots are saved at '/post'

import tkinter as tk
from tkinter import ttk,filedialog
import time,os,sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FormatStrFormatter 
from scipy.stats import gaussian_kde
import numpy as np


_height=300
_width =200

ADVANCED_PLOT_TYPE= {'Centriod location' :1,
                     'Rms size'          :2,
                     'Centriod momentum' :3,
                     'Rms momentum'      :4,
                     'Twiss'             :5,
                     'Emittance'         :6}

class AdvancedPlotControlFrame(tk.Toplevel):
    """Output"""
            
    def __init__(self, master=None, cnf={}, **kw):
        tk.Toplevel.__init__(self, master, cnf, **kw)
        self.title('ImpactZ Plot')
        self.focus_set()  
        """Plot Control"""
        self.frame_plotButton = tk.Frame(self)
        self.frame_plotButton.grid(column=0, row = 0, pady=5 ,padx=10, sticky="we")
        
        self.frame_radio = tk.Frame(self.frame_plotButton)
        self.frame_radio.pack(side='top')
        
        self.plotDirct = tk.IntVar()
        self.plotDirct.set(0)
        self.frame_radio.x = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="X", value=0)
        self.frame_radio.x.pack(side='left')
        self.frame_radio.y = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="Y", value=1)
        self.frame_radio.y.pack(side='left')
        self.frame_radio.z = tk.Radiobutton(self.frame_radio, variable=self.plotDirct,
                                           text="Z", value=2)
        self.frame_radio.z.pack(side='left')
        
        self.plotTypeComx = tk.StringVar(self.frame_plotButton,'Rms size')
        self.plotType = ttk.Combobox(self.frame_plotButton,text=self.plotTypeComx,
                                     width = 15,
                                     values=list(ADVANCED_PLOT_TYPE.keys()))
        self.plotType.pack(side = 'top')
        self.plot = tk.Button(self.frame_plotButton,text='plot',command=self.makePlot)
        self.plot.pack(fill = 'both',expand =1,side = 'top',padx=10)
        
        self.t = ttk.Separator(self, orient=tk.HORIZONTAL).grid(column=0, row = 1, sticky="we")

           
        self.frame2 = tk.Frame(self, height =_height/5, width = _width)
        self.frame2.grid(column=0, row = 2, pady=5 ,padx=10, sticky="nswe")
        
        rowN=0
        
        self.button_overall = tk.Button(self.frame2,text='Overall',
                               command = self.overallPlot)
        self.button_overall.grid(row = rowN, column=0,  pady=5 ,padx=5, columnspan = 2, sticky="nswe")
        rowN+=1
        
        self.button_emitGrowth      = tk.Button(self.frame2,text='EmitGrowth',
                                                command = self.emitGrowthPlot)
        self.button_emitGrowth      .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_Ek              = tk.Button(self.frame2,text='Kinetic Energy',
                                                command = lambda: self.energyPlot(3))
        self.button_Ek              .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_beta            = tk.Button(self.frame2,text='Beta',
                                                command = lambda: self.energyPlot(4))
        self.button_beta            .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_gamma           = tk.Button(self.frame2,text='Gamma',
                                                command = lambda: self.energyPlot(2))
        self.button_gamma           .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_rmax            = tk.Button(self.frame2,text='Rmax',
                                                command = lambda: self.energyPlot(5))
        self.button_rmax            .grid(row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_dw              = tk.Button(self.frame2,text='Absolute phase',
                                                command = lambda: self.energyPlot(1))
        self.button_dw              .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_Temperature         = tk.Button(self.frame2,text='Temperature Plot',
                                                    command = self.makeTemperaturePlot)
        self.button_Temperature         .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_Loss                = tk.Button(self.frame2,text='live Particle #',
                                                    command = self.liveParticlePlot)
        self.button_Loss                .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.t = ttk.Separator(self.frame2, orient=tk.HORIZONTAL).grid(column=0, row = rowN, columnspan=2,sticky="we")        
        rowN+=1
        
        self.max                        = tk.Button(self.frame2,text='Max amplitude',
                                                    command = self.maxPlot)
        self.max                        .grid(row = rowN, column=0,  pady=5 ,padx=5, columnspan=2,sticky="nswe")
        rowN+=1
        
        self.button_3order              = tk.Button(self.frame2,text='3 order parameter',
                                                    command = self.make3orderPlot)
        self.button_3order              .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_4order              = tk.Button(self.frame2,text='4 order parameter',
                                                    command = self.make4orderPlot)
        self.button_4order              .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.t = ttk.Separator(self.frame2, orient=tk.HORIZONTAL).grid(column=0, row = rowN, columnspan=2,sticky="we")        
        rowN+=1

        
        self.button_Particle            = tk.Button(self.frame2,text='Phase Space Plot',
                                                    command = self.makeParticlePlot)
        self.button_Particle            .grid(row = rowN, column=0,  pady=5 ,padx=5, sticky="nswe")
        self.button_ParticleDesity1D    = tk.Button(self.frame2,text='Density1D',
                                                    command = self.ParticleDensityPlot1D)
        self.button_ParticleDesity1D    .grid(row = rowN, column=1,  pady=5 ,padx=5, sticky="nswe")
        rowN+=1
        
        self.button_ParticleDensity     = tk.Button(self.frame2,text='Density2D (by Grid)',
                                                    command = self.ParticleDensityPlot)
        self.button_ParticleDensity     .grid( row = rowN, column=0, pady=5 ,padx=5, sticky="nswe")
        self.button_ParticleDensity2    = tk.Button(self.frame2,text='Density2D (by Ptc)',
                                                    command = self.ParticleDensityPlot2)
        self.button_ParticleDensity2    .grid(row = rowN, column=1, pady=5 ,padx=5, sticky="nswe")
        rowN+=1

    def overallPlot(self):
        print(self.__class__.__name__)

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=OverallFrame(plotWindow)
        l.pack()    
        
    def energyPlot(self,y):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title(sys._getframe().f_back.f_code.co_name)
        
        l=PlotFrame(plotWindow,'fort.18',0,y)
        l.pack()
    
    def emitGrowthPlot(self):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=EmitGrowthFrame(plotWindow)
        l.pack()   
        
    def makeTemperaturePlot(self):
        print((self.plotType))

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=TemperatureFrame(plotWindow)
        l.pack()
        
    def liveParticlePlot(self):
        print(sys._getframe().f_back.f_code.co_name)

        plotWindow = tk.Toplevel(self)
        plotWindow.title(sys._getframe().f_back.f_code.co_name)
        
        l=PlotFrame(plotWindow,'fort.28',0,3)
        l.pack()
        
    def ParticleDensityPlot(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame(plotWindow,fileName)
        l.pack()
        
    def ParticleDensityPlot1D(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame1D(plotWindow,fileName)
        l.pack()
                
    def ParticleDensityPlot2(self):
        print(self.__class__.__name__)
        fileName=filedialog.askopenfilename(parent=self)
        try:
            t=open(fileName)
            t.close()
        except:
            return
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=ParticleDensityFrame2(plotWindow,fileName)
        l.pack()
        
    def makePlot(self):
        print(self.__class__.__name__)
        
        PlotFileName='fort.'+str(self.plotDirct.get()+24)        
        yx=ADVANCED_PLOT_TYPE[self.plotType.get()]
        yl=yx if self.plotDirct.get()!=2 else yx-1

        plotWindow = tk.Toplevel(self)
        plotWindow.title('Plot')
        
        l=PlotFrame(plotWindow,PlotFileName,0,yl)
        l.pack()
        
    def makeParticlePlot(self):
        print(self.__class__.__name__)
        filename = filedialog.askopenfilename(parent=self)
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Phase Space Plot')
        
        l=PhaseSpaceFrame(plotWindow,filename)
        l.pack() 
    def maxPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.27'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('maxPlot')
        
        l=PlotMaxFrame(plotWindow,filename)
        l.pack() 
    def make3orderPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.29'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Cubic root of 3rd moment')
        
        l=PlotHighorderFrame(plotWindow,filename)
        l.pack() 
        
    def make4orderPlot(self):
        print(self.__class__.__name__)
        filename = 'fort.30'
        try:
            t=open(filename)
            t.close()
        except:
            return
        
        plotWindow = tk.Toplevel(self)
        plotWindow.title('Square root, square root of 4th moment')
        
        l=PlotHighorderFrame(plotWindow,filename)
        l.pack() 

class PlotBaseFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.fig = Figure(figsize=(5,5), dpi=100)
        self.subfig = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        

        
class PlotFrame(tk.Frame):
    def __init__(self, parent,PlotFileName,xl,yl):
        tk.Frame.__init__(self, parent)
        LARGE_FONT= ("Verdana", 12)
        label = tk.Label(self, font=LARGE_FONT,
                         text='plot '+PlotFileName+
                         ' use '+str(xl)+':'+str(yl))
        label.pack(pady=10,padx=10)

        try:
            fin = open(PlotFileName,'r')
        except:
            print(( "  ERRPR! Can't open file '" + PlotFileName + "'"))
        
        linesList  = fin.readlines()
        fin .close()
        linesList  = [line.split() for line in linesList ]
        x   = [float(xrt[xl]) for xrt in linesList]
        y   = [float(xrt[yl]) for xrt in linesList]
        
        fig = Figure(figsize=(5,5), dpi=100)
        subfig = fig.add_subplot(111)
        subfig.plot(x,y)
        
        xmajorFormatter = FormatStrFormatter('%2.2e')
        subfig.yaxis.set_major_formatter(xmajorFormatter)
        box = subfig.get_position()
        subfig.set_position([box.x0*1.3, box.y0*1.1, box.width, box.height])
        
        canvas = FigureCanvasTkAgg(fig, self) 
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def quit(self):
        self.destroy()
                
class OverallFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.fig = Figure(figsize=(12,5), dpi=100)
        self.subfig = []
        self.subfig.append(self.fig.add_subplot(221))
        self.subfig.append(self.fig.add_subplot(222))
        self.subfig.append(self.fig.add_subplot(223))
        self.subfig.append(self.fig.add_subplot(224))

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.plot()
    def plot(self):
        picNum = 4
        fileList    = [[]*2]*picNum
        saveName    = []
        labelList   = [[]*2]*picNum
        xdataList   = [[]*2]*picNum
        ydataList   = [[]*2]*picNum
        xyLabelList = [[]*2]*picNum
        
        saveName.append('sizeX')
        fileList[0]     = ['fort.24','fort.27']
        labelList[0]    = ['rms.X','max.X']
        xdataList[0]    = [0,0]
        ydataList[0]    = [2,1]
        xyLabelList[0]  = ['z drection (m)','beam size in X (m)']
        
        saveName.append('sizeY')
        fileList[1]     = ['fort.25','fort.27']
        labelList[1]    = ['rms.Y','max.Y']
        xdataList[1]    = [0,0]
        ydataList[1]    = [2,3]
        xyLabelList[1]  = ['z drection (m)','beam size in Y (m)']
        
        saveName.append('sizeZ')
        fileList[2]     = ['fort.26','fort.27']
        labelList[2]    = ['rms.Z','max.Z']
        xdataList[2]    = [0,0]
        ydataList[2]    = [2,5]
        xyLabelList[2]  = ['z drection (m)','beam size in Z (m)']
        
        saveName.append('emitXY')
        fileList[3]     = ['fort.24','fort.25']
        labelList[3]    = ['emit.nor.X','emit.nor.Y']
        xdataList[3]    = [0,0]
        ydataList[3]    = [6,6]
        xyLabelList[3]  = ['z drection (m)','emittance at X and Y (m*rad)']
        
        lineType = ['r-','b--']


        for i in range(0,picNum):
            for j in range(0,2):
                try:
                    fin = open(fileList[i][j],'r')
                except:
                    print("ERRPR Can't open file ' " + fileList[i][j] + "'")
                    return
                linesList  = fin.readlines()
                fin .close()
                linesList  = [line.split() for line in linesList ]
                xId = xdataList[i][j]
                yId = ydataList[i][j]
                x   = [xrt[xId] for xrt in linesList]
                y   = [xrt[yId] for xrt in linesList]
                self.subfig[i].plot(x, y, lineType[j], linewidth=2, label=labelList[i][j])

            self.subfig[i].set_xlabel(xyLabelList[i][0])
            self.subfig[i].set_ylabel(xyLabelList[i][1])
            box = self.subfig[i].get_position()
            self.subfig[i].set_position([box.x0*1.1, box.y0*1.1, box.width, box.height *0.88])
            xmajorFormatter = FormatStrFormatter('%2.2E')
            self.subfig[i].yaxis.set_major_formatter(xmajorFormatter)  
            self.subfig[i].legend(loc='upper center', bbox_to_anchor=(0.5, 1.21),fancybox=True, shadow=True, ncol=5)

        self.canvas.draw()
        
class EmitGrowthFrame(PlotBaseFrame):
    def __init__(self, parent):
        PlotBaseFrame.__init__(self, parent)
        self.plot()
    def plot(self):        
        fileList        = ['fort.24','fort.25']
        xdataList       = [1,1]
        ydataList       = [7,7]
        xyLabelList     = ['z drection (m)','emit.Avg.growth']
        
        lineType = ['r-','b--']
        
        try:
            fin1 = open(fileList[0],'r')
        except:
            print("  ERRPR! Can't open file '" + fileList[0] + "'")
            return
        try:
            fin2 = open(fileList[1],'r')
        except:
            print("  ERRPR! Can't open file '" + fileList[1] + "'")
            return
        linesList1  = fin1.readlines()
        linesList2  = fin2.readlines()
        fin1 .close()
        fin2 .close()
        linesList1  = [line.split() for line in linesList1 ]
        linesList2  = [line.split() for line in linesList2 ]
        xId = xdataList[0]-1
        yId = ydataList[0]-1
        x   = [float(xrt[xId]) for xrt in linesList1]
        start = (float(linesList1[0][yId]) + float(linesList2[0][yId]))/2
        y   = [(float(linesList1[k][yId]) + float(linesList2[k][yId]))/2 / start -1 for k in range(len(linesList1))]
        
        self.subfig.clear()
        self.subfig.plot(x, y, lineType[0], linewidth=2, label='emit.growth')
        self.subfig.set_xlabel(xyLabelList[0])
        self.subfig.set_ylabel(xyLabelList[1])
        self.subfig.legend()
        
        self.canvas.draw()
        
class TemperatureFrame(PlotBaseFrame):
    def __init__(self, parent):
        PlotBaseFrame.__init__(self, parent)
        self.plot()
    def plot(self):
        arg=['ct','fort.24','fort.25','fort.26']
        labelList= ['X','Y','Z']
        lineType = ['-','--',':']
        col      = ['b','g','r']
        linew    = [2,2,3]
        picNum = len(arg) - 1
        plotPath = './post'
        if os.path.exists(plotPath) == False:
            os.makedirs(plotPath)
            
        self.subfig.clear()
        for i in range(1,picNum+1):
            try:
                fin = open(arg[i],'r')
            except:
                print( "  ERRPR! Can't open file '" + arg[i] + "'")
                return
    
            linesList  = fin.readlines()
            fin .close()
            linesList  = [line.split() for line in linesList ]
            x   = [float(xrt[0]) for xrt in linesList]
            yl=4
            y   = [float(xrt[yl])*float(xrt[yl]) for xrt in linesList]
            self.subfig.plot(x, y, color = col[(i-1)],linestyle=lineType[i-1], linewidth=linew[i-1],label=labelList[i-1])
            
        self.subfig.set_xlabel('T (s)')
        self.subfig.set_ylabel('Temperature')
        self.subfig.legend()
        
        self.canvas.draw()

class PlotHighOrderBaseFrame(tk.Frame):
    ParticleDirec = {'X'    :1,
                     'Px'   :2,
                     'Y'    :3,
                     'Py'   :4,
                     'Z'    :5,
                     'Pz'   :6}
    data = np.array([])
    def __init__(self, parent, PlotFileName):
        tk.Frame.__init__(self, parent)
        try:
            self.data = np.loadtxt(PlotFileName)
        except:
            print(( "  ERROR! Can't open file '" + PlotFileName + "'"))
            return
        
        self.data = np.transpose(self.data)
        self.frame_PlotParticleControl = tk.Frame(self)
        self.frame_PlotParticleControl.pack()
        
        self.label_x    = tk.Label(self.frame_PlotParticleControl, text="Direction:")
        self.label_x.pack(side='left')

        self.ppc1Value  = tk.StringVar(self.frame_PlotParticleControl,'X')
        self.ppc1       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc1Value,
                                       width=3,
                                       values=['X', 'Px', 'Y', 'Py','Z','Pz'])
        self.ppc1.pack(fill = 'both',expand =1,side = 'left')
        
        LARGE_FONT= ("Verdana", 12)
        self.button_ppc=tk.Button(self.frame_PlotParticleControl)
        self.button_ppc["text"] = "Plot"
        self.button_ppc["foreground"] = "blue"
        self.button_ppc["bg"] = "red"
        self.button_ppc["font"] = LARGE_FONT
        self.button_ppc["command"] = self.plot
        self.button_ppc.pack(fill = 'both',expand =1,side = 'left')

        x   = 0
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.subfig = self.fig.add_subplot(111)
        self.subfig.scatter(self.data[x],self.data[y],s=1)
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.4, box.y0, box.width, box.height])

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.plot()
        
class PlotMaxFrame(PlotHighOrderBaseFrame):
    def __init__(self, parent,ifile):    
        PlotHighOrderBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.subfig.clear()
        self.subfig.plot(self.data[0],self.data[y])
    
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        
        self.subfig.set_xlabel('time (secs)')
        if y%2==1:
            self.subfig.set_ylabel('Max '+ self.ppc1.get()+' (m)')
        else:
            self.subfig.set_ylabel('Max '+ self.ppc1.get()+' (MC)')
        self.canvas.draw()
        
        
class PlotHighorderFrame(PlotHighOrderBaseFrame):
    def __init__(self, parent,ifile):    
        PlotHighOrderBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        y   = self.ParticleDirec[self.ppc1.get()]
        
        self.subfig.clear()
        self.subfig.plot(self.data[0],self.data[y])
        
        xmajorFormatter = FormatStrFormatter('%2.2E')
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)

        self.subfig.set_xlabel('time (secs)')
        if y==1 or y ==3:
            self.subfig.set_ylabel(self.ppc1.get()+' (m)')
        elif y==2 or y ==4:
            self.subfig.set_ylabel(self.ppc1.get()+' (rad)')
        elif y==5:
            self.subfig.set_ylabel('phase (degree)')
        elif y==6:
            self.subfig.set_ylabel('Energy deviation (MeV)')
        self.canvas.draw()
    
class PlotParticleBaseFrame(tk.Frame):
    ParticleDirec = {'X'    :0,
                     'Px'   :1,
                     'Y'    :2,
                     'Py'   :3,
                     'Z'    :4,
                     'Pz'   :5}
    data = np.array([])
    def __init__(self, parent, PlotFileName):
        tk.Frame.__init__(self, parent)
        try:
            self.data = np.loadtxt(PlotFileName)
        except:
            print(( "  ERROR! Can't open file '" + PlotFileName + "'"))
            return
        
        self.data = np.transpose(self.data)
        self.frame_PlotParticleControl = tk.Frame(self)
        self.frame_PlotParticleControl.pack()
        
        self.label_x        = tk.Label(self.frame_PlotParticleControl, text="Axi1:")
        self.label_x.pack(side='left')

        self.ppc1Value  = tk.StringVar(self.frame_PlotParticleControl,'X')
        self.ppc1       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc1Value,
                                       width=3,
                                       values=['X', 'Px', 'Y', 'Py','Z','Pz'])
        self.ppc1.pack(fill = 'both',expand =1,side = 'left')
        
        self.label_y        = tk.Label(self.frame_PlotParticleControl, text="Axi2:")
        self.label_y.pack(side='left')
        self.ppc2Value  = tk.StringVar(self.frame_PlotParticleControl,'Y')
        self.ppc2       = ttk.Combobox(self.frame_PlotParticleControl,text=self.ppc2Value,
                                       width=3,
                                       values=['X', 'Px', 'Y', 'Py','Z','Pz'])
        self.ppc2.pack(fill = 'both',expand =1,side = 'left')
        
        LARGE_FONT= ("Verdana", 12)
        self.button_ppc=tk.Button(self.frame_PlotParticleControl)
        self.button_ppc["text"] = "Plot"
        self.button_ppc["foreground"] = "blue"
        self.button_ppc["bg"] = "red"
        self.button_ppc["font"] = LARGE_FONT
        self.button_ppc["command"] = self.plot
        self.button_ppc.pack(fill = 'both',expand =1,side = 'left')

        x   = self.ParticleDirec[self.ppc1.get()]
        y   = self.ParticleDirec[self.ppc2.get()]
        
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.subfig = self.fig.add_subplot(111)
        self.subfig.scatter(self.data[x],self.data[y],s=1)
        
        box = self.subfig.get_position()
        self.subfig.set_position([box.x0*1.4, box.y0, box.width, box.height])

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.plot()
          
class PhaseSpaceFrame(PlotParticleBaseFrame):
    def __init__(self, parent, PlotFileName):
        PlotParticleBaseFrame.__init__(self, parent,PlotFileName)   

    def plot(self):
        x   = self.ParticleDirec[self.ppc1.get()]
        y   = self.ParticleDirec[self.ppc2.get()]
        
        self.subfig.clear()
        self.subfig.scatter(self.data[x],self.data[y],s=1)

        xmajorFormatter = FormatStrFormatter('%2.2e')
        self.subfig.xaxis.set_major_formatter(xmajorFormatter)
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        
        self.canvas.draw()
        
    def quit(self):
        self.destroy()
        

class ParticleDensityFrame(PlotParticleBaseFrame):
    def __init__(self, parent,ifile):    
        PlotParticleBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        x   = self.ParticleDirec[self.ppc1.get()]
        y   = self.ParticleDirec[self.ppc2.get()]
        
        self.subfig.clear()
        self.subfig.hist2d(self.data[x],self.data[y],(200, 200),cmap = 'jet')
        
        xmajorFormatter = FormatStrFormatter('%2.2e')
        self.subfig.xaxis.set_major_formatter(xmajorFormatter)
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        
        self.subfig.set_xlabel(self.ppc1.get())
        self.subfig.set_ylabel(self.ppc2.get())

        self.canvas.draw()
        
class ParticleDensityFrame1D(PlotParticleBaseFrame):
    def __init__(self, parent,ifile):    
        PlotParticleBaseFrame.__init__(self, parent, ifile)
        
    def plot(self):
        self.ppc2.pack_forget()
        self.label_y.pack_forget()
        x1   = self.data[self.ParticleDirec[self.ppc1.get()]]
        
        self.subfig.clear()
        self.subfig.hist(x1,bins=100)

        #xmajorFormatter = FormatStrFormatter('%2.2e')
        #self.subfig.xaxis.set_major_formatter(xmajorFormatter)
        #self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        
        #self.subfig.set_xlabel(self.ppc1.get())
        #self.subfig.set_ylabel(self.ppc2.get())

        self.canvas.draw()
            
class ParticleDensityFrame2(PlotParticleBaseFrame):
    def __init__(self, parent,ifile):    
        PlotParticleBaseFrame.__init__(self, parent, ifile)
        self.plot()
        
    def plot(self):
        x   = self.data[self.ParticleDirec[self.ppc1.get()]]
        y   = self.data[self.ParticleDirec[self.ppc2.get()]]
        
        self.subfig.clear()       
        '''Calculate the point density'''
        xy = np.vstack([x,y])
        z = gaussian_kde(xy)(xy)
    
        '''Sort the points by density, so that the densest points are plotted last'''
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]        
        
        self.subfig.scatter(x, y, c=z, s=10, edgecolor='')        

        xmajorFormatter = FormatStrFormatter('%2.2e')
        self.subfig.xaxis.set_major_formatter(xmajorFormatter)
        self.subfig.yaxis.set_major_formatter(xmajorFormatter)
        self.subfig.set_xlabel(self.ppc1.get())
        self.subfig.set_ylabel(self.ppc2.get())

        self.canvas.draw()        