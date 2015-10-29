# -*- coding: utf-8 -*-
"""
This file contains methods to create particle positions an directions
and a TABLE of available mathods

TABLE usage example:
--------------------
> list_of_available_methods = TABLE.keys()
> pos, dir = TABLE['CosLaw'](bbox)
"""

TABLE = {}

def cos_law():
    """
    Returns a cosine law angle.
    Used to generate an isotropic distribution
    """
    from numpy.random import rand
    from numpy import cos, sin, pi
    while True:
        theta = 0.5*rand()*pi
        y = rand()
        if y < cos(theta)*sin(theta):
            break
    if rand() > .5:
        theta *= -1
    return theta

def cos_square():
    """
    """
    from numpy.random import rand
    from numpy import sin, cos, pi
    while True:
        theta = 0.5*rand()*pi
        y = rand()
        if y < cos(theta)**2:#*sin(theta):
            break
    if rand() > .5:
        theta *= -1
    return theta
    
def gen_beam_top(bbox):
    """
    Returns a 20% wide beam wich hits the volume from the top
    
    Args:
    -----
    bbox : tuple
        The worlds bbox
        
    Returns:
    --------
    pos, dir : list, float
        pos is the [x, y] position, dir the angle
    """
    from .physics import deg
    from numpy.random import rand
    x0, y0, x1, y1 = bbox
    x = (x0+x1)/2 + (x1-x0)/5 * (rand()-.5)
    y = y1
    dir = 270*deg
    return [x, y], dir    
    
def gen_beam_left(bbox):
    """
    Returns a 20% wide beam wich hits the volume from the left
    
    Args:
    -----
    bbox : tuple
        The worlds bbox
        
    Returns:
    --------
    pos, dir : list, float
        pos is the [x, y] position, dir the angle
    """
    from numpy.random import rand
    x0, y0, x1, y1 = bbox
    x = x0
    y = (y0+y1)/2 + (y1-y0)/5 * (rand()-.5)
    dir = 0
    return [x, y], dir    

def gen_beam_right(bbox):
    """
    Returns a 20% wide beam wich hits the volume from the right
    
    Args:
    -----
    bbox : tuple
        The worlds bbox
        
    Returns:
    --------
    pos, dir : list, float
        pos is the [x, y] position, dir the angle
    """
    from .physics import deg
    from numpy.random import rand
    x0, y0, x1, y1 = bbox
    x = x1
    y = (y0+y1)/2 + (y1-y0)/5 * (rand()-.5)
    dir = 180*deg
    return [x, y], dir
    
def gen_isotrop(bbox):
    """
    Returns an isotropic radiation field
    
    Args:
    -----
    bbox : tuple
        The worlds bbox
        
    Returns:
    --------
    pos, dir : list, float
        pos is the [x, y] position, dir the angle
    """
    from .physics import deg
    from numpy.random import rand
    x0, y0, x1, y1 = bbox    
    side = rand()*((x1-x0)+2*(y1-y0)*2)
    if side < y1-y0:
        dir = cos_law()
        pos_x = x0
        pos_y = y0 + rand()*(y1-y0)
    elif side < y1-y0 + x1-x0:
        dir = cos_law() + 270*deg
        pos_x = x0 + rand()*(x1-x0)
        pos_y = y1
    elif side < (y1-y0)*2 + x1-x0:
        dir= cos_law() + 180*deg
        pos_x = x1
        pos_y = y0 + rand()*(y1-y0)   
    else:
        dir = cos_law() + 90*deg
        pos_x = x0 + rand()*(x1-x0)
        pos_y = y0  
    return [pos_x, pos_y], dir

def gen_cos2(bbox):
    """
    Returns an cos2 radiation field
    
    Args:
    -----
    bbox : tuple
        The worlds bbox
        
    Returns:
    --------
    pos, dir : list, float
        pos is the [x, y] position, dir the angle
    """    
    from .physics import deg
    from numpy.random import rand
    x0, y0, x1, y1 = bbox    
    dir = cos_square() + 270*deg
    pos_x = x0 + (.2  + .6*rand())*(x1-x0)
    return [pos_x, y1], dir
    
TABLE['Isotrop'] = gen_isotrop
TABLE['Strahl von Oben'] = gen_beam_top
TABLE['Strahl von Links'] = gen_beam_left
TABLE['Strahl von Rechts'] = gen_beam_right
TABLE['Hoehenstrahlung'] = gen_cos2
