from . import logger, np
from reprep import Report
from aer.programs.stats_freq.meat import load_data  # XXX
from aer.programs.stats_freq.meat import compute_deltas  # XXX


def aer_stats_events_meat(log):
    logger.info('Loading data from %r' % log)
    data = load_data(log)
    logger.info('Found %s samples' % data.size)
    ignore_same = False
    fdata = compute_deltas(data, ignore_same=ignore_same, ignore_plus=True)
    logger.info('Found %s valid deltas' % fdata.size)
    logger.info('percentage same: %s ' % np.mean(fdata['same']))
    logger.info('filtered')
    
    T = data['timestamp'][-1] - data['timestamp'][0]
    logger.info('Delta: %s' % T)
    logger.info('Plotting...')
    
    r = Report('index')
    
    f = r.figure(cols=3)
    
    x = data['x']
    y = data['y']
     
    bins = (range(np.max(x)), range(np.max(y)))
    h, _, _ = np.histogram2d(x, y, bins=bins)
    
    a, b = np.where(h == np.max(h))
    im = a[0]
    jm = b[0] 

    
    min_f = 20.0
    max_f = 5000.0
    
    
    min_f = 800.0
    max_f = 1200.0
    
    min_d = 1.0 / max_f
    max_d = 1.0 / min_f 
    
    
    for_one = np.logical_and(fdata['x'] == im, fdata['y'] == jm)
    logger.info('For one: %d (%f)' % (np.sum(for_one), np.mean(for_one)))
     
    one = fdata[for_one]
    
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
        
    time = one['timestamp'] * 0.000001
    time = time - time[0]
    
    with f.plot('history') as pylab:
        plus = one['sign'] == 1
        minus = one['sign'] == 0        
        ones = np.ones(one.size)
        
        pylab.plot(time[plus], 1 * ones[plus], 'rs')
        pylab.plot(time[minus], 0 * ones[minus], 'bs')
        
        a = pylab.axis()
        t0 = time[0]
        delta = 0.01
        pylab.axis((t0, t0 + delta, -0.2, 1.2)) 
    
    return r

