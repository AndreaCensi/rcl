from procgraph import pg
from quickapp import QuickApp
import sys

class AERTrackerPlotApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("tracks", help='source file', compulsory=True)    
        params.add_int("width", default=128 * 3)    
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_tracker_plot, options.tracks, options.width)        
        
def aer_tracker_plot(tracks, width):
    config = dict(log=tracks, width=width)
    pg('aer_track_plot', config)

def aer_tracker_plot_main():
    sys.exit(AERTrackerPlotApp().main())
        
__all__ = ['aer_tracker_plot_main']
