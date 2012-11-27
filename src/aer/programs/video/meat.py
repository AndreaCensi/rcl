from procgraph import pg

def aer_video_meat(log, dt):
    import procgraph_aer  # @UnusedImport
    config = dict(filename=log, interval=dt)
    pg('aer_events_show', config)


