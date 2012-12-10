import numpy as np
from contracts import new_contract, contract


# These are the particles

aer_particle_dtype = np.dtype([
    ('timestamp', 'float'),
    ('id_track', 'S32'),
    ('coords', 'float', 2),
    ('score', 'float'),
    ('bound', 'float'),
])


@contract(timestamp='float', id_track='str', coords='seq[2](number)',
          score='>0', bound='>0')
def aer_particle(timestamp, id_track, coords, score, bound):     
    """ Creates a particle """
    p = np.zeros(shape=(), dtype=aer_particle_dtype)
    p['timestamp'] = timestamp
    p['id_track'] = id_track
    p['coords'][0] = coords[0]
    p['coords'][1] = coords[1]
    p['score'] = score
    p['bound'] = bound
    return p


@new_contract
def is_particle_dtype(x):
    if not x.dtype == aer_particle_dtype:
        msg = 'Invalid dtype: %r' % x.dtype
        raise ValueError(msg)

new_contract('particles_array', 'array[>=1],is_particle_dtype')



