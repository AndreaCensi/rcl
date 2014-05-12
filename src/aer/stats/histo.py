import numpy as np
from contracts import contract


@contract(returns='array[128x128]')
def aer_histogram(events):
    """ 
        Makes a simple histogram of events. 
    
        first index: y
        second index, x
    """
    h = np.zeros((128, 128), dtype='int')
    for e in events:
        h[e['x'], e['y']] += 1
    return h

def aer_histogram_sign(events):
    """ Makes an  histogram of events, in which a plus counts + and a minus -. """
    h = np.zeros((128, 128), dtype='int')
    for e in events:
        h[e['x'], e['y']] += e['sign']
    return h


def aer_histogram_fancy(events):
    ep = events[events['sign'] > 0]
    en = events[events['sign'] < 0]
    hp = aer_histogram(ep)
    hn = aer_histogram(en)
    
    more = hn > hp
    
    hp[more] = -hn[more]

    return hp
