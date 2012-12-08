import numpy as np
from contracts import contract

aer_color_sequence = ['r', 'g', 'b', 'y']
        
        
@contract(returns='dict(str:str)')
def get_track_colors(tracks):
    """ Returns a dictionary id_track -> color """
    id_tracks = np.unique(tracks['id_track'])
    labels = sorted(id_tracks, key=int)
    
    res = {}
    for i, label in enumerate(labels):
        c = aer_color_sequence[i % len(aer_color_sequence)]
        res[label] = c
    return res 

from .aer_log_reader import *
from .aer_quality_plotter import *
from .aer_track_plotter import *
from .aer_smoother import *
from .aer_resolver import *
from .aer_alt_plotter import *
from .aer_pf import *
