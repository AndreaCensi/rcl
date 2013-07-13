from rawlogs import RawSignal
import numpy as np


__all__ = ['AERSignal']


class AERSignal(RawSignal):
    
    def __init__(self, filename, time_reference='dvs', annotations='dict'):
        self.filename = filename
        self.time_reference = time_reference
        self.annotations = annotations
        
        self.read = False
        
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
        if self.read:
            return
        
        from aer.logs import aer_raw_events_from_file_all
        self.data = aer_raw_events_from_file_all(self.filename, limit=None)
        
        self.read = True
        
    def get_time_bounds(self):
        self._read_data()
        t0 = self.data[0]['timestamp']
        t1 = self.data[-1]['timestamp']
        return (t0, t1)
    
    def read(self, start=None, stop=None):
        self._read_data()
        for e in self.data:
            t = e['timestamp']
            if t >= start and t <= stop: 
                yield e
            if t > stop:
                break
