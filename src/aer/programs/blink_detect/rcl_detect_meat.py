from . import TrackerFixedFreq, logger
from aer import aer_load_log_generic
from aer.filters import aer_pipeline_transitions1, aer_pipeline_transitions1_all
from aer.utils import md_argmax
from aer_led_tracker import AERTrackLogWriter
from contracts import contract
from procgraph_pil.imwrite import imwrite  # XXX
from reprep import rgb_zoom, scale, posneg
from scipy.ndimage import gaussian_filter
from aer.programs.blink_detect.config import get_blink_config
import os
import numpy as np
import itertools
 
class MultipleDetector(object):
    def __init__(self, log, pipeline, sigma, outdir, tracks_filename,
               interval=None,
               min_led_distance=0, weight_others=0,
               detect_smooth_sigma=1.0,
               detect_neighbors=10, write_png=False):
        
        # get configuration
        blink_detect_config = get_blink_config(log)
        
        # create trackers    
        frequencies = blink_detect_config.get_frequencies()
        self.trackers = []
        for f in frequencies:
            others = list(frequencies)
            others.remove(f)
            tracker = TrackerFixedFreq(f, others=others,
                                          others_weight=weight_others,
                                          sigma=sigma, interval=interval)
            self.trackers.append(tracker)

        # start track log
