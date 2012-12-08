from StringIO import StringIO
import numpy as np
import os

aer_track_dtype = [('timestamp', 'float'),
                   ('id_track', 'S32'),
                   ('npeaks', 'int'),
                   ('peak', 'int'),
                   ('i', 'float'),
                   ('j', 'float'),
                   ('quality', 'float')
                   ]

def create_track_observation(frequency, timestamp, peak, npeaks, coords, quality):
    id_track = '%d' % frequency
    val = (timestamp, id_track, npeaks, peak, coords[0], coords[1], quality)
    a = np.array(val, dtype=aer_track_dtype)
    return a


class AERTrackLogWriter(object):
    def __init__(self, filename):
        outdir = os.path.dirname(filename)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)
        self.filename = filename
        self.tmp_filename = filename + '.active'
        self.tracks = open(self.tmp_filename, 'w')
        self.tracks.write('# Format: timestamp id_track  x y  quality\n')
    
    def write_comment(self, s):
        self.tracks.write('# %s \n' % s)
        self.tracks.flush()
        
    def write(self, h):
        self.tracks.write('%15g %10s %d %d %10f %10f %10f\n' % 
                     (h['timestamp'], h['id_track'], h['npeaks'], h['peak'],
                      h['i'], h['j'], h['quality']))
        self.tracks.flush()

    def write_multiple(self, hps):
#        s = StringIO()
#        np.savetxt(s, hps[0])
#        self.tracks.write(s.getvalue())
#        self.tracks.flush()
        for h in hps:
            self.write(h)
        
    def done(self):
        self.tracks.close()
        if os.path.exists(self.filename):
            os.unlink(self.filename)
        if os.path.exists(self.tmp_filename):
            os.rename(self.tmp_filename, self.filename)

        
def aer_track_parse_line(line):
    if '#' in line:
        return None
    x = np.genfromtxt(StringIO(line), aer_track_dtype)
    return x
    
def aer_track_parse_stream_all(stream):
    """ Returns the entire log as an array """
    x = np.genfromtxt(stream, aer_track_dtype)
    return x

def aer_track_parse_stream_as_blocks(stream):
    def enumerate_as_blocks(tracks):
        track_buffer = []
        for t in tracks:
            track_buffer.append(t)
            if t['peak'] == t['npeaks'] - 1:  # last in sequence
                res = np.array(track_buffer, track_buffer[0].dtype)
                yield res
                track_buffer = []
                
    x = aer_track_parse_stream_all(stream)
    for y in enumerate_as_blocks(x):
        yield y

    
