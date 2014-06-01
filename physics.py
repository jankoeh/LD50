# -*- coding: utf-8 -*-
"""
Created on Sun Jun 01 11:24:13 2014

@author: koehler
"""

class Volume(object):
    def __init__(self, fn_image, mm2px=1, material=(8., 16., 1.)):
        from scipy.misc import imread
        self.image = imread(fn_image)
        self.mm2px = mm2px
        self.Z = material[0]
        self.A = material[1]
        self.rho = material[2]*1e3
    def is_inside(self, pos_x, pos_y):
        """ """
        pos_x = int(pos_x*self.mm2px)
        pos_y = int(pos_y*self.mm2px)
        if self.image.shape[0]<=pos_y or pos_y<0 or \
           self.image.shape[1]<=pos_x or pos_x<0:
            return False
        if self.image[pos_y][pos_x][0]>0:
            return True
        else:
            return False
    def get_I(self):
        from scipy.constants import e
        return 10 * e * self.Z
    def get_n(self):
        from scipy.constants import atomic_mass as u
        return self.Z*self.rho/self.A/u

class ChargedParticle(object):
    def __init__(self, mass, charge, energy, pos, direction, volume):
        self.mass = mass       #AMU
        self.charge = charge    #e
        self.energy = energy     #MeV
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.dir = direction
        self.volume = volume
        
        self.path = []
        self.dE = []

    def step(self, ds):
        """
        Make a ds step, return new pos and energy loss
        """
        import numpy as np
        if self.volume.is_inside(self.pos_x, self.pos_y):
            from scipy.constants import e
            dE=self.bethe()/e*1e-6 * ds/100
            if dE > self.energy:
                dE = self.energy
            self.energy -= dE
        else: dE=0
        self.pos_x += np.cos(self.dir)*ds
        self.pos_y += np.sin(self.dir)*ds
        self.path.append((self.pos_x, self.pos_y))
        self.dE.append(dE)
        return self.pos_x, self.pos_y, dE
    
    def get_velocity(self):
        from scipy.constants import atomic_mass as u, c, e
        from numpy import sqrt
        return sqrt(1-(self.energy*e*1e6/(self.mass*u*c**2)+1)**-2)*c
    def bethe(self):
        """
        """
        from numpy import log
        from scipy.constants import epsilon_0, c, pi, m_e, e
        I = self.volume.get_I()
        n = self.volume.get_n()
        v = self.get_velocity()
        z = self.charge
        beta = v/c
        return 4*pi*n*z**2/(m_e*c**2*beta**2)* (e**2/(4*pi*epsilon_0))**2* \
            (log(2*m_e*c**2*beta**2/I/(1-beta**2))-beta**2)