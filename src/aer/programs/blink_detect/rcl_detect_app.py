from aer.programs.blink_detect.mhdetector import MHDetectorLog
from quickapp import QuickApp
import os
import sys
 

class AERBlinkDetect(QuickApp):
    def define_options(self, params):
        params.add_string("log", help='source file', compulsory=True)
        params.add_string("pipeline", default='both')
        params.add_float('interval', default=None)
        params.add_float("sigma", default=50)
        params.add_int("npeaks", default=3)
        params.add_float("min_led_distance", default=5,
                         help='Minimum distance between LEDs')
#        params.add_float("weight_others", default=0)         
        params.add_int("pd", default=100, help="phase discretization")
        params.add_flag("video")
        params.add_string("suffix", compulsory=True)

        params.add_flag("video2", default=True)
        params.add_int("video2_width", default=256)

        
    def define_jobs(self):
        options = self.get_options()
        outdir = self.get_output_dir()
        
        log = options.log
        suffix = options.suffix
        tracks_filename = os.path.splitext(log)[0] + '.%s.tracks' % suffix

        md = self.comp(aer_blink_detect,
                       log=options.log,
                       pipeline=options.pipeline,
                       sigma=options.sigma,
                       outdir=outdir,
                       npeaks=options.npeaks,
                       tracks_filename=tracks_filename,
                       min_led_distance=options.min_led_distance,
                       interval=options.interval,
                       detect_smooth_sigma=1.0,
                       write_png=options.video)
    
        #   if options.video2: #XXX
        if True: 
            from aer_led_tracker.programs.plot.meat import aer_tracker_plot
            self.comp(aer_tracker_plot, tracks=tracks_filename,
                      width=options.video2_width,
                      extra_dep=[md])       
        

def aer_blink_detect(**kwargs):
    
    md = MHDetectorLog(**kwargs)
    
    md.go()
           
 
def aer_blink_detect_main():
    sys.exit(AERBlinkDetect().main())

    
