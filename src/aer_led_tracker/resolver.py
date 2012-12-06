from abc import abstractmethod, ABCMeta
from contracts import contract
from operator import attrgetter
import itertools
import numpy as np


class MotionModel(object):
    """ Interface for a generic motion model. """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def probability_joint(self, tracks):
        """ tracks: array of tracks, with the same ID.
            Return probability of joint distribution """


class MaxVelMotion(MotionModel):
    """ Maximum velocity constraint """
    def __init__(self, max_vel, min_dist):
        self.max_vel = max_vel
        self.min_dist = min_dist
        
    def probability_joint(self, tracks):    
        p_motion = self.probability_velocity(tracks)
        p_state = self.probability_state(tracks)
        return p_motion * p_state
    
    
    def probability_state(self, tracks):
        """ Checks that the distance is not too small """
        def probability2(t1, t2):
            if t1['id_track'] == t2['id_track']:
                return 1
            else:
                delta_time = np.abs(t1['timestamp'] - t2['timestamp'])
                distance = vector_norm(track_coords(t1) - track_coords(t2))
                if False:  # XXX  
                # suppose that it could fly away at max_vel
                # it could be at minimum at this distance
                    min_distance = distance + delta_time * self.max_vel
                else:
                    min_distance = distance
                if min_distance <= self.min_dist:
                    return 0
                else:
                    return 1
                
        indices = range(len(tracks))
        p = 1
        for i, j in itertools.combinations(indices, 2):
            p *= probability2(tracks[i:i + 1], tracks[j:j + 1])
        return p
     
    def probability_velocity(self, tracks):
        for _, its_tracks in enumerate_id_track(tracks):
            if len(its_tracks) == 1:
                return 1.0
            
            vn = track_velocities_norm(its_tracks)
            max_vn = np.max(vn)
            if max_vn >= self.max_vel:
                return 0.0
            else:
                return 1.0

def enumerate_id_track(tracks):
    id_tracks = np.unique(tracks['id_track'])
    for id_track in id_tracks:
        sel = tracks['id_track'] == id_track
        yield id_track, tracks[sel]
    

def vector_norm(x):
    return np.linalg.norm(x, 2)

def assert_only_one_id(tracks):
    x = np.unique(tracks['id_track'])
    assert len(x) == 1
    
@contract(tracks='array[N]', returns='array[(N-1)x2]')
def track_velocities(tracks):
    assert_only_one_id(tracks)
    
    coords = track_coords(tracks)
    vel = np.diff(coords, axis=0)
    return vel

@contract(tracks='array[N]', returns='array[N-1]')
def track_velocities_norm(tracks):
    assert_only_one_id(tracks)
    
    velocities = track_velocities(tracks)
    vn = [vector_norm(x) for x in velocities]
    return np.array(vn)

@contract(tracks='array[N]', returns='array[Nx2]')
def track_coords(tracks):
    assert_only_one_id(tracks)
    
    i = tracks['i']
    j = tracks['j']
    coords = np.vstack((i, j)).T
    n = len(i)
    assert coords.shape == (n, 2)
    return coords

class Resolver(object):
    
    """ Resolves ambiguities based on track history """
    def __init__(self, min_track_dist, motion_model, history):
        """
            :param history: Length of history to consider.
            :param min_track_dist: Minimum distance between different track (pixels)
            :param max_vel: Maximum velocity (pixels/s)
        """
        self.min_track_dist = min_track_dist
        self.motion_model = motion_model
        self.history = history
        
        self.buffer = []
        
    @contract(track_observations='array[>=1]')
    def push_obs(self, track_observations):
        self.buffer.append(track_observations)
        
        def too_big():
            t1 = self.buffer[-1][0]['timestamp']
            t0 = self.buffer[0][0]['timestamp']
            delta = t1 - t0
            print('Current delta: %s  n: %s' % (delta, len(self.buffer)))
            return delta > self.history
                
        while too_big():
            self.buffer.pop(0)

    def push(self, track_observations):
        """
            :param track_observations: array of track_observations_dtype
        """
        self.push_obs(track_observations)
        

        res = compute_alternatives(self.buffer)
        print res
        
        
    def compute_alternatives(self):
        return compute_alternatives(self.buffer, self.motion_model)

    def compute_alternatives_combinatorial(self):
        """ Uses a combinatorial algorithm """
        return compute_alternatives_combinatorial(self.buffer, self.motion_model)



