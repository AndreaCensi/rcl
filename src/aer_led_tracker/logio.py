import os
import numpy as np
from StringIO import StringIO

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
        
    def write(self, timestamp, id_track, x, y, quality):
        self.tracks.write('%15g %10s %10f %10f %10f\n' % 
                     (timestamp, id_track, x, y, quality))
        self.tracks.flush()

    
    def done(self):
        self.tracks.close()
        if os.path.exists(self.filename):
            os.unlink(self.filename)
        if os.path.exists(self.tmp_filename):
            os.rename(self.tmp_filename, self.filename)

        
aer_track_dtype = [('timestamp', 'float'), ('id_track', 'S32'), ('x', 'float'),
                   ('y', 'float'), ('quality', 'float')]

def aer_track_parse_line(line):
    if '#' in line:
        return None
    x = np.genfromtxt(StringIO(line), aer_track_dtype)
    return x
    
    
