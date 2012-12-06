import numpy as np

class TrackerFixedFreq():
    def __init__(self, freq, others, others_weight, sigma,
                        interval=None, shape=(128, 128)):
        print('freq: %s  others: %s' % (freq, others))
        self.frequency = freq
        
        self.start_frame = None
        self.accum = None
        
        self.shape = shape
        
        if interval is None:
            interval = 1.0 / freq
    
        self.interval = interval
        
        self.factors = [(others_weight, fo, sigma) for fo in others] + \
                     [(+1, self.frequency, sigma)]
            
        self.prev_accum = None
        
    def __repr__(self):
        return 'Tracker(%6d, %4.2fms)' % (self.frequency, 1000 * self.interval)
        
    def has_frame(self):
        """ Return true if at least one frame is finished """
        return self.prev_accum is not None
     
    def get_accum(self):
        return self.prev_accum.copy()
            
    def integrate(self, aer_filtered_event):
        """ Returns either None or a numpy array if done """
        e = aer_filtered_event
        t = e['timestamp']
        if self.start_frame is None:
            self.start_frame = t
            self.accum = np.zeros(self.shape, 'float')

        f = e['frequency']
        found = False
        for alpha, freq, sigma in self.factors:
            df = np.abs(f - freq)
            if df / sigma > 6:
                continue
            else:
                if alpha > 0:
                    # found one event good
                    found = True
            w = alpha * np.exp(-(df / sigma) ** 2)
        
            self.accum[e['x'], e['y']] += w

        if found and t > self.start_frame + self.interval:
            self.start_frame = t
            self.prev_accum = self.accum
            self.accum = np.zeros(self.shape, 'float')
            return self.prev_accum
        else:
            return None
        
