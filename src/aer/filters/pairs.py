from . import np

class AER_pairs(object):
    """ Remembers pairs of events """
    def __init__(self, dtype, shape=(128, 128)):
        self.last = np.zeros(shape, dtype=dtype)
        self.last['timestamp'] = 0
    
    def get_pairs(self, seq):
        for e in seq:
            x, y = e['x'], e['y']
            le = self.last[x, y]        
            # Ignore if we did not trigger
            if le['timestamp'] > 0:    
                yield le.copy(), e.copy()
            self.last[x, y] = e  
