from . import TrackerFixedFreq, logger
from aer import aer_load_log_generic
from aer.filters import aer_pipeline_transitions1, aer_pipeline_transitions1_all
from aer.utils import md_argmax
from aer_led_tracker import AERTrackLogWriter
from contracts import contract
from procgraph_pil.imwrite import imwrite  # XXX
from reprep import rgb_zoom, scale
from scipy.ndimage import gaussian_filter
import itertools
import numpy as np
import os


def rcl_detect(log, pipeline, frequencies, sigma, outdir, detect_smooth_sigma=1.0,
               detect_neighbors=10, write_png=False):
    
    if False:
        raw_sequence = aer_load_log_generic(log)
        transitions = aer_pipeline_transitions1(raw_sequence, pipeline)
    else:
        transitions = aer_pipeline_transitions1_all(log, pipeline)
    
    interval = 1.0 / min(frequencies)
    trackers = [TrackerFixedFreq(f, sigma, interval=interval) for f in frequencies]

    tracks_filename = os.path.join(outdir, 'all.tracks.txt')
    tracklog = AERTrackLogWriter(tracks_filename)
    
    def handle_tracker_res(tracker, accum, timestamp):
        detection = peak_detect(accum, sigma=detect_smooth_sigma,
                                    neighbors=detect_neighbors)
        
        if write_png:
            rcl_detect_write_png(tracker, detection, timestamp, outdir)
        else:
            print('%14s %s' % (timestamp, tracker.freq))
        center = detection['centroid'] 
        quality = detection['centroid_nevents']
        id_track = int(tracker.freq)
        tracklog.write(timestamp=timestamp, id_track=id_track,
                       x=center[0], y=center[1], quality=quality)

    for f in transitions:
        for tracker in trackers:
            res = tracker.integrate(f)
            if res is not None:
                handle_tracker_res(tracker, res, f['timestamp'])


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
    _, accum_smooth_max = md_argmax(accum_smooth)
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
    return res
    
    
def rcl_detect_write_png(tracker, detection, timestamp, outdir):
    dirname = os.path.join(outdir, 'f%05d' % tracker.freq)
    
    def write_image(name, values):    
        time_us = timestamp * 1000 * 1000
        dirname2 = os.path.join(dirname, name) 
        if not os.path.exists(dirname2):
            os.makedirs(dirname2)
        filename = os.path.join(dirname2, 'ms%08d.png' % time_us)
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
        
             
         
