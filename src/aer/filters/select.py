
   
def aer_raw_only_minus(aer_raw_seq):
    """ Only yields minus events """
    for e in aer_raw_seq:
        if e['sign'] == -1:
            yield e


def aer_filtered_cutoff(aer_filtered_seq, min_frequency, max_frequency):
    for e in aer_filtered_seq:
        if min_frequency <= e['frequency'] <= max_frequency:
            yield e
    

    
