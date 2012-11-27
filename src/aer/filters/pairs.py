from . import np

__all__ = ['aer_filter_pairs', 'AER_pairs']

class AER_pairs(object):
    """ Remembers pairs of events """
    def __init__(self, dtype, shape=(128, 128)):
        self.last = np.zeros(shape, dtype=dtype)
        self.last['timestamp'] = 0
    
    def get_pairs(self, seq):
        for e in seq:
            le = self.get_last_event(e)
            if le is not None:
                yield le, e.copy()
            
    def get_last_event(self, e):
        """ return the last event, or none """
        x, y = e['x'], e['y']
        le = self.last[x, y].copy()
        self.last[x, y] = e     
        if le['timestamp'] > 0:
            return le.copy()
        else:
            return None    
        
        

def aer_filter_pairs(seq, dtype):
    """ Yields pairs of successive events happened at the same pixel. """
    return AER_pairs(dtype).get_pairs(seq)
