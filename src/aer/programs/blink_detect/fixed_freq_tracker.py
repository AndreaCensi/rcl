import numpy as np

class TrackerFixedFreq():
    def __init__(self, freq, sigma, interval=None, shape=(128, 128)):
        self.frequency = freq
        
        self.start_frame = None
        self.accum = None
        
        self.shape = shape
        
        if interval is None:
            interval = 1.0 / freq
    
        self.interval = interval
        
        self.factors = [(+1, self.frequency, sigma)]             
            
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

#         print('dt %10.4f frequency: %10.2f' % (t - self.start_frame, f))

#         print('factors: %s' % self.factors)
        found = False
#         maxw = 0
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

#         print(t - (self.start_frame + self.interval), found)
        time_to_do_it = t > self.start_frame + self.interval
        reset = found and time_to_do_it
#         reset = time_to_do_it
        if reset:
            self.start_frame = t
            self.prev_accum = self.accum
            self.accum = np.zeros(self.shape, 'float')
            return self.prev_accum
        else:
            return None
        
