LD50
====

A simple tool to visualize radiation damage in humans. - Toying araound with pyQt and matplotlib

Purpose
-------
This tools aims at visualizing the damage of different radiation types in the hman body. It is by no means a way o reliably calculate a radiation hazard.

Simplifciations
---------------
at this stage LD50 uses a lot of simplifications.

    * The model is only 2D
    * The Bethe-Bloch euqation is integrated via Euler method, and with way too lare steps
    * Neutron interactions are dummy values
    * The magnitude of the radiation damage is given by the radius of the circles. This can give the impression that a large area of the Body is affected.


License
-------
This tool is free to use and can be freely modifid and distributed. I'm gratefull for any contribution to this project.
    

Contact
-------

Jan Köhler

jan.koeh@gmail.com
