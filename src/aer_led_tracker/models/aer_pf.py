from .utils import set_viewport_style, get_track_colors
from aer_led_tracker import ParticleTrackerMultiple
from aer_led_tracker.tracks import enumerate_id_track
from aer_led_tracker.utils import scale_score_smooth
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric
import numpy as np


class AERPF(Block):
    """ Simple particle filter """
    
    Block.alias('aer_pf')
    
    Block.input('track_log')
    Block.output('particles', 'All particles')
    Block.output('hps', 'A list of coherent hypotheses')
    
    Block.config('min_track_dist', 'Minimum distance between tracks')
    Block.config('max_vel', 'Maximum velocity')
    Block.config('max_bound', 'Largest size of the uncertainty')
    Block.config('max_hp', 'Maximum number of hypotheses to produce.')
    
    def init(self):
        params = dict(max_vel=self.config.max_vel,
                      min_track_dist=self.config.min_track_dist,
                      max_bound=self.config.max_bound)
        self.pdm = ParticleTrackerMultiple(**params)             
     
    def update(self):
        tracks = self.input.track_log
        
        self.pdm.add_observations(tracks)
        
        particles = self.pdm.get_all_particles()
        if len(particles) > 0:
            self.output.particles = particles

            max_hp = self.config.max_hp
            hps = self.pdm.get_coherent_hypotheses(max_hp)
            self.output.hps = hps 
            



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
            plot_particles(pylab, particles, color)
            
        set_viewport_style(pylab)
        pylab.title('Particles')


def plot_particles(pylab, particles, color):
    prob = particles['score']
    rank = scale_score_smooth(prob)
    alpha = 0.5 + 0.5 * rank

    for i, particle in enumerate(particles):
        x = particle['coords'][0]
        y = particle['coords'][1]
        radius = particle['bound']
        cir = pylab.Circle((x, y), radius=radius,
                           fc=color, edgecolor='none')
        cir.set_alpha(alpha[i])
        cir.set_edgecolor('none')
        pylab.gca().add_patch(cir)
    

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
        
        self.min_score = None  
        self.max_score = None
        
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
        
        min_score = np.min(particles['score'])
        max_score = np.max(particles['score'])
        
        if self.min_score is None:
            self.min_score = min_score
            self.max_score = max_score
            
        self.min_score = min(self.min_score, min_score)
        self.max_score = min(self.max_score, max_score)
             
#        a = pylab.axis()
#        pylab.axis((-1, 30, a[2], a[3]))
        M = 0.1
        y0 = np.log(self.min_score)
        y1 = np.log(self.max_score)
        delta = y1 - y0
        y0 -= M * delta
        y1 += M * delta
        
        pylab.axis((-1, 30, y0, y1))
        pylab.xlabel('spatial uncertainty (pixels)')
        pylab.ylabel('score')
        pylab.title('Particles statistics')


class AERPFHPPlotter(Block):
    Block.alias('aer_pf_hp_plotter')
    Block.config('width', 'Image dimension', default=128)
    Block.config('title', default=None)
    Block.input('alts')
    Block.output('rgb')
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.width,
                                        transparent=False,
                                        tight=False)
        self.max_q = 0
        
    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
    def plot(self, pylab):
        alts = self.input.alts
        
        markers = ['s', 'o', 'x']
        for i, alt in enumerate(alts):    
            marker = markers[i % len(markers)]
            self.plot_hp(pylab, alt, marker)
        
        # only draw if small...
        if len(alts) <= 2:
            scores = ",".join(['%g' % x.score for x  in alts])
            pylab.text(3, 3, 'score: %s' % scores)
        set_viewport_style(pylab)
        title = self.config.title
        if title is not None:
            pylab.title(title) 

    def plot_hp(self, pylab, alt, marker):
        particles = alt.subset
        track2color = get_track_colors(particles)  
        for id_track, particles in enumerate_id_track(particles):
            color = track2color[id_track]
            plot_particles(pylab, particles, color)        

             

# def get_last(subset):
#    tracks = {}
#    for id_track, its_data in enumerate_id_track(subset):
#        tracks[id_track] = its_data[-1:]
#    return tracks
