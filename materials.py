# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 18:05:05 2014

@author: koehler
"""

from physics import q_e, g, cm3, amu, m, eV, MeV, cm2, m3

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
    def get_gamma_mfp(self, energy):
        """Neutron mean free path length"""
        return 1e30*m

class Water(Material):
    def __init__(self, load_x_sections=True):
        from physics import barn
        super(Water, self).__init__(8., 16., 1.*g/cm3)      
        if load_x_sections:
            from numpy import loadtxt
            from scipy.interpolate import interp1d
            energy_H = loadtxt("X-sections/n_X_section_H.txt", 
                               usecols=[0,2,4],skiprows=2).ravel()
            sigma_H = loadtxt("X-sections/n_X_section_H.txt", 
                              usecols=[1,3,5], skiprows=2).ravel()
            energy_O = loadtxt("X-sections/n_X_section_O.txt",
                               usecols=[0,2,4], skiprows=2).ravel()
            sigma_O = loadtxt("X-sections/n_X_section_O.txt", 
                              usecols=[1,3,5], skiprows=2).ravel()
            self.n_xsec_H = interp1d(energy_H*eV, sigma_H*barn)
            self.n_xsec_O = interp1d(energy_O*eV, sigma_O*barn)
            self.n_dens_H = 2*33.3679e27/m3
            self.n_dens_O = 33.3679e27/m3
            g_energy, attenuation = loadtxt('X-sections/g_X_section_H20.txt', 
                                            skiprows=9,
                                            usecols=[0, 7], unpack=True)
            self.g_attn = interp1d(g_energy*MeV, attenuation*cm2/g)
                                            
    def get_mean_ex_pot(self):
        return 75*q_e
    def get_e_density(self):
        return 3.3456e29/m3
    def get_neutron_mfp(self, energy):
        """
        returns mfp for H and O
        """
        return [1./(self.n_dens_H*self.n_xsec_H(energy)),
               1./(self.n_dens_O*self.n_xsec_O(energy))]

    def get_gamma_mfp(self, energy):
        """
        Returns mfp for gammas in H2O
        """        
        return [1./(self.g_attn(energy)*1*g/cm3)]