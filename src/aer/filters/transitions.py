from . import aer_filter_pairs
from .. import aer_filtered_event_dtype

__all__ = ['aer_filter_transitions']

def aer_transitions_and_sign(events, sign):
    for e in events:
        # only get transitions
        if sign == e['sign'] and not e['same']:
            yield e


class AER_Transitions_Filter(object):
    """ Remembers the transitions """
    def __init__(self, sign=(-1)):
        self.sign = sign

    def get_transitions(self, filtered_event_sequence):
        """ Yields pairs of events. """
        transitions = aer_transitions_and_sign(filtered_event_sequence, self.sign)
        pairs = aer_filter_pairs(aer_filtered_event_dtype, transitions)
        for e1, e2 in pairs:
            e = e2.copy()
            e['delta'] = e2['timestamp'] - e1['timestamp']
            e['frequency'] = 1.0 / e['delta']
            yield e
            
def aer_filter_transitions(events, sign):
    f = AER_Transitions_Filter(sign)
    return f.get_transitions(events)
