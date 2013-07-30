from .aer_signal import AERSignal
from rawlogs.library import LogWithAnnotations
from contracts import contract


__all__ = ['AERLog']


class AERLog(LogWithAnnotations):    
    
    @contract(filename='str', interval='None|>0', annotations='dict')
    def __init__(self, filename, interval=None, annotations={}):
        """
            If interval is not None, the logs are read in packets of the 
            given interval.
        """
        LogWithAnnotations.__init__(self, annotations)
        
        self.interval = interval
        self.filename = filename
        self.signal = AERSignal(self.filename)
        
    def get_signals(self):
        return dict(aer=self.signal)

    def get_time_bounds(self):
        return self.signal.get_time_bounds()
    
    def get_resources(self): 
        return [self.filename]

    def read(self, topics, start=None, stop=None):
        if 'aer' in topics:
            if self.interval is not None:
                it = self.signal.read_packets(interval=self.interval, start=start, stop=stop)
            else:
                it = self.signal.read(start=start, stop=stop)
            for x in it:
                yield x
        else:
            print('no aer signal required in %s' % topics)
