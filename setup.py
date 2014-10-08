# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 17:58:59 2014
Some file to define geometry
@author: koehler
"""
WORLD = None

from physics import Volume, MotherVolume, g, cm3

from materials import Material
silicon = Material(14, 28.085, 2.336*g/cm3 ,
                   "X-sections/n_X_section_Si.txt", 
                   "X-sections/g_X_section_Si.txt" )

from materials import Water, CesiumIodide

HUMAN = MotherVolume([Volume('gfx/torso2.png', 'Body', Water())])


ABC = Volume("gfx/RAD_ABC.png", "ABC", silicon, s2px=7450.)
D = Volume("gfx/RAD_D.png", "D", CesiumIodide(), s2px=7450.)
EF = Volume("gfx/RAD_EF.png", "EF", Water(), s2px=7450.)
RAD = MotherVolume([ABC, D, EF])

WORLD = HUMAN