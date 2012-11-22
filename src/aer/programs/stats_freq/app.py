from . import aer_stats_freq_meat
from quickapp import QuickApp
import sys

class AERStatsFreqApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)    
                            
    def define_jobs(self):
        options = self.get_options()
        report = self.comp(aer_stats_freq_meat, options.log, sign=(-1))        
        self.add_report(report, 'rep1')
 

def aer_stats_freq_main():
    sys.exit(AERStatsFreqApp().main())
    
