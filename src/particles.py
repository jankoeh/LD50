# -*- coding: utf-8 -*-
"""
This file contains the particle classes and a TABLE of defined particles

TABLE usage example:
--------------------
> list_of_available_particles = TABLE.keys()
> proton = TABLE['Proton'](energy, [x, y], dir)
"""
from .physics import mm, eV, c_light, amu, q_e, m_e, m_muon, MeV, deg, pi, \
    epsilon_0, keV

TABLE = {}

class Particle(object):
    def __init__(self, mass, charge, energy, pos, direction):
        self.mass = mass
        self.charge = charge    #e
        self.energy = energy
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.dir = direction

        self.world = None

    def set_world(self, world):
        self.world = world
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
        mexpot, edens = self.world.get_mexpot_edens(self.pos_x, self.pos_y)
        v = self.get_velocity()
        z = self.charge/q_e
        beta = v/c_light
        return 4*pi*edens*z**2/(m_e*c_light**2*beta**2)*\
            (q_e**2/(4*pi*epsilon_0))**2* \
            (log(2*m_e*c_light**2*beta**2/mexpot/(1-beta**2))-beta**2)*ds

class Neutron(Particle):
    def __init__(self, energy, pos, direction):
        super(Neutron, self).__init__(amu, 0, energy, pos, direction) 
    def energy_loss(self, ds):
        """
        straggeling
        """
        from numpy.random import rand
        dE = 0
        for mfp in self.world.get_neutron_mfp(self.pos_x, self.pos_y, self.energy):
            if ds/mfp> rand():
                dE += min((20*MeV, self.energy*rand()))
            if dE > 10*keV:
                self.dir += (rand()-.5)*80*deg
        return dE

class Gamma(Particle):
    def __init__(self, energy, pos, direction):
        super(Gamma, self).__init__(0, 0, energy, pos, direction)     
    def energy_loss(self, ds):
        """
        scattering and photo ion
        Simple 'model' which takes the overall mfp and sets every edep below
        0.1MeV as photo ionization.
        """
        from numpy.random import rand
        dE = 0
        for mfp in self.world.get_gamma_mfp(self.pos_x, self.pos_y, self.energy):
            if ds/mfp > rand(): #Crappy way to 'simulate' photo ionization 
                if self.energy < 0.1*MeV:
                    dE += self.energy
                elif self.energy < 3.*MeV:
                    dE += self.energy*(.5+rand()/2)
                else:
                    dE +=  min((20*MeV, self.energy*rand()/2))
            if dE > 10*keV:
                self.dir += (rand()-.5)*80*deg
        return dE



TABLE['Proton'] = lambda energy, pos, dir: ChargedParticle(1*amu, 
                                                           1*q_e, 
                                                           energy,
                                                           pos, 
                                                           dir)
TABLE['Alpha'] = lambda energy, pos, dir: ChargedParticle(4*amu, 
                                                          2*q_e, 
                                                          energy,
                                                          pos, 
                                                          dir)
TABLE['Kohlenstoff'] = lambda energy, pos, dir: ChargedParticle(6*amu, 
                                                                12*q_e, 
                                                                energy,
                                                                pos, 
                                                                dir)  
TABLE['Elektron'] = lambda energy, pos, dir: ChargedParticle(m_e, 
                                                             q_e, 
                                                             energy,
                                                             pos, 
                                                             dir)
TABLE['Muon'] = lambda energy, pos, dir: ChargedParticle(m_muon, 
                                                         q_e, 
                                                         energy,
                                                         pos, 
                                                         dir)
TABLE['kosmisches Muon'] = lambda energy, pos, dir: ChargedParticle(m_muon, 
                                                         q_e, 
                                                         energy,
                                                         pos, 
                                                         dir)

TABLE['Neutron'] = lambda energy, pos, dir: Neutron(energy,
                                                    pos, 
                                                    dir)
TABLE['Gamma'] = lambda energy, pos, dir: Gamma(energy, 
                                                pos, 
                                                dir)
TABLE['Gammazerfall'] = lambda energy, pos, dir: Gamma(energy, 
                                                pos, 
                                                dir)
                                                
TABLE['Alphazerfall'] = lambda energy, pos, dir: ChargedParticle(6*amu, 
                                                                12*q_e, 
                                                                energy,
                                                                pos, 
                                                                dir)                                                