#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import HUMAN as geometry
from src import RunManager, start_gui
run_manager = RunManager(geometry)
start_gui(run_manager)


