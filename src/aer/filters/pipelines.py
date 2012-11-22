from . import aer_raw_relative_timestamp, logger
from aer.filters.frequency import AER_Filter
from aer.filters.transitions import AER_Transitions_Filter
import numpy as np
from aer.logs.generic import aer_load_log_generic

def aer_pipeline_transitions1(raw_sequence, sign):
    """ Iterates over transitions events """
    raw_sequence = aer_raw_relative_timestamp(raw_sequence)
    filtered = AER_Filter().filter(raw_sequence)
    transitions = AER_Transitions_Filter(sign=sign).get_transitions(filtered)
    return transitions

def aer_pipeline_transitions1_all(filename, sign):
    """ Returns all events in a numpy array """
    logger.info('Opening file %s' % filename)
    raw_sequence = aer_load_log_generic(filename)
    filtered = aer_pipeline_transitions1(raw_sequence, sign)
    return collect_all(filtered)


def collect_all(sequence):
    logger.info('Reading all events...')
    l = list(sequence)
    logger.info('... read %d events.' % len(l))
    return np.array(l, dtype=l[0].dtype)
