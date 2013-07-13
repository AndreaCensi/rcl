from rawlogs import RawLog
from .aer_signal import AERSignal


__all__ = ['AERLog']


class AERLog(RawLog):    
    
    def __init__(self, filename, annotations):
        self.filename = filename
        self.signal = AERSignal(self.filename)
        self.annotations = annotations
    
    def get_signals(self):
        return dict(aer=self.signal)

    def get_time_bounds(self):
        return self.signal.get_time_bounds()
    
    def get_resources(self): 
        return [self.filename]

    def read(self, topics, start=None, stop=None):
        for x in self.signal.read(topics, start, stop):
            yield x
                
    def get_annotations(self):
        return self.annotations
    