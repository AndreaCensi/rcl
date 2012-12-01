from procgraph import pg

def aer_tracker_plot(tracks, width):
    config = dict(log=tracks, width=width)
    pg('aer_track_plot', config)
    
