import numpy as np
import os
import yaml
from contracts import contract
from aer import logger

AER_BLINK_CONF = 'aer_blink_conf.yaml'

class BlinkLED(object):
    @contract(frequency='float|int,>0', position='list[3](number)|array[3]')
    def __init__(self, frequency, position):
        self.frequency = float(frequency)
        self.position = np.array(position, dtype='float')
    
    def get_frequency(self):
        return self.frequency
        
class BlinkDetectConfig(object):
    def __init__(self, id_log, log, geometry, desc=None):
        self.id_log = id_log
        self.log = log
        self.desc = desc
        leds_conf = geometry['leds']
        self.leds = []
        for x in leds_conf:
            l = BlinkLED(**x)
            self.leds.append(l)
        
    @contract(returns='list[>=1](number,>0)')
    def get_frequencies(self):
        return [x.get_frequency() for x in self.leds]
    
    def get_desc(self):
        return self.desc
    
    def get_log(self):
        return self.log


def get_blink_config(log):
    """ Reads the file "aer_blink_conf.yaml" """

    options = []

    dirname = os.path.dirname(log)
    confname = os.path.join(dirname, AER_BLINK_CONF)
    options.append(confname)

    options.append(AER_BLINK_CONF)

    for o in options:
        if os.path.exists(o):
            logger.info('Using configuration %r.' % o)
            break
        else:
            logger.warning('Could not find %r.' % o)

    else:
        msg = 'No valid configuration found: %s' % options
        raise ValueError(msg)

    conf = yaml.load(open(o).read())
    if not isinstance(conf, dict):
        msg = 'Expected a dictionary in %r' % conf
        raise ValueError(msg)
    basename = os.path.basename(log)
    while '.' in basename:
        basename = os.path.splitext(basename)[0]
    if not basename in conf:
        msg = 'Could not find entry %r in %r' % (basename, conf.keys())
        raise ValueError(msg)
    log_conf = conf[basename]
    logger.info('Using log configuration %r' % log_conf)
    
    return BlinkDetectConfig(id_log=basename, log=log, **log_conf)
