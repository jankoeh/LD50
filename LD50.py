#!/usr/bin/env python
# -*- coding: utf-8 -*-

from settings import RAD as world

from src.base import RunManager
run_manager = RunManager(world)

from src.gui import start_gui
start_gui(run_manager)


