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

g = 1e-3
kg = 1

eV = q_e
keV = q_e*1e3
MeV = q_e*1e6

deg = 2*pi/360

barn = 1e-28

def quality_factor(L):
    """
    Quality factor according to wikipedia
    """
    from numpy import sqrt
    L /= (keV/um)
    if L < 10:
        return 1
    elif L < 100:
        return 0.32*L-2.2
    else:
        return 300./sqrt(L)

def cos_law():
    """
    Returns a cosine law angle.
    Used to generate an isotropic distribution
    """
    from numpy.random import rand
    from numpy import cos, sin
    while True:
        theta = 0.5*rand()*pi
        y = rand()
        if y < cos(theta)*sin(theta):
            break
    if rand() > .5:
        theta *= -1
    return theta

def cos_square():
    """
    Returns a cosine law angle.
    Used to generate an isotropic distribution
    """
    from numpy.random import rand
    from numpy import cos
    while True:
        theta = 0.5*rand()*pi
        y = rand()
        if y < cos(theta)*cos(theta):
            break
    if rand() > .5:
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
    def __init__(self, load_x_sections=True):
        super(Water, self).__init__(8., 16., 1.*g/cm3)      
        if load_x_sections:
            from numpy import loadtxt
            from scipy.interpolate import interp1d
            energy_H = loadtxt("n_x_section_H.txt", 
                               usecols=[0,2,4],skiprows=2).ravel()
            sigma_H = loadtxt("n_x_section_H.txt", 
                              usecols=[1,3,5], skiprows=2).ravel()
            energy_O = loadtxt("n_x_section_O.txt",
                               usecols=[0,2,4], skiprows=2).ravel()
            sigma_O = loadtxt("n_x_section_O.txt", 
                              usecols=[1,3,5], skiprows=2).ravel()
            self.xsec_H = interp1d(energy_H*eV, sigma_H*barn)
            self.xsec_O = interp1d(energy_O*eV, sigma_O*barn)
            self.n_dens_H = 2*33.3679e27/m3
            self.n_dens_O = 33.3679e27/m3
    def get_mean_ex_pot(self):
        return 75*q_e
    def get_e_density(self):
        return 3.3456e29/m3
    def get_neutron_mfp(self, energy):
        """
        returns mfp for H and O
        """
        return [1./(self.n_dens_H*self.xsec_H(energy)),
               1./(self.n_dens_O*self.xsec_O(energy))]

class Volume(object):
    def __init__(self, fn_image, s2px=1e3,\
                 material=Material(8., 16., 1.*g/cm3)):
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
            return self.material.get_mean_ex_pot(), self.material.get_e_density()
        else:
            return 1e-30, 0
    def get_neutron_mfp(self, pos_x, pos_y, energy):
        """
        Returns the mean free path for neutrons
        """
        if self.is_inside(pos_x, pos_y):            
            return self.material.get_neutron_mfp(energy)
        else:
            return []

WORLD = Volume('torso2.png', material=Water())

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
        N = ds/(.1*mm)
        pos = []
        edep = []
        for i in xrange(int(N)):
            if self.energy < 1*eV:
                break
            dE = self.energy_loss(ds/N)
            if dE > self.energy:
                dE = self.energy
            self.energy -= dE
            self.pos_x += np.cos(self.dir)*ds/N
            self.pos_y += np.sin(self.dir)*ds/N
            pos.append((self.pos_x, self.pos_y))
            edep.append(dE)
        return np.array(pos), np.array(edep), ds/N

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
        mexpot, edens = WORLD.get_mexpot_edens(self.pos_x, self.pos_y)
        v = self.get_velocity()
        z = self.charge/q_e
        beta = v/c_light
        return 4*pi*edens*z**2/(m_e*c_light**2*beta**2)*\
            (q_e**2/(4*pi*epsilon_0))**2* \
            (log(2*m_e*c_light**2*beta**2/mexpot/(1-beta**2))-beta**2)*ds

class Neutron(Particle):
    def energy_loss(self, ds):
        """
        straggeling
        """
        from numpy.random import rand
        dE = 0
        for mfp in WORLD.get_neutron_mfp(self.pos_x, self.pos_y, self.energy):
            if ds/mfp> rand():
                dE += min((20*MeV, self.energy*rand()))
            if dE > 10*keV:
                self.dir += rand()*40*deg-20*deg
        return dE