#        tracks_filename = os.path.splitext(log)[0] + '.%s.tracks' % suffix
        self.tracklog = AERTrackLogWriter(tracks_filename)
        params = dict(frequencies=frequencies,
                      sigma=sigma, weight_others=weight_others,
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
        self.detect_neighbors = detect_neighbors
        self.min_led_distance = int(min_led_distance)
        self.write_png = write_png
        self.outdir = outdir
            
    def go(self):    
        for f in self.transitions:
            # check if this event makes any of those trigger
            triggered = []
            for tracker in self.trackers:
                res = tracker.integrate(f)
                if res is not None:
                    triggered.append(tracker)
                    
            # Check that all trackers have produced a frame
            # if so, start two-phase estimation
            if triggered and all([t.has_frame() for t in self.trackers]):
                self.two_phase_estimation(f['timestamp'], triggered)
        
        self.tracklog.done()
    
    def two_phase_estimation(self, timestamp, triggered):
        # first get the current spots
        first = []
        for t in self.trackers:
            td = peak_detect(t.get_accum(),
                             sigma=self.detect_smooth_sigma,
                             neighbors=self.detect_neighbors)
            first.append(dict(tracker=t, detection=td))
        
        # now let's order by quality
        first.sort(key=lambda x: (-x['detection']['quality']))

        # one by one
        second = []
        occupied = [] 
        while first:
            f = first.pop(0)
            f_accum = remove_occupied(accum=f['tracker'].get_accum(),
                                      occupied=occupied, distance=self.min_led_distance)
            f_d = peak_detect(f_accum, sigma=self.detect_smooth_sigma,
                                        neighbors=self.detect_neighbors)
            if f_d is None:
                logger.debug('No track for %s' % f['tracker'])
            else:
                c = f_d['centroid']
                occupied.append((int(c[0]), int(c[1])))
                second.append(dict(tracker=f['tracker'], detection=f_d))

        d = lambda a, b: np.linalg.norm(np.array(a, 'float') - np.array(b))
        distances = [d(p1, p2) for p1, p2 in itertools.combinations(occupied, 2)]
        if distances:
            min_distance = np.min(distances)
            assert min_distance >= self.min_led_distance
        
        for s in second: 
            if s['tracker'] in triggered:
                triggered.remove(s['tracker'])
                self.output(timestamp, s['tracker'], s['detection'])
        
        # ones that are invalid
        for t in triggered:
            if s['tracker'] == t:
                s['detection']['centroid'] = (5, 5)
                self.output(timestamp, s['tracker'], s['detection'])
        
                
    
    def output(self, timestamp, tracker, detection):
        if self.write_png:
            rcl_detect_write_png(tracker, detection, timestamp, self.outdir)
        else:
                pass
        # print('%14s %s' % (timestamp, tracker.freq))
        center = detection['centroid'] 
        quality = detection['centroid_nevents']
        id_track = int(tracker.freq)
        self.tracklog.write(timestamp=timestamp, id_track=id_track,
                            x=center[0], y=center[1], quality=quality)
 
    
def debug_show_list(name, x):
    print(name)
    for s in x:
        print('- %4d %4d  quality %6.3f  tracker %s' % 
              (s['detection']['centroid'][0],
               s['detection']['centroid'][1],
               s['detection']['quality'], s['tracker']))
    
    
@contract(accum='array[HxW]', occupied='list(seq[2](float))', distance='int')
def remove_occupied(accum, occupied, distance):
    """ Zeros the elements of the accum in the radius around the given points """
    accum = accum.copy()
    for x, y in occupied:
        x = int(x)
        y = int(y)
        mask = get_mask(accum, x, y, distance)
        accum[mask] = 0
        assert accum[x, y] == 0
    return accum    

    
def get_mask(accum, x, y, n):
    H, W = accum.shape
    x0 = max(x - n, 0)
    x1 = min(x + n, H - 1)
    y0 = max(y - n, 0)
    y1 = min(y + n, W - 1)
    xs = np.array(range(x0, x1 + 1), 'int')
    ys = np.array(range(y0, y1 + 1), 'int')
    assert xs[0] == x0
    assert xs[-1] == x1
    assert ys[0] == y0
    assert ys[-1] == y1
    mask = np.zeros(shape=accum.shape, dtype='bool')
    mask.fill(False)
    for x in xs:
        mask[x, ys] = True
    return mask
    
@contract(accum='array[HxW]', center='seq[2](int)', neighbors='int,>1')
def centroid_estimate2(accum, center, neighbors):
    """ Returns S, mi, mj """
    accum = accum.copy()
    i, j = center[0], center[1] 
    xs = range(max(0, i - neighbors), min(127, i + neighbors))
    ys = range(max(0, j - neighbors), min(127, j + neighbors))
    
    points = [(i, j) for i, j in itertools.product(xs, ys)]
    n = len(points)
    weights = np.array([accum[i, j] for (i, j) in points])
    points = np.array(points).T
    assert points.shape == (2, n)
    
    mi = np.average(points[0, :], weights=weights)
    mj = np.average(points[1, :], weights=weights)
    S = weights.sum()
    return accum, S, mi, mj
    
def peak_detect(accum, sigma, neighbors):
    """ Returns a dictionary with the fields:
    
        accum
        accum_cleared
        accum_smooth 
        accum_smooth_max = (x, y)
        centroid
    """
    # smooth a little bit
    accum_smooth = gaussian_filter(accum, sigma=sigma)
    val, accum_smooth_max = md_argmax(accum_smooth)
    if val == 0:
        return None
    # now take a weighted mean around val
    accum_cleared, nevents, mi, mj = \
        centroid_estimate2(accum, center=accum_smooth_max, neighbors=neighbors)
    
    res = {}
    res['accum'] = accum
    res['accum_cleared'] = accum_cleared
    res['accum_smooth'] = accum_smooth
    res['accum_smooth_max'] = accum_smooth_max
    res['centroid'] = (mi, mj)
    res['centroid_nevents'] = nevents
    res['quality'] = nevents  # overall quality estimate
    return res
    
    
def rcl_detect_write_png(tracker, detection, timestamp, outdir):
    dirname = os.path.join(outdir, 'f%05d' % tracker.freq)
    
    def write_image(name, values):    
        time_us = timestamp * 1000 * 1000
        dirname2 = os.path.join(dirname, name) 
        if not os.path.exists(dirname2):
            os.makedirs(dirname2)
        filename = os.path.join(dirname2, 'ms%08d.png' % time_us)
        if np.nanmin(values) < 0:
            rgb = posneg(values)
        else:
            rgb = scale(values)
        rgb = rgb_zoom(rgb, K=4)
        imwrite(rgb, filename)
        logger.debug('print to %r' % filename)

    c = detection['centroid']
    
    videos = ['accum', 'accum_cleared', 'accum_smooth']
    videos = ['accum'] 
    for name in videos:
        value = detection[name]
        value[c[0], c[1]] = np.nan
        write_image(name, value)
        
             
         
