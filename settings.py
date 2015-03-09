# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 17:58:59 2014
Some file to define geometry
@author: koehler
"""
from src.physics import Volume, MotherVolume, cm
from src.materials import TABLE as m_tbl

HUMAN = MotherVolume([Volume('gfx/torso2.png', 'Body', m_tbl['H2O'])])

A = Volume("gfx/RAD_A.png", "A", m_tbl['Silicon'], s2px=1192./16/cm)
B = Volume("gfx/RAD_B.png", "B", m_tbl['Silicon'], s2px=1192./16/cm)
C = Volume("gfx/RAD_C.png", "C", m_tbl['Silicon'], s2px=1192./16/cm)
D = Volume("gfx/RAD_D.png", "D", m_tbl['CsI'], s2px=1192./16/cm)
E = Volume("gfx/RAD_E.png", "E", m_tbl['H2O'], s2px=1192./16/cm)
F = Volume("gfx/RAD_F.png", "F", m_tbl['H2O'], s2px=1192./16/cm)
RAD = MotherVolume([A, B, C, D, E, F])


CANCER_BG = Volume("gfx/cancer_bg.png", "Gesundes Gewebe", m_tbl['H2O'], s2px=700./16/cm)
CANCER_FG = Volume("gfx/cancer_fg.png", "Krankes gewebe", m_tbl['H2O'], s2px=700./16/cm)
CANCER = MotherVolume([CANCER_BG, CANCER_FG])
