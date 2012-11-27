from . import aer_video_meat
from quickapp import QuickApp
import sys

class AERVideoApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)    
        params.add_float("interval", help='delta', default=0.03)
                            
    def define_jobs(self):
        options = self.get_options()
        self.comp(aer_video_meat, options.log, options.interval)        

def aer_video_main():
    sys.exit(AERVideoApp().main())
    