class Alternative():
    def __init__(self, id_choice, score, motion_score, obs_score, subset, nmisses,
                 ntracks):
        self.id_choice = id_choice
        self.score = score
        self.motion_score = motion_score
        self.obs_score = obs_score
        self.subset = subset
        self.nmisses = nmisses
        self.ntracks = ntracks
    
    def __repr__(self):
        return ("Alt(id:%s;#:%d;score:%g;motion:%g;obs:%g)" % 
        (self.id_choice, self.ntracks, self.score, self.motion_score, self.obs_score))


def alternatives_print(alts):
    for i, x in enumerate(alts):
        print('%s: %s' % (i, x))
        
MISS = '-'
@contract(obs_buffer='list[>=1](array[>=1])')
def select_tracks(obs_buffer, choice):
    chosen = []
    for obs, i in zip(obs_buffer, choice):
        if i == MISS:
            continue
        chosen.append(obs[i])
    if not chosen:
        raise ValueError('all misses')
    return np.array(chosen, chosen[0].dtype)
    
@contract(obs_buffer='list[>=1](array[>=1])')
def compute_alternatives_combinatorial(obs_buffer, motion_model):
    assert len(obs_buffer) >= 1
    
    options = []
    for b in obs_buffer:
        options.append(range(len(b)) + [MISS])

    delta = obs_buffer[-1][0]['timestamp'] - obs_buffer[0][0]['timestamp']
    print 'delta: %fs hps: %s' % (delta, map(len, obs_buffer))

    choices = []
    all_options = itertools.product(*tuple(options))     
    for c in all_options:
        # Skip if all misses
        nmisses = len([x for x in c if x == MISS])
        if nmisses == len(c):
            continue
        
        tracks = select_tracks(obs_buffer, c)
        ntracks = len(np.unique(tracks['id_track']))
        assert len(tracks) == len(obs_buffer) - nmisses
        motion_prob = motion_model.probability_joint(tracks)
        
        if motion_prob == 0:
            # Do not write those with impossible prob.
            continue
        
        motion_score = np.log(motion_prob)
        obs_score = np.sum(np.log(tracks['quality']))
        score = motion_score + obs_score
        id_choice = "".join(map(str, c))
        alt = Alternative(id_choice=id_choice,
                          score=score,
                          ntracks=ntracks,
                          motion_score=motion_score,
                          obs_score=obs_score,
                          nmisses=nmisses,
                          subset=tracks)
        choices.append(alt)
    
    sort_alternatives_ntracks_score(choices)
    
    return choices

def sort_alternatives_ntracks_score(choices):
    # Because python has stable sorting, we can do this:
    choices.sort(key=attrgetter('score'), reverse=True)
    choices.sort(key=attrgetter('ntracks'), reverse=True)

 
def compute_alternatives(obs_buffer):
    """
        Returns a list of tuples
        
            [(quality, [obs1, ..., obs3]), ...]
    """
    def entropy(track_observations):
        return -np.max(track_observations['quality'])
    # Let's first sort by certainty
    obs_buffer = sorted(obs_buffer, key=entropy)

    return compute_alternatives_slave(likelihood=[], decided=[], remaining=obs_buffer,)


def compute_likelihood(decided, obs):
    return 1

def compute_alternatives_slave(likelihood, decided, remaining, id_choice=""):
    if not remaining:
        return []
    # Let's take one set of observations
    obs = remaining[0]
    
    # If there is only one choice
    for i, alternate in enumerate(obs):
        if len(obs) == 1:
            # only one observations
            id_choice += '-'
        else:
            id_choice += str(i)
            
        this_choice_likelihood = compute_likelihood(decided, alternate)
        
        likelihood += [this_choice_likelihood] 
#        
#        print('%d: %s %s' % (i,
#                             track_obs[0]['id_track'], track_obs['quality']))
#        
#        if len(track_obs) == 1:
#        
#        
#        if len(track_obs) > 1:
#            for j in range(len(track_obs)):
#                bj = obs_buffer[1:]
#        



