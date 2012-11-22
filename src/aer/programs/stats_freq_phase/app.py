import sys
from quickapp import QuickApp
from . import filter_phase, filter_phase_report
 
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
 
def aer_stats_freq_phase_main():
    sys.exit(RCLFilterPhaseApp().main())
    
