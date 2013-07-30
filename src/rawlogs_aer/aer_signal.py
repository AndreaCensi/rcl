from contracts import contract
from rawlogs import RawSignal
import numpy as np



__all__ = ['AERSignal']


class AERSignal(RawSignal):
    
    def __init__(self, filename, time_reference='dvs', annotations='dict'):
        self.filename = filename
        self.time_reference = time_reference
        self.annotations = annotations
        
        self.read_file = False
        
    def get_signal_type(self):
        from aer.types import aer_raw_event_dtype
        return np.dtype(aer_raw_event_dtype)

    def get_time_reference(self):
        return self.time_reference

    def get_resources(self):
        return [self.filename]
    
    def get_annotations(self):
        return self.annotations

    def _read_data(self):
        if self.read_file:
            return
        
        from aer.logs import aer_raw_events_from_file_all_faster
        
        self.data = aer_raw_events_from_file_all_faster(self.filename, limit=None)
        
        if False:
            from aer.logs import aer_raw_events_from_file_all
            data1 = aer_raw_events_from_file_all(self.filename, limit=None)
            
            for i in xrange(self.data.size):
                d1 = data1[i]
                d2 = self.data[i]
                print d1
                print d2
            
        self.read_file = True
        
    def get_time_bounds(self):
        self._read_data()
        t0 = self.data[0]['timestamp']
        t1 = self.data[-1]['timestamp']
        return (t0, t1)
    
    def read(self, start=None, stop=None):
        self._read_data()
        # print('reading stream %s %s' % (self.data.shape, self.data.dtype))
        for i in xrange(self.data.size):
            e = self.data[i]
            t = e['timestamp']
            if (start is None or t >= start) and (stop is None or t <= stop):
                yield t, ('aer', e)  # RawSignalData('aer', t, e) 
            if (stop is not None) and (t > stop):
                break

    @contract(interval='>0')
    def read_packets(self, interval, start=None, stop=None):
        """ Read events in packets with the given interval """
        self._read_data()
        # print('reading stream %s %s' % (self.data.shape, self.data.dtype))
        E = self.data
        T = E['timestamp']
        
        T0 = T[0]
        if start is not None:
            T0 = max(T0, start)
        T1 = T[-1]
        if stop is not None:
            T1 = min(T1, stop)
        
        n = int(np.ceil((T1 - T0) / interval)) 

        for i in range(n):
            t0 = T[0] + i * interval
            t1 = t0 + interval
            sel = np.logical_and(T >= t0, T < t1)
            Es = E[sel]
            yield t1, ('aer', Es)  # RawSignalData('aer', t1, Es)
            
#             
#               
#         
#         stop = start + 1
#         while stop <= n - 1:
#             delta = T[stop] - T[start]
#             if delta > interval:
#                 es = E[start:stop]
#                 
#                 start = stop
#                 stop = start + 1 
#             
#             stop += 1
