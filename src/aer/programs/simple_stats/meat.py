from aer.logs.load_aer_logs import aer_raw_events_from_file_all, \
    aer_raw_events_from_file_all_faster
from aer.stats import aer_histogram
from quickapp import QuickApp
from reprep import Report


def aer_simple_stats(log):
    events = aer_raw_events_from_file_all_faster(log)
    sign = events['sign']
    print('histogram')
    h_all = aer_histogram(events)
    print('histogram +')
    h_plus = aer_histogram(events[sign == +1])
    print('histogram -')
    h_minus = aer_histogram(events[sign == -1])

    return dict(h_all=h_all, h_plus=h_plus, h_minus=h_minus)

def aer_simple_stats_report(stats):
    r = Report()
    
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
    
