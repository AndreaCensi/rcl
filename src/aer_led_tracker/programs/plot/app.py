from . import aer_tracker_plot
from quickapp import QuickApp
import sys

class AERTrackerPlotApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("tracks", help='source file', compulsory=True)    
        params.add_int("width", default=128 * 3)    
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_tracker_plot, options.tracks, options.width)        
        

def aer_tracker_plot_main():
    sys.exit(AERTrackerPlotApp().main())
    
