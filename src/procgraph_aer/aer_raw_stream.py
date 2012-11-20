from conf_tools import BadConfig
from procgraph import Block
import os
from procgraph.block_utils import IteratorGenerator
from rcl.library.aerlog.load_aer_logs import aer_raw_events_from_file
from rcl.library.event_text_log_reader import aer_raw_sequence

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
    
        if '.aer.txt' in filename:
            raw_events = aer_raw_sequence(open(filename))
        else:
            raw_events = aer_raw_events_from_file(filename)
    
        for e in raw_events:
            yield 'events', e['timestamp'], e
    
