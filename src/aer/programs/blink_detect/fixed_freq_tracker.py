import numpy as np

class TrackerFixedFreq():
    def __init__(self, freq, sigma, interval=None, shape=(128, 128)):
        self.freq = freq
        self.sigma = sigma
        
        self.start_frame = None
        self.accum = None
        
        self.shape = shape
        
        if interval is None:
            interval = 1.0 / freq
    
        self.interval = interval
        
    def integrate(self, aer_filtered_event):
        """ Returns either None or a numpy array if done """
        e = aer_filtered_event
        t = e['timestamp']
        f = e['frequency']
        df = np.abs(f - self.freq)
        if df / self.sigma > 4: 
            return  
        
        if self.start_frame is None:
            self.start_frame = t
            self.accum = np.zeros(self.shape, 'float32')
        
        w = np.exp(-(df / self.sigma) ** 2)
        
        self.accum[e['x'], e['y']] += w

        if t > self.start_frame + self.interval:
            self.start_frame = t
            current = self.accum
            self.accum = np.zeros(self.shape, 'float32')
            return current
        else:
            return None
        
