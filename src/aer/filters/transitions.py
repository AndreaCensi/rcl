from . import AER_pairs
from .. import aer_filtered_event_dtype

__all__ = ['aer_filter_transitions']

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
            
def aer_filter_transitions(events, sign):
    f = AER_Transitions_Filter(sign)
    return f.get_transitions(events)
