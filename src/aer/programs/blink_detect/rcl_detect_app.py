from . import rcl_detect
from quickapp import QuickApp
import sys
 

class AERBlinkDetect(QuickApp):
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)
        params.add_string("pipeline", default='both')
            
        params.add_int_list("frequencies", default=[500, 700, 1000],
                                                    help='frequencies')
        params.add_float("sigma", default=50)        
        params.add_int("pd", default=100, help="phase discretization")
        params.add_flag("video")
        
    def define_jobs(self):
        options = self.get_options()
        outdir = self.get_output_dir()
        self.comp(rcl_detect, options.log, options.pipeline,
                  options.frequencies, options.sigma, outdir,
                  write_png=options.video)
        

 
def aer_blink_detect_main():
    sys.exit(AERBlinkDetect().main())

    
