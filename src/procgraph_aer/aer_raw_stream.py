from procgraph import Block, BadConfig
from procgraph.block_utils import IteratorGenerator
from rcl.library.filters import aer_raw_relative_timestamp
import os
from rcl.library.aerlog import load_aer_generic


class AERRawStream(IteratorGenerator):
    ''' 

    '''
    Block.alias('aer_raw_stream')
    Block.config('filename', 'File.')
    
    Block.output('events', 'Event stream')

    def get_iterator(self):
        filename = self.config.filename
        if not os.path.exists(filename):
            raise BadConfig(self, 'Not existent file %r.' % filename,
                            'filename')
    
        raw_events = load_aer_generic(filename)
    
        events2 = aer_raw_relative_timestamp(raw_events)
        for e in events2:
            yield 0, e['timestamp'], e
    
