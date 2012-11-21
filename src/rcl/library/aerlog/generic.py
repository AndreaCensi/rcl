from . import aer_raw_events_from_file, aer_raw_sequence


def load_aer_generic(filename):
    if '.aer.txt' in filename:
        raw_events = aer_raw_sequence(open(filename))
    else:
        raw_events = aer_raw_events_from_file(filename)
    return raw_events
