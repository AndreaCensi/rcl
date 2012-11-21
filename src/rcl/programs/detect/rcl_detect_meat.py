from . import TrackerFixedFreq, logger
from contracts import contract
from procgraph_pil.imwrite import imwrite
from rcl.library.aerlog import load_aer_generic
from rcl.library.filters import (aer_raw_relative_timestamp, AER_Filter,
    AER_Transitions_Filter)
from rcl.utils import md_argmax, construct_matrix
from reprep import rgb_zoom, scale
from scipy.ndimage import gaussian_filter
import os
import itertools
from aer_led_tracker.logio import AERTrackLogWriter


def rcl_detect(log, frequencies, sigma, outdir, detect_smooth_sigma=1.0,
               detect_neighbors=10, write_png=False):
    raw_sequence = load_aer_generic(log)
    raw_sequence = aer_raw_relative_timestamp(raw_sequence)
    filtered = AER_Filter().filter(raw_sequence)
    transitions = AER_Transitions_Filter(sign=(+1)).get_transitions(filtered)
    trackers = [TrackerFixedFreq(f, sigma) for f in frequencies]


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


Mi = construct_matrix((128, 128), lambda i, _: i)
Mj = construct_matrix((128, 128), lambda _, j: j)

import numpy as np


@contract(accum='array[HxW]', center='seq[2](int)', neighbors='int,>1')
def centroid_estimate(accum, center, neighbors):
    """ Returns S, mi, mj """
    accum = accum.copy()
    i, j = center[0], center[1]
    # Set as 0
    mask = np.zeros((128, 128), dtype=bool)
    mask.fill(True)
    mask[max(0, i - neighbors):min(127, i + neighbors),
          max(0, j - neighbors):min(127, j + neighbors)] = False
    accum[mask] = 0  
    # compute mean coordinate
    S = accum.sum()
    mi = (accum * Mi).sum() / S
    mj = (accum * Mj).sum() / S
    return accum, S, mi, mj


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
    for name in ['accum', 'accum_cleared', 'accum_smooth']:
        value = detection[name]
        value[c[0], c[1]] = np.nan
        write_image(name, value)
        
         
    
