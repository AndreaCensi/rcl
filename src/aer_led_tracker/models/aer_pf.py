from aer_led_tracker.models import get_track_colors
from aer_led_tracker.pf import ParticleDetection, aer_state_dtype
from aer_led_tracker.tracks import enumerate_id_track
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
import numpy as np


class AERPF(Block):
    """ Simple particle filter """
    
    Block.alias('aer_pf')
    
    Block.input('track_log')
    Block.output('hps')
    
    Block.config('min_track_dist', default=10)
    Block.config('max_vel', default=1000.0)
    Block.config('history', default=0.005)
    
    Block.config('max_hp', 'Maximum number of hypotheses to show',
                 default=10)
    
    def init(self):
        # id_track -> PF
        self.pfs = {}
            
    def update(self):
        tracks = self.input.track_log
        id_track = tracks[0]['id_track']
        if not id_track in self.pfs:
            self.pfs[id_track] = ParticleDetection()
        
        self.pfs[id_track].observations(tracks)
        
        current = self.get_current_tracks()
        if len(current) > 0:
            self.output.hps = current

    def get_current_tracks(self):
        """ Returns the current guesses for the state. """
        current = []
        for x in self.pfs.values():
            current.extend(x.get_current_tracks()) 
        current = np.array(current, dtype=aer_state_dtype) 
        return current



class AERPFPlotter(Block):
    Block.alias('aer_pf_plot')
    Block.config('width', 'Image dimension', default=384)
    Block.input('tracks')
    Block.output('rgb')
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.width,
                                        transparent=False,
                                        tight=False)
        
        
    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
    def plot(self, pylab):
        tracks = self.input.tracks
        track2color = get_track_colors(tracks)  
        for id_track, particles in enumerate_id_track(self.input.tracks):
            color = track2color[id_track]
            prob = particles['score']
        
            lprob = np.log(prob)
            lprob -= np.min(lprob)
            lprob /= np.max(lprob)
            
            for i, particle in enumerate(particles):
                x = particle['coords'][0]
                y = particle['coords'][1]
                radius = particle['bound']
                cir = pylab.Circle((x, y), radius=radius,
                                   fc=color, edgecolor='none')
                alpha = lprob[i] * 0.5 + 0.5
                cir.set_alpha(alpha)
                cir.set_edgecolor('none')
                pylab.gca().add_patch(cir) 
        pylab.axis((-1, 128, -1, 128)) 


class AERPFQualityPlotter(Block):
    Block.alias('aer_pf_quality_plot')
    Block.config('width', 'Image dimension', default=384)
    Block.input('tracks')
    Block.output('rgb')
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.width,
                                        transparent=False,
                                        tight=False)
        
        
    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
    def plot(self, pylab):
        tracks = self.input.tracks
        track2color = get_track_colors(tracks)  
        for id_track, particles in enumerate_id_track(self.input.tracks):
            color = track2color[id_track]
            bound = particles['bound']
            score = particles['score']
            pylab.scatter(bound, np.log(score), marker='s', color=color)
            
        a = pylab.axis()
        pylab.axis((-1, 30, a[2], a[3]))
        pylab.xlabel('bound (pixel)')
        pylab.ylabel('score')
         
