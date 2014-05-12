''' 
    This is a set of blocks to read and display AER_ data.
    
    .. _AER: http://sourceforge.net/apps/trac/jaer/wiki

'''

from procgraph import import_succesful, import_magic

procgraph_info = {
    # List of python packages 
    'requires': ['aer']
}

aer = import_magic(__name__, 'aer')

if import_succesful(aer):
    from .aer_raw_stream import *
    from .aer_events_histograms import *
    from .aer_chunks_stream import *

# load models
from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)


