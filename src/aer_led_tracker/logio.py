import os


class AERTrackLogWriter(object):
    def __init__(self, filename):
        outdir = os.path.dirname(filename)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        self.tracks = open(filename, 'w')
        self.tracks.write('# timestamp id_track  x y  quality\n')
    
    def write(self, timestamp, id_track, x, y, quality):
        self.tracks.write('%15g %10s %10f %10f %10f\n' % 
                     (timestamp, id_track, x, y, quality))
        self.tracks.flush()

    
 
