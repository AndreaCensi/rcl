from . import logger, np
from ..utils import wrap_script_entry_point
from optparse import OptionParser
import os
from reprep import Report


def rcl_demo_plots(args):
    parser = OptionParser(usage="")
    parser.disable_interspersed_args()

    
    parser.add_option("--outdir", "-o", default='rcl_demo_vehicles',
                    help="output directory [%default]")
    
    (options, args) = parser.parse_args()
    
    if args:
        raise Exception()
    
    
    data = load_data(options.outdir)
    
    print data
    
    r = Report('index')
    
    f = r.figure()
    y = data['observations']
    events = data['events']
    events['timestamp'] -= events['timestamp'][0]
    
    f.data('y', y.T).display('scale').add_to(f)
    
    with f.plot('events') as pylab:
        pos = events['sign'] == 1
        neg = events['sign'] == -1
    
        pylab.plot(events['timestamp'][pos], events['index'][pos], 'rs')
        pylab.plot(events['timestamp'][neg], events['index'][neg], 'bs')
        
    
    rf = os.path.join(options.outdir, 'report.html')
    logger.info('Writing to %r' % rf)
    r.to_html(rf)
    
    
def load_data(dirname):
    events_log = os.path.join(dirname, 'events.txt')
    obs_log = os.path.join(dirname, 'observations.txt')
    
    res = {}
    res['observations'] = np.loadtxt(obs_log)
    res['events'] = np.loadtxt(events_log,
     dtype={'names': ('timestamp', 'index', 'sign'),
                      'formats': ('float', 'i', 'i')})
    return res


def main():
    wrap_script_entry_point(rcl_demo_plots, logger)
