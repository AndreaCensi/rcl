import numpy as np
from contracts import contract
from procgraph_images.copied_from_reprep import skim_top


@contract(returns='array[X x Y]', shape='tuple(X,Y)')
def aer_histogram(events, shape=(128, 128)):
    """ 
        Makes a simple histogram of events. 
    
        first index: y
        second index, x
    """
    h = np.zeros(shape, dtype='int')
    for e in events:
        h[e['x'], e['y']] += 1
    return h


@contract(returns='array[X x Y]', shape='tuple(X,Y)')
def aer_histogram_2(events, shape=(128, 128)):
    """ 
        Makes a simple histogram of events. 
    
        This switches indices compared with the previous one
        first index: x
        second index: y
    """
    h = np.zeros(shape, dtype='int')
    for e in events:
        h[e['y'], e['x']] += 1
    return h


def aer_histogram_sign(events):
    """ Makes an  histogram of events, in which a plus counts + and a minus -. """
    h = np.zeros((128, 128), dtype='int')
    for e in events:
        h[e['x'], e['y']] += e['sign']
    return h

def aer_histogram_sign_2(events, shape):
    """ Makes an  histogram of events, in which a plus counts + and a minus -. 
        Different way to use indices. """
    h = np.zeros(shape, dtype='int')
    for e in events:
        h[e['y'], e['x']] += e['sign']
    return h


def aer_histogram_fancy(events):
    ep = events[events['sign'] > 0]
    en = events[events['sign'] < 0]
    hp = aer_histogram(ep)
    hn = aer_histogram(en)

    more = hn > hp

    hp[more] = -hn[more]

    return hp

def aer_histogram_fancy_2(events, shape, nhot=10):
#     print events['sign']
    ep = events[events['sign'] > 0]
    en = events[events['sign'] < 0]
    hp = aer_histogram_2(ep, shape=shape)
    hn = aer_histogram_2(en, shape=shape)

    top_percent = nhot * 100.0 / (shape[0] * shape[1])
    hp = skim_top(hp, top_percent)
    hn = -skim_top(-hn, top_percent)  # important: negative

    more = hn > hp

    hp[more] = -hn[more]

    hp = hp.astype('float')
    return hp



