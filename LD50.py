# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg



class MyMplCanvas(FigureCanvasQTAgg):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=8, dpi=100):
        from matplotlib.figure import Figure
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_axes([0, 0, 1, 1])
        self.axes.set_xlim(0, 1)
        self.axes.set_ylim(0, 1)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.compute_initial_figure()

        FigureCanvasQTAgg.__init__(self, fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def compute_initial_figure(self):
        pass

    def clear_figure(self):
        pass


class ParticlePlotCanvas(MyMplCanvas):
    """
    """
    def __init__(self, *args, **kwargs):
        from physics import ChargedParticle, MeV, cm, amu, q_e, deg, WORLD
        self.particle = ChargedParticle(1*amu, 1*q_e, 150*MeV,
                                               [0, 60*cm], 0*deg)
        self.path = []
        self.dE = []
        self.show_dose_equivalent = False
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.axes.set_xlim(0, WORLD.image.shape[1])
        self.axes.set_ylim(0, WORLD.image.shape[0])
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), \
                               self.update_figure)
        self.size = 30

    def compute_initial_figure(self):
        from matplotlib.pyplot import imread
        from physics import WORLD
        image = imread("torso2.png")
        self.axes.imshow(image, extent=(0, WORLD.image.shape[1],\
                                        0, WORLD.image.shape[0]))
        self.p_line = self.axes.plot([], [], 'bo')[0]
        self.scat = self.axes.scatter([], [], s=[], c='red',
                                      alpha=0.4, linewidth=0)
    def update_figure(self):
        from physics import MeV, eV, mm, WORLD
        ds = 10*mm
        pos, dE, dl = self.particle.step(ds)
        pos  = pos.mean(axis=0)
        if self.show_dose_equivalent:
                from physics import quality_factor
                dE = sum([quality_factor(i/dl)*i for i in dE])
        else:
            dE = sum(dE)
        if dE/MeV > 0.001:    
            self.dE.append((dE/MeV*self.size)**2/1000.) #area->radius
            self.path.append(pos/mm)
        self.scat.set_offsets(self.path)
        self.scat._sizes = self.dE
        self.p_line.set_data([self.particle.pos_x/mm], [self.particle.pos_y/mm])
        self.draw()
        if self.particle.energy <= 1*eV or\
           pos[0] < 0 or pos[0]/mm >WORLD.image.shape[1] or\
           pos[1] < 0 or pos[1]/mm > WORLD.image.shape[0]:
            self.p_line.set_data([], [])
            self.draw()
            self.timer.stop()

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
        ui_grid.addWidget(QtGui.QLabel("Strahlungsart:"), 0, 0)
        self.selector = QtGui.QComboBox()
        self.selector.addItem("Proton")
        self.selector.addItem("Alpha")
        self.selector.addItem("Kohlenstoff")
        self.selector.addItem("Elektron")
        self.selector.addItem("Muon")
        self.selector.addItem("Neutron")
        self.selector.addItem("Gamma/X-Ray")
        
        ui_grid.addWidget(self.selector, 0, 1)
        ui_grid.addWidget(QtGui.QLabel("Energie / MeV"), 1, 0)
        self.energy = QtGui.QLineEdit("50")
        ui_grid.addWidget(self.energy, 1, 1)

        ui_grid.addWidget(QtGui.QLabel("Einfallsrichtung:"), 2, 0)
        self.sel_dir = QtGui.QComboBox()
        self.sel_dir.addItems(['Isotrop', 'Strahl', u"Höhenstrahlung"])
        ui_grid.addWidget(self.sel_dir, 2, 1)

        ui_grid.addWidget(QtGui.QLabel("Darstellung in:"), 5, 0)
        self.b_gray = QtGui.QRadioButton("Gray (Dosis)")
        self.b_gray.setChecked(True)
        self.b_sievert = QtGui.QRadioButton(u"Sievert (Äquivalentdosis)")
        ui_grid.addWidget(self.b_gray, 5, 1)
        ui_grid.addWidget(self.b_sievert, 6, 1)


        ui_grid.addWidget(QtGui.QLabel(u"Größe Darstellung:"), 7, 0)
        self.b_size = QtGui.QSpinBox()
        self.b_size.setMinimum(1)
        self.b_size.setMaximum(1000)
        self.b_size.setValue(15)
        ui_grid.addWidget(self.b_size, 7, 1)

        btn_start = QtGui.QPushButton("Start")
        btn_start.clicked.connect(self.start_run)
        btn_clear = QtGui.QPushButton(u"Zurücksetzen")
        btn_clear.clicked.connect(self.clear)
        ui_grid.addWidget(btn_start, 8, 0)
        ui_grid.addWidget(btn_clear, 8, 1)


        ui_widget = QtGui.QWidget(self.main_widget)
        ui_widget.setLayout(ui_grid)


        self.rad_plot = ParticlePlotCanvas(self.main_widget, width=3,\
                                           height=4, dpi=100)
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
u"""LD50
Ein Tool zur Visualisierung von Strahlenschäden .
"""
)
    def increase_dose(self, dose):
        """
        Increase dose on the label
        """
        self.lbl_dose.setText( float(self.lbl_dose.text()) + dose)

        
    def reset_dose_lbl(self):
        """
        Resets the dose label to 0
        """
        self.lbl_dose.setText('0')

 
    def start_run(self):
        #for i in xrange(self.b_shots.value()):
        self.rad_plot.timer.stop()
        self.particle_generator()
        self.rad_plot.timer.start(20)

    def clear(self):
        self.rad_plot.timer.stop()
        self.rad_plot.clear_figure()

    def particle_generator(self):
        from physics import ChargedParticle, cos_law, mm
        from physics import MeV, amu, q_e, deg
        from numpy.random import rand

        self.rad_plot.size = float(self.b_size.text())
        energy = float(self.energy.text())
        if self.sel_dir.currentText() == "Isotrop":
            pos = (rand()*1200*2+800)*mm
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
                pos_x = 800*mm
                pos_y = pos -2000*mm
        elif self.sel_dir.currentText() == "Strahl":
            direction = 0*deg
            pos_x = 0
            pos_y = 550*mm+rand()*100*mm
        elif self.sel_dir.currentText() == u"Höhenstrahlung":
            from physics import cos_square
            direction = cos_square()+270*deg            
            pos_x = rand()*800*mm
            pos_y = 1200*mm            

        if self.selector.currentText() == "Proton":
            self.rad_plot.particle = ChargedParticle(1*amu, 1*q_e, energy*MeV,
                                        [pos_x, pos_y], direction)
        elif self.selector.currentText() == "Alpha":
            self.rad_plot.particle = ChargedParticle(4*amu, 2*q_e, energy*MeV,
                                        [pos_x, pos_y], direction)
        elif self.selector.currentText() == "Kohlenstoff":
            self.rad_plot.particle = ChargedParticle(6*amu, 12*q_e, energy*MeV,
                                        [pos_x, pos_y], direction)                                        
        elif self.selector.currentText() == "Elektron":
            from physics import m_e
            self.rad_plot.particle = ChargedParticle(m_e, q_e, energy*MeV,
                                        [pos_x, pos_y], direction)
        elif self.selector.currentText() == "Muon":
            from physics import m_muon
            self.rad_plot.particle = ChargedParticle(m_muon, q_e, energy*MeV,
                                        [pos_x, pos_y], direction)
        elif self.selector.currentText() == "Neutron":
            from physics import Neutron
            self.rad_plot.particle = Neutron(amu, 0, energy*MeV,
                                        [pos_x, pos_y], direction)
            self.b_gray.setChecked(False)
        elif self.selector.currentText() == "Gamma/X-Ray":
            from physics import Gamma
            self.rad_plot.particle = Gamma(amu, 0, energy*MeV,
                                        [pos_x, pos_y], direction)
            self.b_gray.setChecked(False)
        self.rad_plot.show_dose_equivalent = self.b_sievert.isChecked()

qApp = QtGui.QApplication(sys.argv)
aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
