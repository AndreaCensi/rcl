from . import logger, np
from reprep import Report
from aer.filters.pipelines import aer_pipeline_transitions1_all


def aer_stats_freq_meat(log):
    fdata = aer_pipeline_transitions1_all(log, sign=(+1))
    x, y = fdata['x'], fdata['y']

    logger.info('percentage same: %s ' % np.mean(fdata['same']))
    logger.info('filtered')
    
    logger.info('Plotting...')
    
    r = Report('index')
    
    f = r.figure(cols=3)
    
    bins = (range(128), range(128))
    
    
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
    

    def show_heat(pylab, select=None):
        if select is None:
            xs, ys = x, y
        else:
            xs = x[select]
            ys = y[select]
            
        if xs.size:
            h, _, _ = np.histogram2d(xs, ys, bins=bins)
        else:
            h = np.zeros((128, 128))
        pylab.imshow(h)

    with f.plot('events') as pylab:
        show_heat(pylab)
         
    with f.plot('delta_raw') as pylab:
        pylab.hist(fdata['delta'], bins=1000)
    
    with f.plot('delta_s_clipped') as pylab:
        dbins = np.linspace(min_d, max_d, 1000)
        pylab.hist(delta_s, bins=dbins)

    with f.plot('freq') as pylab:
        fbins = np.linspace(min_f, max_f, 1000)
        pylab.hist(frequency, bins=fbins)
    
    f2 = r.figure(cols=2)
    
    with f2.plot('events_same') as pylab:
        select = fdata['same']
        
        show_heat(pylab, select)
        pylab.colorbar()
    
    with f2.plot('events_not_same') as pylab:
        select = np.logical_not(fdata['same'])
        show_heat(pylab, select)
        pylab.colorbar()
        
    return r
         
    
def compute_deltas(data, ignore_same=True, ignore_plus=False):
    n = data.size
    dtype = [('timestamp', 'int'), ('x', 'int'), ('y', 'int'), ('sign', 'int'),
             ('delta', 'float'), ('frequency', 'float'),
              ('valid', 'bool'), ('same', 'bool')]
    # copy fields we know
    fdata = np.zeros(n, dtype=dtype)
    fdata['x'][:] = data['x']
    fdata['y'][:] = data['y']
    fdata['timestamp'][:] = data['timestamp']
    fdata['sign'][:] = data['sign']
    
    x = data['x']
    y = data['y']
    timestamp = data['timestamp']
    # remember last event
    last = np.zeros((128, 128), 'int')
    last_sign = np.zeros((128, 128), 'int')
    last.fill(timestamp[0])
    delta = fdata['delta']
    frequency = fdata['frequency']
    valid = fdata['valid']
    sign = data['sign']
    same = fdata['same']
    
    for i in xrange(n):
        t = timestamp[i]
        
        if ignore_plus and sign[i] == 1:
            valid[i] = False
            continue
        
        l = last[x[i], y[i]]
        delta[i] = (t - l) * 0.000001
        frequency[i] = 1.0 / delta[i]
        
        is_same = sign[i] == last_sign[x[i], y[i]]
        if is_same and ignore_same:
            valid[i] = False
            continue
        else:
            pass 

        last[x[i], y[i]] = t        
        
        valid[i] = delta[i] > 0
        same[i] = is_same
        last_sign[x[i], y[i]] = sign[i]
        
    use = fdata['valid']  
    res = fdata[use]
    
    assert np.all(res['delta'] > 0)

    return res


def load_data(filename):
    dtype = [('timestamp', 'int'), ('x', 'int'), ('y', 'int'), ('sign', 'int')]
    return np.loadtxt(filename, dtype)

