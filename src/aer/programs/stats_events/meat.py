import numpy as np
from aer.stats import aer_histogram
from aer.utils import md_argmax
from reprep import Report, scale
from aer.logs.load_aer_logs import aer_raw_events_from_file_all

def get_for_one(events, coords): 
    for_one = np.logical_and(events['x'] == coords[0],
                             events['y'] == coords[1])
    one = events[for_one]
    return one

def report_for_one(r, events, coords):
    f = r.figure(caption='For coordinate %s' % str(coords))
    h = aer_histogram(events).astype('float')
    h[coords[0], coords[1]] = np.nan
    
    one = get_for_one(events, coords)
    
    
    min_f = 20.0
    max_f = 5000.0
    min_d = 1.0 / max_f
    max_d = 1.0 / min_f 
   
    f.data_rgb('where', scale(h))
    
    if False:
        with f.plot('frequency') as pylab:
            fbins = np.linspace(min_f, max_f, 1000)
            pylab.hist(one['frequency'], bins=fbins)
            pylab.xlabel('1/interval (Hz)')
    
        with f.plot('delta') as pylab:
            dbins = (1.0 / fbins)[::-1]
            pylab.hist(one['delta'], bins=dbins)
            ticks = np.linspace(min_d, max_d, 10)
            labels = ['%d' % (x * 1000000) for x in ticks]
            pylab.xticks(ticks, labels)
            pylab.xlabel('interval (microseconds)')
            
    time = one['timestamp']
    time = time - time[0]
    
    with f.plot('history') as pylab:
        plus = one['sign'] == 1
        minus = one['sign'] == -1
        ones = np.ones(one.size)
        
        pylab.plot(time[plus], 1 * ones[plus], 'rs')
        pylab.plot(time[minus], -1 * ones[minus], 'bs')
        
        t0 = time[0]
        delta = 0.01
        pylab.axis((t0, t0 + delta, -1.2, 1.2)) 
    

def aer_stats_events_meat(log):
#    events = collect_all(aer_load_log_generic(log))
    events = aer_raw_events_from_file_all(log)
    hist = aer_histogram(events)
    _, coords = md_argmax(hist)

    r = Report('index')    
    with r.subsection('sub') as sub:
        report_for_one(sub, events, coords)
    return r

