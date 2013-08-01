import os
from aer import logger
import yaml
from contracts import contract
from aer.logs.load_aer_logs import aer_raw_events_from_file_all_faster


__all__ = ['aedat_info_cached', 'aedat_info']

def aedat_info(filename):
    """ 
        Returns dictionary with:
        - "start" timestamp (seconds) start
        - "end" timestamp (seconds) start
        - "duration": end-start
        - "nevents" number of events
        
    """
    events = aer_raw_events_from_file_all_faster(filename)
    start = events['timestamp'][0]
    end = events['timestamp'][-1]
    duration = end - start
    nevents = events.size
    return dict(duration=duration, start=start, nevents=nevents, end=end)
    

@contract(returns='dict')
def aedat_info_cached(filename):
    """ Caches the result in a file <filename>.info.yaml. """
    cache = filename + '.info.yaml'
    if os.path.exists(cache):
        logger.debug('Reading from cache: %s' % cache)
        with open(cache) as f:
            cached = yaml.load(f)
            if not isinstance(cached, dict):
                logger.debug('Invalid cache: %s' % cached)
                os.unlink(cache)
                return aedat_info_cached(filename)
            return cached
    else:
        result = aedat_info(filename)
        with open(cache, 'w') as f:
            yaml.dump(result, f)
        return result
