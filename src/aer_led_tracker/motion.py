from abc import abstractmethod, ABCMeta
from aer_led_tracker.tracks import (track_coords, vector_norm, enumerate_id_track,
    track_velocities_norm)
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
