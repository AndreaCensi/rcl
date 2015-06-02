from aer import aer_load_log_generic
from quickapp import QuickApp
from reprep import Report
import sys
from aer.filters.pipelines import collect_all
from aer.stats import aer_histogram
from quickapp.quick_app_base import QuickAppBase

def aer_simple_stats(log):
    events = collect_all(aer_load_log_generic(log))
    sign = events['sign']
    h_all = aer_histogram(events)
    h_plus = aer_histogram(events[sign == +1])
    h_minus = aer_histogram(events[sign == -1])

    return dict(h_all=h_all, h_plus=h_plus, h_minus=h_minus)

def aer_simple_stats_report(stats):
    r = Report('simplestatsreport')
    
    f = r.figure()
    for n in ['h_all', 'h_plus', 'h_minus']:
        h = stats[n]
        cap = '%d events' % (h.sum())
        r.data(n, h).display('scale').add_to(f, caption=cap)
    
    return r

class AERSimpleStats(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='AER log file')    
                            
    def define_jobs_context(self, context):
        options = self.get_options()
        stats = context.comp(aer_simple_stats, log=options.log)
        report = context.comp(aer_simple_stats_report, stats)
        context.add_report(report, 'rep1')
 
aer_simple_stats_main = AERSimpleStats.get_sys_main()
    
