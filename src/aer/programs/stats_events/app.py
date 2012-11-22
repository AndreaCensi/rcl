from . import aer_stats_events_meat
from quickapp import QuickApp
import sys

class AERStatsEventsApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)    
                            
    def define_jobs(self):
        options = self.get_options()
        report = self.comp(aer_stats_events_meat, options.log)        
        self.add_report(report, 'rep1')
 

def aer_stats_events_main():
    sys.exit(AERStatsEventsApp().main())
    
