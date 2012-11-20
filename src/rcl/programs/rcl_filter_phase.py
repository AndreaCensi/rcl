from rcl.library.event_text_log_reader import (aer_raw_sequence,
    aer_raw_only_minus, aer_raw_relative_timestamp, AER_Filter, aer_filtered_cutoff)
from reprep import Report
import numpy as np
from quickapp import QuickApp

def get_event_stream(filename, f_min, f_max):
    line_stream = open(filename)
    raw_sequence = aer_raw_sequence(line_stream)
    raw_sequence = aer_raw_only_minus(raw_sequence)
    raw_sequence = aer_raw_relative_timestamp(raw_sequence)
    aer_filter = AER_Filter()
    filtered = aer_filter.filter(raw_sequence)
    cutoff = aer_filtered_cutoff(filtered, f_min, f_max)
    return cutoff
    

def filter_phase(log, f_min, f_max, fd, pd, n_stop=0):
    stream = get_event_stream(log, f_min, f_max)
    
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
            
    # returns statistics
    stats = {}
    stats['P'] = P
    return stats

def filter_phase_report(stats):
    P = stats['P']
    
    r = Report('unknown')
    f = r.figure()
    r.data('P', P).display('scale').add_to(f)
    
    return r    
    
class RCLFilterPhaseApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)    
        params.add_int("fd", default=1000, help='frequency discretization')
        params.add_int("pd", default=100, help="phase discretization")
        params.add_float("f_min", default=100)
        params.add_float("f_max", default=2000)
        params.add_int("n_stop", help="Number of events to consider. 0 = all",
                                default=0)
                            
    def define_jobs(self):
        options = self.get_options()
        stats = self.comp(filter_phase, log=options.log,
                          f_min=options.f_min,
                          f_max=options.f_max,
                          fd=options.fd,
                          pd=options.pd,
                          n_stop=options.n_stop)

        report = self.comp(filter_phase_report, stats)
        
        self.add_report(report, 'rep1')
 
def main():
    RCLFilterPhaseApp().main()
    
