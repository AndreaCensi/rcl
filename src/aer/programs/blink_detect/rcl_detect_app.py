from quickapp import QuickApp
import sys
from aer.programs.blink_detect.rcl_detect_meat import MultipleDetector
 

class AERBlinkDetect(QuickApp):
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)
        params.add_string("pipeline", default='both')
#        params.add_int_list("frequencies", default=[500, 700, 1000],
#                                                    help='frequencies')
        params.add_float('interval', default=None)
        params.add_float("sigma", default=50)
        params.add_float("min_led_distance", default=0,
                         help='Minimum distance between LEDs')
        params.add_float("weight_others", default=0)         
        params.add_int("pd", default=100, help="phase discretization")
        params.add_flag("video")
        params.add_string("suffix", compulsory=True)
        
    def define_jobs(self):
        options = self.get_options()
        outdir = self.get_output_dir()
        
        self.comp(aer_blink_detect, log=options.log, pipeline=options.pipeline,
                  weight_others=options.weight_others,
#                  frequencies=options.frequencies, 
                  min_led_distance=options.min_led_distance,
                  sigma=options.sigma,
                  outdir=outdir, interval=options.interval,
                  write_png=options.video, suffix=options.suffix)
        

def aer_blink_detect(log, pipeline, sigma, outdir, suffix,
               interval=None,
               min_led_distance=0, weight_others=0,
               detect_smooth_sigma=1.0,
               detect_neighbors=10, write_png=False):
    
    md = MultipleDetector(log=log,
                          pipeline=pipeline,
                          sigma=sigma, outdir=outdir, suffix=suffix,
                          interval=interval,
                          min_led_distance=min_led_distance,
                          weight_others=weight_others,
                          detect_smooth_sigma=detect_smooth_sigma,
                          detect_neighbors=detect_neighbors,
                          write_png=write_png)
    md.go()
           
 
def aer_blink_detect_main():
    sys.exit(AERBlinkDetect().main())

    
