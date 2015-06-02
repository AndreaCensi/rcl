from contracts import contract
import numpy as np


@contract(x='array[N]', returns='array[N](>=0,<=N-1)')
def scale_score(x):
    import scipy.stats
    return scipy.stats.mstats.rankdata(x) - 1

@contract(x='array[N]', returns='array[N](>=0,<=1)')
def scale_score_smooth(x):
    if len(x) == 0:
        return np.zeros(shape=(0,))
    
    if x.size > 1:
        rank = scale_score(x)
        rank = rank * 1.0 / (rank.size - 1)        
        return rank
    else:
        return np.array([1.0])
    
    
