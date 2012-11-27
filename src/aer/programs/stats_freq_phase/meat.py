from aer.filters import aer_filtered_cutoff, aer_pipeline_transitions1_all
from reprep import Report
import numpy as np

 
def filter_phase(log, pipeline, f_min, f_max, fd, pd, n_stop=0):
    transitions = aer_pipeline_transitions1_all(log, pipeline)
    stream = aer_filtered_cutoff(transitions, f_min, f_max)
    
    P = np.zeros((fd, pd))
    frequencies = np.linspace(f_min, f_max, fd)
    phases = np.linspace(0, 1, pd)
    
    count = 0
    for ae in stream:
        f = ae['frequency']
        t = ae['timestamp']
        delta = 1 / f
        s = t / delta
        phase = s - np.floor(s)
        i = np.digitize([f], frequencies) - 1
        j = np.digitize([phase], phases) - 1
        P[i, j] += 1
    
        count += 1
        if n_stop != 0 and count >= n_stop:
            break
            
    stats = {}
    stats['P'] = P
    return stats

def filter_phase_report(stats):
    P = stats['P']
    
    r = Report('unknown')
    f = r.figure()
    r.data('P', P.T).display('scale').add_to(f)
    
    return r    
    
