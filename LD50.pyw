# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys, os
from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg


progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvasQTAgg):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=8, dpi=100):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_axes([0,0,1,1])
        #self.axes = fig.add_subplot(111)
        self.axes.set_xlim(0,1)
        self.axes.set_ylim(0,1)        
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def compute_initial_figure(self):
        pass




class ParticlePlotCanvas(MyMplCanvas):
    """
    """
    def __init__(self, *args, **kwargs):
        from physics import ChargedParticle, Volume, MeV, cm, amu, q_e, deg
        self.volume = Volume("torso2.png")
        self.particle = ChargedParticle(1*amu, 1*q_e, 150*MeV, 
                                        [0, 60*cm], 0*deg, self.volume)
        self.path = []
        self.dE = [] 
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.axes.set_xlim(0, self.volume.image.shape[1])
        self.axes.set_ylim(0, self.volume.image.shape[0])    
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_figure)

    def compute_initial_figure(self):
        from matplotlib.pyplot import imread
        image = imread("torso2.png")
        self.axes.imshow(image, extent=(0, self.volume.image.shape[1], 0, self.volume.image.shape[0]))
        self.p_line = self.axes.plot([], [], 'bo')[0]
        self.scat = self.axes.scatter([], [], s=[], c='red',
                                      alpha=0.4, linewidth=0)
    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        from physics import MeV, mm
        if self.particle.energy <= 0:
            self.p_line.set_data([], [])
            self.draw()
            self.timer.stop()
            return            
        x, y, dE = self.particle.step(10.*mm) 
        if x <0 or x/mm >self.volume.image.shape[1] or y<0 or y/mm>self.volume.image.shape[0]:
            self.timer.stop()
            return
        if dE/MeV>0.1:
            self.dE.append((dE/MeV)**2/4)   
            self.path.append((x/mm, y/mm))
        self.scat.set_offsets(self.path)
        self.scat._sizes = self.dE #area->radius
        self.p_line.set_data([self.particle.pos_x/mm], [self.particle.pos_y/mm])
        self.draw()

    def clear_figure(self): 
        self.path = []
        self.dE = []
        self.scat.set_offsets(self.path)
        self.scat._sizes = self.dE
        self.draw()
  
        
class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("LD50")

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QHBoxLayout(self.main_widget)
        
        ui_grid = QtGui.QGridLayout()
        ui_grid.addWidget(QtGui.QLabel("Strahlungsart"), 0, 0)
        self.selector = QtGui.QComboBox()
        self.selector.addItem("Proton")
        self.selector.addItem("Alpha")
        self.selector.addItem("Kosmische Strahlung")
        ui_grid.addWidget(self.selector, 0, 1)
        ui_grid.addWidget(QtGui.QLabel("Energy / MeV"), 1, 0)
        self.energy = QtGui.QLineEdit("150")
        ui_grid.addWidget(self.energy)
        
        btn_start = QtGui.QPushButton("Start")
        btn_start.clicked.connect(self.start_run)
        btn_clear = QtGui.QPushButton("Clear")
        btn_clear.clicked.connect(self.clear)
        ui_grid.addWidget(btn_start, 2, 0)
        ui_grid.addWidget(btn_clear, 2, 1)
                
        
        ui_widget = QtGui.QWidget(self.main_widget)
        ui_widget.setLayout(ui_grid)

        #sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.rad_plot = ParticlePlotCanvas(self.main_widget, width=3, height=4, dpi=100)
        l.addWidget(ui_widget)
        #l.addWidget(sc)
        l.addWidget(self.rad_plot)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""LD50
A tool to visualize the effect of radiation on the human body.
"""
)
    def start_run(self):
        self.rad_plot.timer.stop()
        self.particle_generator()
        self.rad_plot.timer.start(10)
    def clear(self):
        self.rad_plot.timer.stop() 
        self.rad_plot.clear_figure()
    def particle_generator(self):
        from physics import ChargedParticle, cos_law, mm
        from physics import MeV, amu, q_e, deg
        from numpy.random import rand
        energy = float(self.energy.text())
        pos = (rand()*1200*2+800)*mm
        pos = rand()*2000*mm
        if pos < 1200*mm:
            direction = cos_law()
            pos_x = 0
            pos_y = pos
        elif pos < (1200+800)*mm:
            direction = cos_law() + 270*deg
            pos_x = pos-1200*mm
            pos_y = 1200*mm
        else:
            direction = cos_law() + 180*deg
            pos_x = 600*mm
            pos_y = pos -2000*mm
        

        if self.selector.currentText()=="Proton":
            self.rad_plot.particle = ChargedParticle(1*amu, 1*q_e, energy*MeV, 
                                        [pos_x, pos_y], direction, self.rad_plot.volume)
        elif self.selector.currentText()=="Alpha":
            self.rad_plot.particle = ChargedParticle(4*amu, 2*q_e, energy*MeV, 
                                        [pos_y, pos_y], direction, self.rad_plot.volume)            

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
#aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
