from contracts import contract
from aer_led_tracker.motion import MaxVelMotion

import numpy as np
from aer_led_tracker.tracks import vector_norm
 
aer_state_dtype = np.dtype([
                            ('timestamp', 'float'),
                            ('id_track', 'S32'),
                            ('npeaks', 'int'),
                            ('peak', 'int'),
                            ('coords', 'float', 2),
                            ('score', 'float'),
                            ('bound', 'float'),
                   ])

def particle_dist(p2, p1):
    return vector_norm(p2['coords'] - p1['coords'])

def particle_is_compatible(p, coords):
    """ Returns true if the observation at coords are compatible. """
    pos1 = p['coords']
    pos2 = coords
    dist = vector_norm(pos1 - pos2)
    compatible = dist < p['bound']
    return compatible 
    
def particle_merge(p, coords, coords_score):
    """ Merge the observations """
    q = np.zeros(shape=(), dtype=aer_state_dtype)
    pos1 = p['coords']
    pos2 = coords
    alpha1 = 1.0 / p['bound']
    alpha2 = 1.0 
    pos = (pos1 * alpha1 + pos2 * alpha2) / (alpha1 + alpha2)
    
    bound2 = 1.0 / (alpha1 + alpha2)
    score = p['score'] * coords_score
    q['coords'] = pos
    q['bound'] = bound2
    q['timestamp'] = p['timestamp']
    q['id_track'] = p['id_track']
    q['score'] = score 
    return q
        
        
        
def evolve_state(p, max_vel, delta):
    q = p.copy()
    q['timestamp'] += delta
    q['bound'] += max_vel * delta
    return q
    
def track2state(t):
    p = np.zeros(shape=(), dtype=aer_state_dtype)
    p['timestamp'] = t['timestamp']
    p['id_track'] = t['id_track']
    p['coords'][0] = t['i']
    p['coords'][1] = t['j']
    p['score'] = t['quality']
    p['bound'] = 1.0  # XXX
    return p
    
class ParticleDetection():
    
    def __init__(self, max_vel=200, max_bound=25):
        self.max_vel = max_vel
        self.max_bound = max_bound
        min_dist = 10000
        self.motion_model = MaxVelMotion(max_vel, min_dist)
        self.particles = []
        self.last = None
        
    def evolve(self, delta):
        self.particles = [evolve_state(p, self.max_vel, delta)
                          for p in self.particles]
             
    @contract(tracks='tracks_array')
    def observations(self, tracks):
        if self.last is None:
            self.last = tracks.copy()
            return

        t0 = self.last[0]['timestamp']
        t1 = tracks[0]['timestamp']
        delta = t1 - t0
        self.evolve(delta)
        
        self.merge_observations(tracks)

        self.remove_too_large()
        self.merge_particles()

        score_sum = np.sum([x['score'] for x in self.particles])
        for p in self.particles:
            p['score'] /= score_sum
            
        if not self.particles:
            self.particles = map(track2state, tracks)


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
        # also add new particles
        new_particles.extend(map(track2state, tracks))
        self.particles = new_particles
        
    def get_current_tracks(self):
        self.particles.sort(key=lambda x: (-x['score']))
        return list(self.particles)
    
    

    
        
