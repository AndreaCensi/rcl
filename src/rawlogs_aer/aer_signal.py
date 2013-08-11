from aer.logs import aedat_info_cached
from contracts import contract
from numpy.testing.utils import assert_allclose
from rawlogs import RawSignal
import numpy as np
from aer.logs.chunks import check_good_chunks, get_chunks_linear
from numpy.ma.core import allclose


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
            
            for i in xrange(0, self.data.size, 100):
                d1 = data1[i]
                d2 = self.data[i]
                print i, d1, d2
                assert_allclose(d1, d2)
                # print d1
                # print d2
            
        self.read_file = True
        
    def get_time_bounds(self):
        info = aedat_info_cached(self.filename)
        return info['start'], info['end']
    
    def read(self, start=None, stop=None):
        self._read_data()
        print('reading stream %s %s' % (self.data.shape, self.data.dtype))
        print('Start= %s; stop= %s' % (start, stop))
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
        one = (start is not None) or (stop is not None)
        both = (start is not None) and (stop is not None)
        if one and not both:
            msg = 'Specify none or both start and stop.'
            raise ValueError(msg)
        if one:
            if not start <= stop:
                msg = 'Wrong interval: %s, %s' % (start, stop)
                raise ValueError(msg)
            
        self._read_data()
        print('Start= %s; stop= %s interval= %s' % (start, stop, interval))

        E = self.data
        T = E['timestamp']
        
        T0 = T[0]
        T1 = T[-1]
        
        if T0 > T1:
            raise Exception('weird data: %s %s' % (T0, T1))
        
        if ((start is not None) and (T1 < start)):
            # no data at all
            msg = 'start>=T1: Start: %s Stop: %s. Log is %s - %s' % (start, stop, T0, T1)
            raise Exception(msg)
        if  ((stop is not None) and (T0 > stop)):
            msg = 'stop<=T0: Start: %s Stop: %s. Log is %s - %s' % (start, stop, T0, T1)
            raise Exception(msg)
             
        if start is not None:
            T0 = max(T0, start)
        else:
            start = T0
            
        if stop is not None:
            T1 = min(T1, stop)
        else:
            stop = T1
        
        assert T0 <= T1
        
        chunks = list(get_chunks_linear(T, T0, T1, interval))
        check_good_chunks(T, T0, T1, interval, chunks)

        if not chunks:
            raise Exception('weird data')
        
        print('start: %s stop: %s' % (start, stop))
        print('Reading %d chunks from %s to %s (log is %s to %s)' % (len(chunks), T0, T1, T[0], T[-1]))
        
        npackets = 0
        for i, (a, b) in enumerate(chunks):
            t0 = T0 + i * interval
            t1 = t0 + interval
            
            Es = E[a:b + 1]
            e_t0 = Es['timestamp'][0]
            e_t1 = Es['timestamp'][-1]
            
            msg = ('chunk[i-1] %s chunk[i] %s chunk[i+1] %s' % (chunks[i - 1] if i > 0 else None,
                                                                 chunks[i], chunks[i + 1] if i < len(chunks) else None)) 
            msg += '\nstart %s t0 %s e_t0 %s e_t1 %s t1 %s stop %s' % (start, t0, e_t0, e_t1, t1, stop)
            
            assert_lte(t0, e_t0, msg)
            assert_lte(e_t0, e_t1, msg)
            assert_lte(e_t1, t1, msg)
            
            assert_lte(start, e_t0, msg)
            assert_lte(e_t0, e_t1, msg)
            assert_lte(e_t1, stop, msg)
            
            yield e_t1, ('aer', Es)  
            npackets += 1
            
        if npackets == 0:
            msg = 'Probably a bug or very weird data: no packets sent?'
            raise Exception(msg)
            
def assert_lte(a, b, msg):
    good = allclose(a, b) or a <= b
    if not good:
        raise ValueError(msg + '(%s <= %s)' % (a, b))
    
    
    
