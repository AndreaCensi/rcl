from contracts import contract
import numpy as np 

aer_color_sequence = ['r', 'g', 'b', 'y']
        
@contract(returns='dict(str:str)', tracks='array[>=1]')
def get_track_colors(tracks):
    """ Returns a dictionary id_track -> color """
    id_tracks = np.unique(tracks['id_track'])
    labels = sorted(id_tracks, key=int)
    
    res = {}
    for i, label in enumerate(labels):
        c = aer_color_sequence[i % len(aer_color_sequence)]
        res[label] = c
    return res 


def set_viewport_style(pylab):
    """ Sets the style to display the tracking data """
    pylab.axis((-1, 128, -1, 128))
    pylab.xticks([], [])
    pylab.yticks([], [])

