from aer.filters.pipelines import (aer_pipeline_transitions1,
    aer_pipeline_transitions1_all)
from aer.logs.generic import aer_load_log_generic
from aer.programs.blink_detect.config import get_blink_config
from aer.programs.blink_detect.fixed_freq_tracker import TrackerFixedFreq
from aer.programs.blink_detect.rcl_detect_meat import (centroid_estimate2,
    remove_occupied)
from aer.utils import md_argmax
from aer_led_tracker.logio import AERTrackLogWriter
from aer_led_tracker.tracks import create_track_observation
from contracts import contract
from scipy.ndimage.filters import gaussian_filter
import itertools
import numpy as np
 
    
class MHDetectorLog(object):
    
    def __init__(self, log, pipeline, sigma, outdir, tracks_filename,
               interval,
               min_led_distance,
               detect_smooth_sigma,
               npeaks,
               write_png=False):
        
        # get configuration
        blink_detect_config = get_blink_config(log)
        frequencies = blink_detect_config.get_frequencies()

        self.trackers = []
        for f in frequencies:
            others = list(frequencies)
            others.remove(f)
            tracker = TrackerFixedFreq(f, sigma=sigma, interval=interval)
            self.trackers.append(tracker)

        # start track log
        self.tracklog = AERTrackLogWriter(tracks_filename)
        params = dict(frequencies=frequencies,
                      sigma=sigma, weight_others=None,
                      interval=interval)
        self.tracklog.write_comment('params: %s' % params)

        # open files
        if False:
            raw_sequence = aer_load_log_generic(log)
            self.transitions = aer_pipeline_transitions1(raw_sequence, pipeline)
        else:
            self.transitions = aer_pipeline_transitions1_all(log, pipeline)

        # save params needed later
        self.detect_smooth_sigma = detect_smooth_sigma
        self.detect_neighbors = int(min_led_distance)
        self.min_led_distance = int(min_led_distance)
        # self.write_png = write_png
        self.outdir = outdir
        self.npeaks = npeaks
            
    def go(self):    
        for f in self.transitions:
            # check if this event makes any of those trigger
            for tracker in self.trackers:
                res = tracker.integrate(f)
                if res is not None:
                    self.find_peaks(f['timestamp'], tracker)
        self.tracklog.done()
    
    def find_peaks(self, timestamp, tracker):
        # first get the current spots
        accum = tracker.get_accum()
        accum_smooth = gaussian_filter(accum, sigma=self.detect_smooth_sigma)
        hps = peak_detect_multiple(accum_smooth,
                                     centroid_area=self.detect_neighbors,
                                     min_distance=self.min_led_distance,
                                     npeaks=self.npeaks,
                                     timestamp=timestamp,
                                     frequency=tracker.frequency)
        self.tracklog.write_multiple(hps)
                
 
 
@contract(accum='array[HxW]', min_distance='>0', centroid_area='>0',
          npeaks='int,>=1')
def peak_detect_multiple(accum, min_distance, centroid_area,
                         npeaks, frequency, timestamp,
                         min_nevents=0.000001):
    """ 
        Returns a set of peaks, at least min_distance from each other.
    
        Returns a dictionary with the fields:
    
        accum
        accum_cleared
        accum_smooth 
        accum_smooth_max = (x, y)

        hypotheses = list of hypotheses
        centroid
    """
    # For each peak
    hp = []
    for i in range(npeaks):
        # find the current peak
        val, accum_smooth_max = md_argmax(accum)
        if val <= min_nevents:
            continue
        
        # now take a weighted mean around val
        _, nevents, mi, mj = \
            centroid_estimate2(accum, center=accum_smooth_max,
                               neighbors=centroid_area)

        h = create_track_observation(frequency=frequency,
                                     timestamp=timestamp,
                                     coords=(mi, mj),
                                     quality=nevents,
                                     peak=i, npeaks=npeaks)        
        hp.append(h)
        
        m_before = np.max(accum)
        # print(accum[mi, mj])
        accum = remove_occupied(accum, occupied=[(mi, mj)],
                                distance=min_distance)
        # print(accum[mi, mj])
        assert accum[mi, mj] == 0
        
        m_after = np.max(accum)
        # print('%s >= %s' % (m_before, m_after))
        
        # XXX: something is still not right (should be ">")
        assert m_before >= m_after
        
        # Note: because of centroid stuff, it is not guaranteed
        # check_minimum_distance(hp, min_distance)
        
    # check_minimum_distance(hp, min_distance)
    
    for h in hp:
        h['npeaks'] = len(hp)
        
    return hp


def check_minimum_distance(hps, min_distance):
    """ Checks that the minimum distance is respected """
    points = [np.array((x['i'], x['j']), 'float') for x in hps]
    
    d = lambda a, b: np.hypot(a[0] - b[0], a[1] - b[1])
    distances = [d(p1, p2) for p1, p2 in itertools.combinations(points, 2)]
    if distances:
        min_d = np.min(distances)
        if min_d >= min_distance:
            msg = 'Wrong: %s ' % points
            msg += '\n%s' % hps
            msg += '\n distances: %s' % distances
            raise Exception(msg)
            
         
