from procgraph import pg
from quickapp import QuickApp
import sys

class AERParticlesPlotApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("tracks", help='source file', compulsory=True)    
        params.add_int("width", default=128 * 3)    
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_particles_plot,
                  tracks=options.tracks,
                  width=options.width)        
        
def aer_particles_plot(tracks, width):
    config = dict(log=tracks, width=width)
    pg('aer_particles_plot', config)
    
def aer_particles_plot_main():
    sys.exit(AERParticlesPlotApp().main())
    
