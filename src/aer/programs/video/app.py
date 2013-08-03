from quickapp import QuickApp
from quickapp import iterate_context_names_triplet

__all__ = ['AERVideoApp', 'aer_video_main']

class AERVideoApp(QuickApp):
    
    cmd = 'video'
    
    usage = '%prog --log <data.aedat> --interval 0.05'
    
    styles = {'bysign': 'aer_events_show_bysign',
              'simple': 'aer_events_show_simple'}
    
    def define_options(self, params):
        params.add_string_list("log", help='source file')    
        params.add_float_list("interval", help='delta', default=0.03)
        params.add_string_list("style", default='simple')
                            
    def define_jobs_context(self, context):
        options = self.get_options()
        models = [AERVideoApp.styles[s] for s in options.style]
        logs = options.log
        intervals = options.interval
        
        combinations = iterate_context_names_triplet(context, models, logs, intervals)
        for c, model, log, interval in combinations:
            c.comp(aer_video_meat, log=log, interval=interval, model=model)        

aer_video_main = AERVideoApp.get_sys_main()

from procgraph import pg

def aer_video_meat(log, interval, model='aer_events_show'):
    import procgraph_aer  # @UnusedImport
    config = dict(filename=log, interval=interval)
    pg(model, config)


