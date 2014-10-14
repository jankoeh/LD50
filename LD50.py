#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

class ParticleCanvas(QtGui.QGraphicsView):
    def __init__(self, parent=None, max_width=400, max_height=600):
        """
        QGraphicsView that will show an image scaled to the current widget size
        using events
        """
        super(ParticleCanvas, self).__init__(parent)
        self.max_width = max_width
        self.max_height = max_height
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), \
                               self.update_figure)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        from config import WORLD
        x0, y0, x1, y1 = WORLD.bbox
        self.s2px = min([self.max_width/(x1-x0), self.max_height/(y1-y0)])
        self.create_scene()
        
        self.particles = []
        self.p_dots = []
        self.dmg_dots = []
        self.p_pen = QtGui.QPen(QtGui.QColor(0,0,255,0))
        self.p_brush = QtGui.QBrush(QtGui.QColor(0,0,255))
        self.dmg_pen = QtGui.QPen(QtGui.QColor(255,0,0,0))
        self.dmg_brush = QtGui.QBrush(QtGui.QColor(255,0,0,100))

    def create_scene(self):
        from config import WORLD
        scene = QtGui.QGraphicsScene()
        for fn_image, bbox in WORLD.get_image_info():
            image = QtGui.QPixmap(fn_image)
            x0, y0, x1, y1 = bbox
            image = image.scaled((x1-x0)*self.s2px, (y1-y0)*self.s2px)
            s_image = scene.addPixmap(image)
            y_offset = (WORLD.bbox[3]-y1)*self.s2px
            s_image.setOffset(x0*self.s2px,y_offset)
        self.setScene(scene)

    def world_to_canvas(self, pos_x, pos_y):
        """ 
        Transforms world coordninates to image based coordinates
        """
        from config import WORLD
        x0, y0, x1, y1 = WORLD.bbox
        return (pos_x-x0)*self.s2px, (y1-pos_y)*self.s2px
        
    def add_particle(self, particle):
        self.particles.append(particle)
        pos_x, pos_y = self.world_to_canvas(particle.pos_x, particle.pos_y)
        dot = self.scene().addEllipse(pos_x-5, pos_y-5, 10, 10, 
                                      self.p_pen, self.p_brush)
        self.p_dots.append(dot)
        
    def update_figure(self):
        from config import WORLD
        from src.physics import MeV, eV
        ds = (WORLD.bbox[2]-WORLD.bbox[0])/100.
        for particle, dot in zip(self.particles, self.p_dots):
            pos, dE, dl = particle.step(ds)
            pos_x, pos_y = self.world_to_canvas(*pos.mean(axis=0))
            dE = sum(dE)
            if dE/MeV > 0.001:
                radius = (dE/MeV*self.size)/100.
                dmg = self.scene().addEllipse(pos_x-radius, pos_y-radius, 
                                              radius*2, radius*2, 
                                              self.dmg_pen, self.dmg_brush)
                self.dmg_dots.append(dmg)
            dot.setRect(pos_x-5, pos_y-5, 10, 10)
            if particle.energy <= 1*eV or \
               not WORLD.is_in_bbox(particle.pos_x, particle.pos_y):
                self.particles.remove(particle)
                self.p_dots.remove(dot)
                self.scene().removeItem(dot)
        if len(self.particles) == 0:
            self.timer.stop()
            
    def clear(self):
        self.particles = []
        for dot in self.p_dots:
            self.scene().removeItem(dot)
        self.p_dots = []
        for dot in self.dmg_dots:
            self.scene().removeItem(dot)
        self.dmg_dots = []
            


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
        from src.particles import TABLE as p_tbl
        self.selector.addItems(p_tbl.keys())
        
        ui_grid.addWidget(self.selector, 0, 1)
        ui_grid.addWidget(QtGui.QLabel("Energie / MeV"), 1, 0)
        self.energy = QtGui.QLineEdit("100")
        ui_grid.addWidget(self.energy, 1, 1)

        ui_grid.addWidget(QtGui.QLabel("Einfallsrichtung:"), 2, 0)
        self.sel_dir = QtGui.QComboBox()
        from src.guns import TABLE as g_tbl
        self.sel_dir.addItems(g_tbl.keys())
        ui_grid.addWidget(self.sel_dir, 2, 1)

        ui_grid.addWidget(QtGui.QLabel(u"Größe Darstellung:"), 7, 0)
        self.b_size = QtGui.QSpinBox()
        self.b_size.setMinimum(1)
        self.b_size.setMaximum(1000)
        self.b_size.setValue(100)
        ui_grid.addWidget(self.b_size, 7, 1)

        btn_start = QtGui.QPushButton("Start")
        btn_start.clicked.connect(self.start_run)
        btn_clear = QtGui.QPushButton(u"Zurücksetzen")
        btn_clear.clicked.connect(self.clear)
        ui_grid.addWidget(btn_start, 8, 0)
        ui_grid.addWidget(btn_clear, 8, 1)


        ui_widget = QtGui.QWidget(self.main_widget)
        ui_widget.setLayout(ui_grid)


        self.rad_plot = ParticleCanvas(self.main_widget)
        l.addWidget(ui_widget)
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
        self.particle_generator()
        self.rad_plot.timer.start(20)

    def clear(self):
        self.rad_plot.timer.stop()
        self.rad_plot.clear()

    def particle_generator(self):
        from src.physics import MeV
        from config import WORLD

        self.rad_plot.size = float(self.b_size.text())
        energy = float(self.energy.text())
        from src.guns import TABLE as g_tbl
        gun = str(self.sel_dir.currentText())
        pos, dir = g_tbl[gun](WORLD.bbox)

        from src.particles import TABLE as p_tbl
        particle = str(self.selector.currentText())
        self.rad_plot.add_particle(p_tbl[particle](energy*MeV, pos, dir))


qApp = QtGui.QApplication(sys.argv)
aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
