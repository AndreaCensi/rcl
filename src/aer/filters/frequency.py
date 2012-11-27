from . import aer_filter_pairs, np
from aer import aer_raw_event_dtype, aer_filtered_event_dtype

__all__ = ['aer_filter_successive']

class AER_Filter(object):
    """ Creates a sequence of aer_filtered_events. """
    def __init__(self, shape=(128, 128)):
        self.shape = shape
        self.last_event = np.zeros(shape, dtype=aer_raw_event_dtype)
        self.last_event['timestamp'] = 0

    def filter(self, raw_event_sequence):
        pairs = aer_filter_pairs(raw_event_sequence, aer_raw_event_dtype)
        
        for le, e in pairs:
            fe = make_filtered(le, e)
            if fe['delta'] > 0:
                yield fe
                
                
def make_filtered(le, e):
    fe = np.zeros((), dtype=aer_filtered_event_dtype)
    fe['timestamp'] = e['timestamp']
    fe['x'] = e['x']
    fe['y'] = e['y']
    fe['sign'] = e['sign']
    fe['delta'] = e['timestamp'] - le['timestamp']
    fe['same'] = (e['sign'] == le['sign'])

    if fe['delta'] > 0:
        fe['frequency'] = 1.0 / fe['delta']
    else:
        fe['frequency'] = 0
    return fe

def aer_filter_successive(sequence):
    """ Creates a sequence of aer_filtered_events, by considering
        pairs of events and computing the frequency """
    return AER_Filter().filter(sequence)
