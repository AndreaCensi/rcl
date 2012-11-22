
def aer_raw_relative_timestamp(aer_raw_seq):
    """ Lets the first timestamp be 0 """
    t0 = None
    for e in aer_raw_seq:
        if t0 is None:
            t0 = float(e['timestamp'])
        e['timestamp'] -= t0
        yield e
