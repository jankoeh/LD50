# -*- coding: utf-8 -*-
"""
Created on Sun Jun 01 11:24:13 2014

@author: koehler
"""
from scipy.constants import atomic_mass as amu, e as q_e, pi

mm = 1e-3
cm = 1e-2
m = 1
km = 1e3

cm3 = 1e-6
m3 = 1

g =1e-3
kg = 1

MeV = q_e*1e6

deg = 2*pi/360

class Material(object):
    def __init__(self, Z, A, rho):
        self.Z = Z
        self.A = A
        self.rho = rho
    def get_I(self):
        """bethe"""
        return 10 * q_e * self.Z
    def get_n(self):
        """ bethe"""
        return self.Z*self.rho/self.A/amu
        
class Volume(object):
    def __init__(self, fn_image, s2px=1e3, material=Material(8., 16., 1.*g/cm3)):
        from scipy.misc import imread
        self.image = imread(fn_image)
        self.s2px = s2px
        self.material = material
    def is_inside(self, pos_x, pos_y):
        """ """
        pos_x = int(pos_x*self.s2px)
        pos_y = int(pos_y*self.s2px)
        if self.image.shape[0]<=pos_y or pos_y<0 or \
           self.image.shape[1]<=pos_x or pos_x<0:
            return False
        if self.image[pos_y][pos_x][0]>0:
            return True
        else:
            return False


class ChargedParticle(object):
    def __init__(self, mass, charge, energy, pos, direction, volume):
        self.mass = mass
        self.charge = charge    #e
        self.energy = energy
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
            dE = self.bethe()* ds
            if dE > self.energy:
                dE = self.energy
            self.energy -= dE
        else: 
            dE = 0
        self.pos_x += np.cos(self.dir)*ds
        self.pos_y += np.sin(self.dir)*ds
        self.path.append((self.pos_x, self.pos_y))
        self.dE.append(dE)
        return self.pos_x, self.pos_y, dE
    
    def get_velocity(self):
        from scipy.constants import c
        from numpy import sqrt
        return sqrt(1-(self.energy/(self.mass*c**2)+1)**-2)*c
    def bethe(self):
        """
        """
        from numpy import log
        from scipy.constants import epsilon_0, c, pi, m_e
        I = self.volume.material.get_I()
        n = self.volume.material.get_n()
        v = self.get_velocity()
        z = self.charge/q_e
        beta = v/c
        return 4*pi*n*z**2/(m_e*c**2*beta**2)*(q_e**2/(4*pi*epsilon_0))**2* \
            (log(2*m_e*c**2*beta**2/I/(1-beta**2))-beta**2)
            
