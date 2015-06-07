from aer.logs.chunks import aer_iterate_intervals
from aer.logs.load_aer_logs import (aer_raw_events_from_csv,
    aer_raw_events_from_file_all_faster)
from procgraph import BadConfig, Block
from procgraph.block_utils import IteratorGenerator
import os


__all__ = ['AERChunksStream']

class AERChunksStream(IteratorGenerator):
    ''' 
        Yields packets of AER events with the given interval.
    '''
    Block.alias('aer_chunk_stream')
    
    Block.config('filename', 'AEDAT Filename.')
    Block.config('interval', 'Interval')

    Block.output('events', 'Event stream')
    

    def init_iterator(self):
        filename = self.config.filename
        interval = self.config.interval
        
        if not os.path.exists(filename):
            msg = 'Not existent file %r.' % filename
            raise BadConfig(block=self, error=msg, config='filename')
        
        if 'events.txt' in filename:
            raw_events = aer_raw_events_from_csv(filename)
        else:
            raw_events = aer_raw_events_from_file_all_faster(filename)
#         for e in raw_events:
#             self.info('timestamp %r es %s %s' % (e['timestamp'], e['x'], e['y']))
            
        chunks = aer_iterate_intervals(raw_events, interval)
        for timestamp, es in chunks:
            yield 0, timestamp, es

