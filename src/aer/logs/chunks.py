from numpy.ma.core import allclose
import numpy as np
from contracts import contract


@contract(events='array', interval='float,>0')
def aer_iterate_intervals(events, interval):
    """ 
        Returns chunks of events with the given interval. 
    
        Chunks can be empty. Yields timestamp, events
    """
    timestamps = events['timestamp']
    T0 = timestamps[0]
    T1 = timestamps[-1]
    chunks = list(get_chunks_linear(timestamps, T0, T1, interval))
    check_good_chunks(timestamps, T0, T1, interval, chunks)
    for a, b in chunks:
        timestamp = timestamps[a]
#         if a == b:  # no events in this chunk
#             continue
        Ei = events[a:b + 1]
        yield timestamp, Ei
        
@contract(timestamps='array', T0='float', T1='float', interval='float,>0')
def get_chunks(timestamps, T0, T1, interval):
    n = int(np.ceil((T1 - T0) / interval)) 
    
    for i in range(n):
        t0 = T0 + i * interval
        t1 = t0 + interval
        sel = np.logical_and(timestamps >= t0, timestamps < t1)
        indices, = np.nonzero(sel)
        yield indices[0], indices[-1]
        
@contract(timestamps='array', T0='float', T1='float', interval='float,>0')
def get_chunks_linear(timestamps, T0, T1, interval):
    n = int(np.ceil((T1 - T0) / interval))
    times = T0 + np.array(range(n + 1)) * interval
    
    chunks = np.searchsorted(timestamps, times)
    
    for i in range(chunks.size - 1):
        a = chunks[i]
        b = chunks[i + 1] - 1
        
        # this means that there are no events in this chunk
#         if a == b:
#             break
#         else:
        yield a, b
            
        s0 = T0 + i * interval
        s1 = s0 + interval
        
        # print 'a %s b %s T[a] %.5f T[b] %.5f s0 %.5f s1 %.5f' % (a, b, timestamps[a], timestamps[b], s0, s1)
        good = (timestamps[a] >= s0) and (allclose(timestamps[b], s1) or timestamps[b] <= s1)
        if not good:
            print 'i %s a,b %s %s T[a], T[b] %.5f  %.5f s0,s1 %.5f %.5f' % (i, a, b, timestamps[a], timestamps[b], s0, s1)
            eps1 = timestamps[a] - s0
            eps2 = s1 - timestamps[b] 
            print '%.10f  %.10f' % (eps1, eps2)
            raise Exception()
                
        
def check_good_chunks(timestamps, T0, T1, interval, chunks):
    n = int(np.ceil((T1 - T0) / interval))
    if len(chunks) != n:
        raise ValueError('expected %s, got %s' % (n, len(chunks)))
    for i in range(n):
        s0 = T0 + i * interval
        s1 = s0 + interval
        
        a, b = chunks[i]
        assert timestamps[a] >= s0
        assert allclose(timestamps[b], s1) or timestamps[b] <= s1

