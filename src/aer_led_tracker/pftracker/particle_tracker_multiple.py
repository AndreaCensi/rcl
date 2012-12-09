from . import compute_alternatives, np, contract, ParticleTracker
from .. import aer_particle_dtype
from aer_led_tracker.pftracker.particles import particle_dist
import itertools


class ParticleTrackerMultiple():
    @contract(max_vel='>0', min_track_dist='>0', max_bound='>0')
    def __init__(self, max_vel, min_track_dist, max_bound):
        self.max_vel = max_vel
        self.min_track_dist = min_track_dist
        self.max_bound = max_bound
        self.pfs = {}

    @contract(tracks='tracks_array')
    def add_observations(self, tracks):
        id_track = tracks[0]['id_track']
        timestamp = tracks[0]['timestamp']
        
        # Create Tracker if it doesn't exist
        if not id_track in self.pfs:
            pd = ParticleTracker(max_vel=self.max_vel,
                                 max_bound=self.max_bound)
            self.pfs[id_track] = pd
            
        self.pfs[id_track].add_observations(tracks)
        
        # update up to a given time
        for p in self.pfs.values():
            p.evolve_up_to(timestamp)
        
    @contract(returns='particles_array')
    def get_all_particles(self):
        """ Returns the current guesses for the state. """
        current = []
        for x in self.pfs.values():
            current.extend(x.get_all_particles()) 
        current = np.array(current, dtype=aer_particle_dtype) 
        return current
    
    def get_coherent_hypotheses(self, num_hps):
        choices = [x.get_all_particles() for x in self.pfs.values()]
        choices = [x for x in choices if len(x) > 0]
        alts = arbitrate(choices, min_distance=self.min_track_dist)
        return alts


@contract(choices='list[>=1](list[>=1](is_particle_dtype))')
def arbitrate(choices, min_distance):
    """
        min_distance: minimum distance betwee different tracks
    """
    
    def score_function(particles):
        def not_too_close(t1, t2):
            if t1['id_track'] == t2['id_track']:
                return 1.0          
            distance = particle_dist(t1, t2)
            if distance <= min_distance:
                return 0.0
            else:
                return 1.0
        indices = range(len(particles))
        p = 1.0
        for i, j in itertools.combinations(indices, 2):
            p *= not_too_close(particles[i], particles[j])
            if p == 0: 
                return p
                 
        lik = np.prod([x['score'] for x in particles])
        return p * lik 

    alts = compute_alternatives(choices, score_function=score_function)
    return alts

    
    
