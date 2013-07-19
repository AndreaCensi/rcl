

def aer_raw_only_middle(seq, xmin, xmax, ymin, ymax):
    """ Selects the events only in the middle of the image """
    for e in seq:
        if (xmin <= e['x'] <= xmax) and (ymin <= e['y'] <= ymax):
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
    

    
