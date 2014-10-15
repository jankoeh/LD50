# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 13:52:34 2014

@author: koehler
"""

class RunManager():
    def __init__(self, world):
        self.world = world
        from PyQt4 import QtCore
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), \
                               self.step)        
        self.canvas = None
        self.particles = []
        self.energy_tbl = None
        self.names = []
        self.edeps = []

    def set_energy_tbl(self, energy_tbl):
        """
        Set energy table
        """
        from PyQt4 import QtGui
        self.names = self.world.get_name()
        self.energy_tbl = energy_tbl
        energy_tbl.setColumnCount(2)
        energy_tbl.setRowCount(len(self.names))
        for i in xrange(len(self.names)):
            energy_tbl.setItem(i, 0, QtGui.QTableWidgetItem(self.names[i]))
            self.edeps.append(0)
        energy_tbl.setHorizontalHeaderLabels(('Detektor', 'Energiedeposit / MeV'))
        energy_tbl.setColumnWidth(0, 110)
        energy_tbl.setColumnWidth(1, 152)
        self.update_energy_tbl()
        
    def set_canvas(self, canvas):
        if not self.world:
            print "WORLD not set"
            raise 
        self.canvas = canvas
        self.canvas.set_world(self.world)

    def add_particle(self, particle):
        particle.set_world(self.world)
        self.particles.append(particle)
        self.canvas.add_particle(particle)

    def step(self):
        from src.physics import MeV, eV
        ds = (self.world.bbox[2]-self.world.bbox[0])/100.
        pos_edep = []
        for particle in self.particles:
            pos, dE, dl = particle.step(ds)
            pos_x, pos_y = pos.mean(axis=0)
            dE = sum(dE)
            if dE/MeV > 0.001:
                pos_edep.append((pos_x, pos_y, dE))
                volume = self.world.get_volume(pos_x, pos_y)
                if volume:
                    i = self.names.index(volume.name)
                    self.edeps[i]+=dE/MeV
            if particle.energy <= 1*eV or \
               not self.world.is_in_bbox(particle.pos_x, particle.pos_y):
                if self.canvas:
                    i = self.particles.index(particle)
                    dot = self.canvas.p_dots.pop(i)
                    self.canvas.scene().removeItem(dot)
                self.particles.remove(particle)

        if self.canvas:
            self.canvas.draw_edep(pos_edep)
            self.canvas.draw_particles(self.particles)
        if self.energy_tbl:
            self.update_energy_tbl()
        if len(self.particles) == 0:
            self.timer.stop()
            
    def update_energy_tbl(self):
        """
        Update content of energy tbl
        """
        from PyQt4 import QtGui
        for i in xrange(len(self.edeps)):
            self.energy_tbl.setItem(i,1, QtGui.QTableWidgetItem(str(self.edeps[i])))
    def clear(self):
        self.particles = []
        if self.energy_tbl:
            for i in xrange(len(self.edeps)):
                self.edeps[i] = 0
        if self.canvas:
            self.canvas.clear()
            