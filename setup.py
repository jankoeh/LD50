# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 17:58:59 2014
Some file to define geometry
@author: koehler
"""
from physics import Volume, MotherVolume, cm
from materials import TABLE as m_tbl

HUMAN = MotherVolume([Volume('gfx/torso2.png', 'Body', m_tbl['H2O'])])

ABC = Volume("gfx/RAD_ABC.png", "ABC", m_tbl['Silicon'], s2px=1192./16/cm)
D = Volume("gfx/RAD_D.png", "D", m_tbl['CsI'], s2px=1192./16/cm)
EF = Volume("gfx/RAD_EF.png", "EF", m_tbl['H2O'], s2px=1192./16/cm)
RAD = MotherVolume([ABC, D, EF])

#Define your WORLD here
WORLD = HUMAN