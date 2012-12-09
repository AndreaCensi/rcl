from aer_led_tracker.utils.vectors import vector_distance
from aer_led_tracker.types import aer_particle


def particle_dist(p2, p1):
    return vector_distance(p2['coords'], p1['coords'])

def particle_is_compatible(p, coords):
    """ Returns true if the observation at coords are compatible. """
    dist = vector_distance(p['coords'], coords)
    compatible = dist < p['bound']
    return compatible 
    

def particle_merge(p, coords, coords_score):
    """ Merge the observations """
    assert p.shape == ()
    pos1 = p['coords']
    pos2 = coords
    alpha1 = 1.0 / p['bound']
    alpha2 = 1.0 
    pos = (pos1 * alpha1 + pos2 * alpha2) / (alpha1 + alpha2)
    
    bound2 = 1.0 / (alpha1 + alpha2)
    score = p['score'] * coords_score
    timestamp = p['timestamp'].item()
    id_track = p['id_track'].item()
    return aer_particle(timestamp=timestamp, id_track=id_track,
                        score=score, coords=pos, bound=bound2)
        
def particle_evolve_up_to(p, max_vel, timestamp):
    delta = timestamp - p['timestamp']
    assert delta >= 0
    q = p.copy()
    q['timestamp'] = timestamp
    q['bound'] += max_vel * delta
    return q
    
