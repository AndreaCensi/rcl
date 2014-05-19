import os

from aer_led_tracker.programs.tracker_plot import aer_tracker_plot
from quickapp import QuickApp
from quickapp import iterate_context_names

from .mhdetector import MHDetectorLog


__all__ = ['aer_blink_detect_main']


class AERBlinkDetect(QuickApp):
    """ Detects blinking LEDs in .aedat file. """

    def define_options(self, params):
        params.add_string_list("log", help='AER .aedat file')
        params.add_string("pipeline", default='both')
        params.add_float('interval', default=None)
        params.add_float("sigma", default=50)
        params.add_int("npeaks", default=3)
        params.add_float("min_led_distance", default=5,
                         help='Minimum distance between LEDs')
        params.add_int("pd", default=100, help="phase discretization")
        params.add_flag("video")
        params.add_string("suffix")

        params.add_int("video2_width", default=256)

        
    def define_jobs_context(self, context):
        options = self.get_options()
        outdir = context.get_output_dir()

        for c, ilog in iterate_context_names(context, range(len(options.log))):
            log = options.log[ilog]
            if not os.path.exists(log):
                msg = ('Cannot find log %r.' % log)
                raise ValueError(msg)
            suffix = options.suffix
            tracks_filename = os.path.splitext(log)[0] + '.%s.tracks' % suffix

            md = c.comp(aer_blink_detect,
                           log=log,
                           pipeline=options.pipeline,
                           sigma=options.sigma,
                           outdir=outdir,
                           npeaks=options.npeaks,
                           tracks_filename=tracks_filename,
                           min_led_distance=options.min_led_distance,
                           interval=options.interval,
                           detect_smooth_sigma=1.0,
                           write_png=options.video)

    #         #   if options.video2: #XXX
    #         if True:
            context.comp(aer_tracker_plot, tracks=tracks_filename,
                          width=options.video2_width,
                          extra_dep=[md])
        

def aer_blink_detect(**kwargs):
    md = MHDetectorLog(**kwargs)
    md.go()
           
 
aer_blink_detect_main = AERBlinkDetect.get_sys_main()

    
