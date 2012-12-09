from procgraph import pg
from quickapp import QuickApp
import sys

class AERResolverPlotApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("tracks", help='source file', compulsory=True)    
        params.add_int("width", default=128 * 3)    
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_resolver_plot,
                  tracks=options.tracks,
                  width=options.width)        
        
def aer_resolver_plot(tracks, width):
    config = dict(log=tracks, width=width)
    pg('aer_resolver_plot', config)
    
def aer_resolver_plot_main():
    sys.exit(AERResolverPlotApp().main())
    
