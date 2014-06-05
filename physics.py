# -*- coding: utf-8 -*-
"""
Created on Sun Jun 01 11:24:13 2014

@author: koehler
"""
#constants
from scipy.constants import \
    atomic_mass as amu,\
    e as q_e, \
    pi, \
    m_e, \
    c as c_light,\
    epsilon_0
from scipy.constants import physical_constants
m_muon = physical_constants['muon mass'][0]

#Units
um = 1e-6
mm = 1e-3
cm = 1e-2
m = 1
km = 1e3

cm3 = 1e-6
m3 = 1

g =1e-3
kg = 1

eV = q_e
keV = q_e*1e3
MeV = q_e*1e6

deg = 2*pi/360

def quality_factor(L):
    """
    Quality factor according to wikipedia
    """
    from numpy import sqrt
    if L < 10*keV/um:
        return 1
    elif L < 100*keV/um:
        return 0.32*L-2.2
    else:
        300./sqrt(L)

def cos_law():
    from numpy.random import rand
    from numpy import cos, sin
    while True:
        theta = 0.5*rand()*pi
        y = rand()
        if y < cos(theta)*sin(theta): 
            break
    if rand()>.5:
        theta *= -1
    return theta

class Material(object):
    def __init__(self, Z, A, rho):
        self.Z = Z
        self.A = A
        self.rho = rho
    def get_mean_ex_pot(self):
        """
        returns the means excitation potential        
        """
        return 10 * q_e * self.Z
    def get_e_density(self):
        """
        returns the material specific electron density        
        """
        return self.Z*self.rho/self.A/amu
    def get_neutron_mfp(self, energy):
        """Neutron mean free path length"""
        return 1e30*m

class Water(Material):
    def get_I(self):
        return 75*q_e
    def get_n(self):
        return 3.3456e29/m3
    def get_neutron_mfp(self, energy):
        #FIXME TODO
        return 10*cm
        
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
        if self.image[-pos_y][pos_x][0]>0:
            return True
        else:
            return False
    def get_mexpot_edens(self, pos_x, pos_y):
        """
        Returns a tuple o the 
        means excitation potential and the electron density
        """
        if self.is_inside(pos_x, pos_y):
            return self.material.get_I(), self.material.get_n()
        else:
            return 1e-30, 0 
    def get_neutron_mfp(self, pos_x, pos_y, energy):
        """
        Returns the mean free path for neutrons
        """
        if self.is_inside(pos_x, pos_y):
            return self.material.get_neutron_mfp(energy)
        else:
            return 1e30

WORLD = Volume('torso2.png', material=Water(8., 16., 1.*g/cm3))

class Particle(object):
    def __init__(self, mass, charge, energy, pos, direction):
        self.mass = mass
        self.charge = charge    #e
        self.energy = energy
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.dir = direction
        
        self.path = []
        self.dE = []

    def step(self, ds):
        """
        Make a ds step, return new pos and energy loss
        """
        import numpy as np

        dE = self.energy_loss(ds)
        if dE > self.energy-10*eV:
            dE = self.energy
        self.energy -= dE

        pos_x = self.pos_x
        pos_y = self.pos_y
        self.pos_x += np.cos(self.dir)*ds
        self.pos_y += np.sin(self.dir)*ds
        return pos_x, pos_y, dE
    
    def get_velocity(self):
        """Returns the particle velocity"""
        from numpy import sqrt
        if self.energy == 0:
            return 0
        return sqrt(1-(self.energy/(self.mass*c_light**2)+1)**-2)*c_light
    def energy_loss(self, ds):
        """
        Prototype funktion for energy_loss and angular scattering
        """        
        return 0


class ChargedParticle(Particle):
    def energy_loss(self, ds):
        """
        Beethe Bloch
        """
        from numpy import log
        I, n = WORLD.get_mexpot_edens(self.pos_x, self.pos_y)
        v = self.get_velocity()
        z = self.charge/q_e
        beta = v/c_light
        return 4*pi*n*z**2/(m_e*c_light**2*beta**2)*\
            (q_e**2/(4*pi*epsilon_0))**2* \
            (log(2*m_e*c_light**2*beta**2/I/(1-beta**2))-beta**2)*ds    
            
class Neutron(Particle):
    def energy_loss(self, ds):
        """
        straggeling
        """
        from numpy.random import rand
        dE = 0
        mfp = WORLD.get_neutron_mfp(self.pos_x, self.pos_y, self.energy)
        if ds/mfp> rand():
            dE = min((20*MeV, self.energy*rand()))
        if dE > 10*keV:
            self.dir += rand()*40*deg-20*deg
        return dE