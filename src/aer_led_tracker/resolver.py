from contracts import contract
from operator import attrgetter
import itertools
import numpy as np


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
        
#        res = compute_alternatives(self.buffer)
#        print res
        
        
    def compute_alternatives(self):
        print('------------')
        alt1 = compute_alternatives_sep(self.buffer, self.motion_model)
        print('------------')
        alt1 = compute_alternatives(self.buffer, self.motion_model)
        return alt1
    
    def compute_alternatives_combinatorial(self):
        """ Uses a combinatorial algorithm """
        return compute_alternatives_combinatorial(self.buffer, self.motion_model)



class Alternative():
    def __init__(self, id_choice, score, motion_prob,
                 motion_score, obs_score, subset, nmisses,
                 ntracks):
        self.id_choice = id_choice
        self.score = score
        self.motion_score = motion_score
        self.obs_score = obs_score
        self.subset = subset
        self.nmisses = nmisses
        self.ntracks = ntracks
        self.motion_prob = motion_prob
    
    def zero_prob(self):
        return self.motion_prob == 0
    
    def __repr__(self):
        return ("Alt(id:%s;#:%d;score:%g;motion:%g;obs:%g)" % 
        (self.id_choice, self.ntracks, self.score, self.motion_score, self.obs_score))


def alternatives_print(alts, what=None, n=None):
    num = len(alts)
    if n:
        if len(alts) > n:
            alts = alts[:n]
    else:
        n = len(alts)
         
    if what:
        print('--- %s  (%s/%s) ---' % (what, n, num))
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
        if num_misses(c) == len(c):
            continue
        
        alt = make_alternative(obs_buffer=obs_buffer, choice=c,
                               motion_model=motion_model)
        if alt.motion_prob == 0:
            # Do not write those with impossible prob.
            continue
        choices.append(alt)
    
    sort_alternatives_ntracks_score(choices)
    
    return choices


def make_alternative(obs_buffer, choice, motion_model):
    assert len(obs_buffer) == len(choice)
    assert not all_misses(choice)
    tracks = select_tracks(obs_buffer, choice)
    assert len(tracks) == len(obs_buffer) - num_misses(choice)
    assert len(tracks) >= 0
    ntracks = len(np.unique(tracks['id_track']))
    motion_prob = motion_model.probability_joint(tracks)
    
    motion_score = np.log(motion_prob)
    obs_score = np.sum(np.log(tracks['quality']))
    score = motion_score + obs_score
    id_choice = "".join(map(str, choice))
    alt = Alternative(id_choice=id_choice,
                      score=score,
                      ntracks=ntracks,
                      motion_prob=motion_prob,
                      motion_score=motion_score,
                      obs_score=obs_score,
                      nmisses=num_misses(choice),
                      subset=tracks)
    return alt


def num_misses(choice):
    return len([x for x in choice if x == MISS])


def all_misses(choice):
    return num_misses(choice) == len(choice)
    
    
def sort_alternatives_ntracks_score(choices):
    # Because python has stable sorting, we can do this:
    choices.sort(key=attrgetter('score'), reverse=True)
    choices.sort(key=attrgetter('ntracks'), reverse=True)

 

def compute_alternatives_sep(obs_buffer, motion_model):
    
    id_tracks = set([x[0]['id_track'].item() for x in obs_buffer])
    
    res = {}
    for id_track in id_tracks:
        obs_track = [x for x in obs_buffer if x[0]['id_track'] == id_track]
 
#        print('Computing for track %s' % id_track)
#        
        alts = compute_alternatives(obs_track, motion_model)
        # alternatives_print(alts, 'track %s' % id_track, 5)
        
        res[id_track] = len(alts)
    print res
     
    
def compute_alternatives(obs_buffer, motion_model):
    """
        Returns a list of tuples
        
            [(quality, [obs1, ..., obs3]), ...]
    """
    debug = {}
    debug['niterations'] = 0
    debug['nterm'] = 0
    debug['ntest'] = 0
    debug['nstop'] = 0
    obs_buffer.sort(key=lambda x: x[0]['id_track'])
    res = compute_alternatives_slave(obs_buffer=obs_buffer,
                                     motion_model=motion_model,
                                     choice_so_far=[],
                                      decided=[], remaining=obs_buffer,
                                      debug=debug)
    
    ncomb = np.prod([(len(x) + 1) for x in obs_buffer])
    ndone = debug['niterations']
    possible = len(res)
    print('%d -> %d iterations instead of %d' % (len(obs_buffer), ndone, ncomb))
    print(debug)
    print('possible: %d ' % possible)
    sort_alternatives_ntracks_score(res)
    return res


@contract(obs_buffer='list[N,>=1](array[>=1])',
          returns='list[>=1]')
def compute_alternatives_slave(obs_buffer, motion_model, choice_so_far,
                               decided, remaining,
                               debug,
                               max_misses=4):
    """
    
        decided: 
        remaining: choices to make
        
        Returns a list of alternatives.
    """
    assert len(obs_buffer) == len(decided) + len(remaining)
    assert len(choice_so_far) == len(decided)
    
    if not remaining:
        # We have chosen everything
        if all_misses(choice_so_far):
            return []
        alt = make_alternative(obs_buffer, choice_so_far, motion_model)
        return [alt]
    
    debug['niterations'] += 1
        
    # Let's take one set of observations
    current = remaining[0]
    
    # Either one of the options, or "MISS"
    possible_choices = range(len(current)) + [MISS] 
    
    # If there is only one choice
    res = []
    
    for alternate in possible_choices:
        c = choice_so_far + [alternate]
        
        if num_misses(c) >= max_misses:
            continue
        
        # Cannot compute probability for all misses
        if all_misses(c):
            ok = True
        else:
            # print 'evaluating choice %s' % c
            assert not all_misses(c)
            partial = make_alternative(obs_buffer[:len(c)], c, motion_model)
            ok = not partial.zero_prob()
            
        debug['ntest'] += 1
        if not ok:
            # print('skipping %s + %s' % (choice_so_far, alternate))
            debug['nstop'] += 1
            continue
        else:
            decided2 = decided + [current]
            remaining2 = remaining[1:]
            x = compute_alternatives_slave(obs_buffer=obs_buffer,
                                          motion_model=motion_model,
                                          choice_so_far=c,
                                          decided=decided2,
                                          remaining=remaining2,
                                          debug=debug)
            res.extend(x)  

    return res

