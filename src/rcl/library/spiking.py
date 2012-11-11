from . import np, contract

__all__ = ['SpikingSensor', 'event_dtype']


event_dtype = np.dtype([('timestamp', 'float'),
               ('index', 'int'),
               ('sign', 'int'),
               ('value', 'float')])

class SpikingSensor(object):
    """ A class that simulates a spiking retina. """
    
    @contract(threshold='>0')
    def __init__(self, threshold):
        self.threshold = threshold
        self.last_timestamp = None
        self.last_levels = None
    
    @contract(timestamp='float', observations='array[N]',
              returns='list(array)')
    def push(self, timestamp, observations):
        """ Returns a possibly empty list of events. Each event is described
            by a timestamp, an index, and a positive/negative sign.
        """
            
        observations = np.array(observations)
             
        if self.last_timestamp is None:
            # First time
            self.last_timestamp = timestamp
            self.last_levels = observations
            return []
        
        diff = observations - self.last_levels
        
        events = []
        for i in range(len(diff)):
            if np.abs(diff[i]) >= self.threshold:
                sign = np.sign(diff[i])
                event = np.array((timestamp, i, int(sign), observations[i]),
                                 dtype=event_dtype)
                events.append(event) 
                self.last_levels[i] = observations[i]
                
        return events
