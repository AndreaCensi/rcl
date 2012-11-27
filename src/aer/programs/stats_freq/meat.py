from . import logger, np
from reprep import Report
from aer.filters import aer_pipeline_transitions1_all
from aer.stats import aer_histogram

def aer_stats_freq_meat(log, pipeline):
    fdata = aer_pipeline_transitions1_all(log, pipeline)
    
    r = Report('index')
    
    f = r.figure(cols=3)
    
    min_f = 20.0
    max_f = 3000.0
    min_d = 1.0 / max_f
    max_d = 1.0 / min_f
    
    delta_s = fdata['delta'] 
    frequency = 1.0 / delta_s 
    
    valid = np.logical_and(frequency > min_f, frequency < max_f)
    
    logger.info('Valid: %s' % (np.mean(valid) * 100))
    frequency = frequency[valid]
    delta_s = delta_s[valid]

    def show_heat(pylab, events):
        if events.size > 0:
            h = aer_histogram(events)
        else:
            h = np.zeros((128, 128))
        pylab.imshow(h)

    print('events')
    with f.plot('events') as pylab:
        show_heat(pylab, fdata)
    
    print('freq')
    with f.plot('freq') as pylab:
        fbins = np.linspace(min_f, max_f, 1000)
        pylab.hist(frequency, bins=fbins)

    if False:     
        print('deltaraw')
        with f.plot('delta_raw') as pylab:
            pylab.hist(fdata['delta'], bins=1000)
        
        print('deltas_clipped')
        with f.plot('delta_s_clipped') as pylab:
            dbins = np.linspace(min_d, max_d, 1000)
            pylab.hist(delta_s, bins=dbins)
    
    print('done') 
    
    return r
         
     
