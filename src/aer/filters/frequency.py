from . import np, AER_pairs
from aer import aer_raw_event_dtype, aer_filtered_event_dtype


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

