from aer import aer_load_log_generic
from quickapp import QuickApp
from reprep import Report
import numpy as np
import sys

def aer_simple_stats(log):
    h = np.zeros((128, 128))

    count = 0    
    for e in aer_load_log_generic(log):
        print count, e
        h[e['x'], e['y']] += 1
        count += 1
         
    return dict(h=h)

def aer_simple_stats_report(stats):
    h = stats['h']
    r = Report('simplestatsreport')
    
    f = r.figure()
    r.data('histogram', h).display('scale').add_to(f)
    
    return r

class AERSimpleStats(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='AER log file', compulsory=True)    
                            
    def define_jobs(self):
        options = self.get_options()
        stats = self.comp(aer_simple_stats, log=options.log)
        report = self.comp(aer_simple_stats_report, stats)
        self.add_report(report, 'rep1')
 
def aer_simple_stats_main():
    sys.exit(AERSimpleStats().main())
    
