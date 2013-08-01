from . import aer_video_meat
from quickapp import QuickApp


class AERVideoApp(QuickApp):
    
    usage = '%prog --log <data.aer> --interval 0.05'
    
    def define_options(self, params):
        params.add_string("log", help='source file')    
        params.add_float("interval", help='delta', default=0.03)
                            
    def define_jobs_context(self, context):
        options = self.get_options()
        context.comp(aer_video_meat, options.log, options.interval)        

aer_video_main = AERVideoApp.get_sys_main()

    
    

