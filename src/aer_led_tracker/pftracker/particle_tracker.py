from . import contract, np
from aer_led_tracker.pftracker.particles import (particle_dist,
    particle_is_compatible, particle_merge, particle_evolve_up_to)
from aer_led_tracker.types import aer_particle

class ParticleTracker():
    """ A class that tracks a set of particles for one frequency. """
    
    @contract(max_vel='>0', max_bound='>0')    
    def __init__(self, max_vel, max_bound):
        self.max_vel = max_vel
        self.max_bound = max_bound
        self.particles = []
    
    def evolve_up_to(self, timestamp):
        e = lambda p: particle_evolve_up_to(p, self.max_vel, timestamp)
        self.particles = map(e, self.particles)
                          
    @contract(tracks='tracks_array')
    def add_observations(self, tracks):
        timestamp = tracks[0]['timestamp']
        
        self.evolve_up_to(timestamp)
        
        self.merge_observations(tracks)

        self.remove_too_large()
        self.merge_particles()

        score_sum = np.sum([x['score'] for x in self.particles])
        for p in self.particles:
            p['score'] /= score_sum

        # also add new particles
        self.particles.extend(map(track2particle, tracks))
        
        self.last = tracks.copy()
        
    def remove_too_large(self):
        new_particles = []
        for p in self.particles:
            if p['bound'] <= self.max_bound:
                new_particles.append(p) 
        self.particles = new_particles
        
    def merge_particles(self):
        new_particles = []
        # sort particles by bound, smallest to big
        self.particles.sort(key=lambda x: x['bound'])
        for p_big in self.particles:
            for p_small in new_particles:
                # if p_small is included into p_big,
                # then let's say they merge 
                dist = particle_dist(p_small, p_big)
                merge = dist < p_big['bound']  
                if merge:
                    p_small['score'] += p_big['score']
                    break
            else:
                new_particles.append(p_big)
                 
        self.particles = new_particles
    
    def merge_observations(self, tracks):
        new_particles = []
        for p in self.particles:
            # add one without merging
            # with the lowest probability
            q = p.copy()
            min_quality = np.min(tracks['quality'])
            q['score'] *= min_quality
            new_particles.append(q)
            # add the ones that merged
            for t in tracks:
                coords = np.array([t['i'], t['j']])
                if particle_is_compatible(p, coords):
                    p1 = particle_merge(p, coords, coords_score=t['quality'])        
                    new_particles.append(p1)
        
        self.particles = new_particles
        
    def get_all_particles(self):
        self.particles.sort(key=lambda x: (-x['score']))
        return list(self.particles)
    
    
@contract(t='track_dtype', returns='is_particle_dtype')
def track2particle(t):
    p = aer_particle(timestamp=t['timestamp'],
                     id_track=t['id_track'],
                     coords=[t['i'], t['j']],
                     score=t['quality'],
                     bound=2)  # XXX
    return p

    
    
