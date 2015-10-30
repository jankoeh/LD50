# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 14:37:49 2014

@author: koehler
"""
from __future__ import unicode_literals
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
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.world = None
        self.p_dots = []
        self.dmg_dots = []
        self.p_pen = QtGui.QPen(QtGui.QColor(0,0,255,0))
        self.p_brush = QtGui.QBrush(QtGui.QColor(0,0,255))
        self.dmg_pen = QtGui.QPen(QtGui.QColor(255,0,0,0))
        self.dmg_brush = QtGui.QBrush(QtGui.QColor(255,0,0,100))

    def set_world(self, world):
        self.world = world
        x0, y0, x1, y1 = self.world.bbox
        self.s2px = min([self.max_width/(x1-x0), self.max_height/(y1-y0)])
        self.create_scene()
        
    def create_scene(self):
        scene = QtGui.QGraphicsScene()
        for fn_image, bbox in self.world.get_image_info():
            image = QtGui.QPixmap(fn_image)
            x0, y0, x1, y1 = bbox
            image = image.scaled((x1-x0)*self.s2px, (y1-y0)*self.s2px)
            s_image = scene.addPixmap(image)
            y_offset = (self.world.bbox[3]-y1)*self.s2px
            s_image.setOffset(x0*self.s2px,y_offset)
        self.setScene(scene)

    def world_to_canvas(self, pos_x, pos_y):
        """ 
        Transforms world coordninates to image based coordinates
        """
        x0, y0, x1, y1 = self.world.bbox
        return (pos_x-x0)*self.s2px, (y1-pos_y)*self.s2px
        
    def add_particle(self, particle):
        pos_x, pos_y = self.world_to_canvas(particle.pos_x, particle.pos_y)
        dot = self.scene().addEllipse(pos_x-5, pos_y-5, 10, 10, 
                                      self.p_pen, self.p_brush)
        self.p_dots.append(dot)
        
    def draw_particles(self, particles):
        for particle, dot in zip(particles, self.p_dots):
            px_x, px_y = self.world_to_canvas(particle.pos_x, particle.pos_y)
            dot.setRect(px_x-5, px_y-5, 10, 10)
            
    def draw_edep(self, pos_edep):
        from src.physics import MeV
        for pos_x, pos_y, dE in pos_edep:
            px_x, px_y = self.world_to_canvas(pos_x, pos_y)
            radius = (dE/MeV*self.size)/100.
            dmg = self.scene().addEllipse(px_x-radius, px_y-radius, 
                                          radius*2, radius*2, 
                                          self.dmg_pen, self.dmg_brush)
            self.dmg_dots.append(dmg)

            
    def clear(self):
        for dot in self.p_dots:
            self.scene().removeItem(dot)
        self.p_dots = []
        for dot in self.dmg_dots:
            self.scene().removeItem(dot)
        self.dmg_dots = []


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self, run_manager):
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


        ui_grid = QtGui.QGridLayout()
        ui_grid.addWidget(QtGui.QLabel("Strahlungsart:"), 0, 0)
        self.selector = QtGui.QComboBox()
        from src.particles import TABLE as p_tbl
        self.selector.addItems(p_tbl.keys())
        self.selector.currentIndexChanged.connect(self.set_rad_setting)
        
        ui_grid.addWidget(self.selector, 0, 1)
        ui_grid.addWidget(QtGui.QLabel("Energie / MeV:"), 1, 0)
        self.energy = QtGui.QLineEdit("100")
        ui_grid.addWidget(self.energy, 1, 1)

        ui_grid.addWidget(QtGui.QLabel("Einfallsrichtung:"), 2, 0)
        self.sel_dir = QtGui.QComboBox()
        from src.guns import TABLE as g_tbl
        self.sel_dir.addItems(g_tbl.keys())
        ui_grid.addWidget(self.sel_dir, 2, 1)
        ui_grid.addWidget(QtGui.QLabel(u"Schadensskalierung:"), 3, 0)
        self.b_size = QtGui.QSpinBox()
        self.b_size.setMinimum(1)
        self.b_size.setMaximum(5000)
        self.b_size.setValue(100)
        ui_grid.addWidget(self.b_size, 3, 1)
        ui_grid.setRowMinimumHeight(4, 20)

        btn_start = QtGui.QPushButton("Start")
        btn_start.clicked.connect(self.start_run)
        btn_clear = QtGui.QPushButton(u"Zurücksetzen")
        btn_clear.clicked.connect(self.clear)
        ui_grid.addWidget(btn_start, 8, 0)
        ui_grid.addWidget(btn_clear, 8, 1)

        ui_widget = QtGui.QWidget(self.main_widget)
        ui_widget.setLayout(ui_grid)

        left_side = QtGui.QVBoxLayout()
        left_side.addWidget(ui_widget)
        left_side.addSpacing(30)
        energy_tbl = QtGui.QTableWidget()
        left_side.addWidget(energy_tbl)
        left_widget = QtGui.QWidget(self.main_widget)
        left_widget.setLayout(left_side)
        
        self.rad_plot = ParticleCanvas(self.main_widget)
        l = QtGui.QHBoxLayout(self.main_widget)
        l.addWidget(left_widget)#ui_widget)
        l.addWidget(self.rad_plot)
        self.main_widget.setLayout(l)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.run_manager = run_manager
        run_manager.set_energy_tbl(energy_tbl)
        run_manager.set_canvas(self.rad_plot)
        self.set_rad_setting()

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
 
    def start_run(self):
        self.particle_generator()
        self.run_manager.timer.start(20)

    def clear(self):
        self.run_manager.clear()

    def particle_generator(self):
        from src.physics import MeV
        self.rad_plot.size = float(self.b_size.text())
        energy = self.energy.text().replace(',', '.')
        if len(energy.split('-')) == 2:
            from numpy.random import rand
            e1 = float(energy.split('-')[0])
            e2 = float(energy.split('-')[1])
            energy = e1*(e2/e1)**rand() #-1 power law
        else:
            energy = float(self.energy.text())
        from src.guns import TABLE as g_tbl
        gun = unicode(self.sel_dir.currentText())
        pos, dir = g_tbl[gun](self.run_manager.world.bbox)

        from src.particles import TABLE as p_tbl
        particle = str(self.selector.currentText())
        self.run_manager.add_particle(p_tbl[particle](energy*MeV, pos, dir))

    def set_rad_setting(self):
        if str(self.selector.currentText()) == 'kosmisches Muon':
            self.b_size.setValue(1000)
            self.energy.setText("1000-10000")
            self.sel_dir.setCurrentIndex(self.sel_dir.findText(u"Höhenstrahlung"))
        elif str(self.selector.currentText()) == 'Gammazerfall':
            self.b_size.setValue(1000)
            self.energy.setText("0.1-3")
            self.sel_dir.setCurrentIndex(self.sel_dir.findText("Isotrop"))
        elif str(self.selector.currentText()) == 'Alphazerfall':
            self.b_size.setValue(100)
            self.energy.setText("1-6")
            self.sel_dir.setCurrentIndex(self.sel_dir.findText("Isotrop"))
        elif str(self.selector.currentText()) == 'X-Ray':
            self.b_size.setValue(4000)
            self.energy.setText("0.01-0.25")
            self.sel_dir.setCurrentIndex(self.sel_dir.findText("Isotrop"))

def start_gui(run_manager):
    """
    Starts the Qt gui
    """
    import sys
    from PyQt4 import QtGui
    qApp = QtGui.QApplication(sys.argv)
    aw = ApplicationWindow(run_manager)
    aw.show()
    sys.exit(qApp.exec_())