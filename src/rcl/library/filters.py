from . import np
from rcl.library.aerlog import (aer_raw_event_dtype, aer_filtered_event_dtype)

def aer_raw_relative_timestamp(aer_raw_seq):
    """ Lets the first timestamp be 0 """
    t0 = None
    for e in aer_raw_seq:
        if t0 is None:
            t0 = float(e['timestamp'])
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
    """ Creates a sequence of aer_filtered_events. """
    def __init__(self, shape=(128, 128)):
        self.shape = shape
        self.last_event = np.zeros(shape, dtype=aer_raw_event_dtype)
        self.last_event['timestamp'] = 0

    def filter(self, raw_event_sequence):
        pairs = AER_pairs(aer_raw_event_dtype).get_pairs(raw_event_sequence)
        
        for le, e in pairs:
            # filtered event 
            fe = np.zeros((), dtype=aer_filtered_event_dtype)
            fe['timestamp'] = e['timestamp']
            fe['x'] = e['x']
            fe['y'] = e['y']
            fe['sign'] = e['sign']
            fe['delta'] = e['timestamp'] - le['timestamp']
            fe['same'] = (e['sign'] == le['sign'])

            fe['frequency'] = 1.0 / fe['delta']
            yield fe


class AER_pairs(object):
    """ Remembers pairs of events """
    def __init__(self, dtype, shape=(128, 128)):
        self.last = np.zeros(shape, dtype=dtype)
        self.last['timestamp'] = 0
    
    def get_pairs(self, seq):
        for e in seq:
            x, y = e['x'], e['y']
            le = self.last[x, y]        
            # Ignore if we did not trigger
            if le['timestamp'] > 0:    
                yield le.copy(), e.copy()
            self.last[x, y] = e  


def aer_transitions(events, sign):
    for e in events:
        # only get transitions
        if sign == e['sign'] and not e['same']:
            yield e
    
    
class AER_Transitions_Filter(object):
    """ Remembers the transitions """
    def __init__(self, sign=(-1)):
        self.sign = sign
        self.pairs = AER_pairs(aer_filtered_event_dtype)
        
    def get_transitions(self, filtered_event_sequence):
        """ Yields pairs of events. """
        transitions = aer_transitions(filtered_event_sequence, self.sign)
        pairs = self.pairs.get_pairs(transitions)
        for e1, e2 in pairs:
            e = e2.copy()
            e['delta'] = e2['timestamp'] - e1['timestamp']
            e['frequency'] = 1.0 / e['delta']
            yield e
            
            
