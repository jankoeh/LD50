# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 17:58:59 2014
Some file to define geometry
@author: koehler
"""

from physics import Volume, MotherVolume
from materials import Water

WORLD = MotherVolume([Volume('gfx/torso2.png', 'Body', Water())], 
                    [(0, 0)])