from . import np, logger
from StringIO import StringIO
from rcl.library.aerlog.types import (aer_raw_event_dtype,
    aer_filtered_event_dtype)


def aer_raw_sequence(line_stream):
    """ Yields a sequence of events from a stream.
        Returns a raw_event_dtype.
     """
    for line in line_stream:
        io = StringIO(line)  # XXX inefficient
        try:
            a = np.genfromtxt(io, dtype=aer_raw_event_dtype)
        except ValueError as e:
            msg = 'Could not read line %r: %s' % (line, e)
            logger.error(msg)
            raise
                
        a['timestamp'] = a['timestamp'] * 0.001 * 0.001
        if a['sign'] == 0:
            a['sign'] = -1
        yield a

def aer_raw_relative_timestamp(aer_raw_seq):
    t0 = None
    for e in aer_raw_seq:
        if t0 is None:
            t0 = e['timestamp']
        e['timestamp'] -= t0
        yield e
    
def aer_raw_only_minus(aer_raw_seq):
    """ Only yields minus events """
    for e in aer_raw_seq:
        if e['sign'] == -1:
            yield e

def aer_filtered_cutoff(aer_filtered_seq, min_frequency, max_frequency):
    for e in aer_filtered_seq:
        if min_frequency <= e['frequency'] <= max_frequency:
            yield e
    

class AER_Filter(object):
    def __init__(self, shape=(128, 128)):
        self.shape = shape
        self.last_event = np.zeros(shape, dtype=aer_raw_event_dtype)
        self.last_event['timestamp'] = 0
        
    def filter(self, raw_event_sequence):
        for e in raw_event_sequence:
            x, y = e['x'], e['y']
            
#            if True:  # XXX
#                scale = 2
#                x = x / scale
#                y = y / scale
#            
            # last event
            le = self.last_event[x, y]
            
            # Ignore if we did not trigger
            if le['timestamp'] == 0:
                self.last_event[x, y] = e  # XXX 
            else:
                
                # filtered event 
                fe = np.zeros((), dtype=aer_filtered_event_dtype)
                fe['timestamp'] = e['timestamp']
                fe['timestamp_prev'] = le['timestamp']
                fe['x'] = e['x']
                fe['y'] = e['y']
                fe['sign'] = e['sign']
                fe['delta'] = e['timestamp'] - le['timestamp']
                fe['frequency'] = 1.0 / fe['delta']
                fe['sign'] = e['sign']
                fe['sign_prev'] = le['sign']
                fe['same'] = e['sign'] == le['sign']

                yield fe
                                
                self.last_event[x, y] = e  # XXX
                

