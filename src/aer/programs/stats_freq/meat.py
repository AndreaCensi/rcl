from reprep import Report
from aer.filters import aer_pipeline_transitions1_all
from aer.stats import aer_histogram
import numpy as np
from aer import logger

def aer_stats_freq_meat(log, pipeline):
    events = aer_pipeline_transitions1_all(log, pipeline)
    
    r = Report('index')
        
    with r.subsection('all') as sub:
        report_band(sub, events, min_f=20.0, max_f=3000.0)

    with r.subsection('high') as sub:
        report_band(sub, events, min_f=500.0, max_f=3000.0)
            
    return r
    
    
def report_band(r, events, min_f, max_f):
    valid = np.logical_and(events['frequency'] > min_f, events['frequency'] < max_f)
    nvalid = np.sum(valid)
    sel_events = events[valid]
    caption = ('Found %s (%s%%) events in the frequency range (%s, %s)' 
               % (nvalid, np.mean(valid) * 100, min_f, max_f))
    logger.info(caption) 
    f = r.figure(caption=caption, cols=2)

    with f.plot('events') as pylab:
        show_heat(pylab, sel_events)
    
    with f.plot('freq') as pylab:
        fbins = np.linspace(min_f, max_f, 1000)
        pylab.hist(sel_events['frequency'], bins=fbins)

#    if False:     
#        min_d = 1.0 / max_f
#        max_d = 1.0 / min_f
#
#        print('deltaraw')
#        with f.plot('delta_raw') as pylab:
#            pylab.hist(fdata['delta'], bins=1000)
#            delta_s = delta_s[valid]
#
#        print('deltas_clipped')
#        with f.plot('delta_s_clipped') as pylab:
#            dbins = np.linspace(min_d, max_d, 1000)
#            pylab.hist(delta_s, bins=dbins)
#    
#    print('done')      
 
def show_heat(pylab, events):
    if events.size > 0:
        h = aer_histogram(events)
    else:
        h = np.zeros((128, 128))
    pylab.imshow(h)
