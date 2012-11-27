from . import aer_filter_pairs, AER_pairs
from aer import aer_raw_event_dtype
from aer.filters.frequency import make_filtered

__all__ = ['aer_sign_transitions']

def aer_sign_transitions(raw_sequence, p2n=True, n2p=True):
    """ yields a sequence of filtered events """
    for e1, e2 in aer_filter_transitions2(raw_sequence, p2n=p2n, n2p=n2p):
        fe = make_filtered(e1, e2)
        if fe['delta'] > 0:
            yield fe

def aer_select_transitions(raw_sequence):
    """ Yields pairs of events happened at the same pixel """
    raw_pairs = aer_filter_pairs(raw_sequence, aer_raw_event_dtype)
    for e1, e2 in raw_pairs:
        # only get transitions
        if e1['sign'] != e2['sign']:
            yield e1, e2


def aer_filter_transitions2(raw_sequence, p2n, n2p):
    """ 
        Returns both -1 -> +1 and +1 --> -1 transitions.
        Yields pairs of raw_events.
    """
    # First, let's select all transitions successive pairs
    last_p2n = AER_pairs(aer_raw_event_dtype) 
    last_n2p = AER_pairs(aer_raw_event_dtype)
    for _, r2 in aer_select_transitions(raw_sequence):
        # now put them in a separate 
        if (r2['sign'] == -1) and p2n:
            last = last_p2n.get_last_event(r2)
            if last is not None:
                yield last, r2
            
        if (r2['sign'] == +1) and n2p:
            last = last_n2p.get_last_event(r2)
            if last is not None:
                yield last, r2

