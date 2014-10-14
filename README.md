LD50
====

A simple tool to visualize radiation damage in humans. - Toying around with pyQt.

Purpose
-------
This tools aims at visualizing the damage of different radiation types in the human body (or matter in general). It is by no means a way to reliably calculate a radiation hazard.

Updates
-------
Changed matplotlib backend to Qt.

Usage
-------
In addition to the human torso the geonetry of the Radiation Assessment Detector (RAD) (see http://mslrad.boulder.swri.edu/) is also available. The simulation setup can be defined in `setup.py`.
Set a human body via `WORLD = HUMAN`, set RAD via `WORLD = RAD`.

Install
-------
LD50 is written in Python 2.7 and makes use of Py QT and numpy/scipy.
To get a complete and ready-to-use python setup, you can download https://code.google.com/p/pythonxy/

If you don't want to download/install the whole phythonxy package, you have to download/install 
* https://www.python.org/download/releases/2.7.8/
* http://www.scipy.org/scipylib/download.html
* http://www.riverbankcomputing.com/software/pyqt/download

To Start the LD50, just execute LD50.py


Simplifications
---------------
at this stage LD50 uses a lot of simplifications.
* The model is only 2D
* The Bethe-Bloch equation is integrated via Euler method
* Neutron/gamma angular scattering are dummy values
* The magnitude of the radiation damage is given by the radius of the circles. This can give the impression that a large area of the Body is affected.
* The Torso is located in Vacuum, not in air. I.e. energy loss of particles in air is neglected.


License
-------
This tool is free to use and can be freely modified and distributed. I'm grateful for any contribution to this project.
    


Contact
-------

Jan Köhler

jan.koeh@gmail.com
