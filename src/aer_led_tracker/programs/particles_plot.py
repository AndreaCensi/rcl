from procgraph import pg
from quickapp import QuickApp
import sys
import os

class AERParticlesPlotApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("tracks", help='source file', compulsory=True)    
        params.add_int("width", default=int(128 * 2.3))    
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_particles_plot,
                  tracks=options.tracks,
                  width=options.width)        
        
def aer_particles_plot(tracks, width):
    log = find_log_for_tracks(tracks)
    config = dict(log=log, tracks=tracks, width=width)
    pg('aer_particles_plot', config, stats=True)
    
def aer_particles_plot_main():
    sys.exit(AERParticlesPlotApp().main())
    
__all__ = ['aer_particles_plot_main']



def find_log_for_tracks(tracks):
    while '.' in tracks:
        tracks = os.path.splitext(tracks)[0]
        f = tracks + '.aedat'
        print('trying %s' % f)
        if os.path.exists(f):
            return f
    msg = ('Could not find raw event log for tracks %r' % tracks)
    raise ValueError(msg)
    return None
        
        
