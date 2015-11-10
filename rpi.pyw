#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import RPI as geometry
from src import RunManager, start_gui, particles
#remove distracting particles
particles.TABLE.pop("Kohlenstoff")
particles.TABLE.pop("Elektron")
particles.TABLE.pop("Alpha")
particles.TABLE.pop("Gamma")
particles.TABLE.pop("Muon")
particles.TABLE.pop("Proton")
particles.TABLE.pop('Neutron')

run_manager = RunManager(geometry)
start_gui(run_manager)


