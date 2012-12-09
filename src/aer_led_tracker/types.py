import numpy as np
from contracts import new_contract, contract

# These are the observations

aer_track_dtype = [
   ('timestamp', 'float'),
   ('id_track', 'S32'),
   ('npeaks', 'int'),
   ('peak', 'int'),
   ('i', 'float'),
   ('j', 'float'),
   ('quality', 'float')
]


@new_contract
def track_dtype(x):
    if not x.dtype == aer_track_dtype:
        msg = 'Invalid dtype: %r' % x.dtype
        raise ValueError(msg)

new_contract('tracks_array', 'array[>=1],track_dtype')

def create_track_observation(frequency, timestamp, peak, npeaks, coords, quality):
    id_track = '%d' % frequency
    val = (timestamp, id_track, npeaks, peak, coords[0], coords[1], quality)
    a = np.array(val, dtype=aer_track_dtype)
    return a

# These are the particles

aer_particle_dtype = np.dtype([
    ('timestamp', 'float'),
    ('id_track', 'S32'),
#    ('npeaks', 'int'),
#    ('peak', 'int'),
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



