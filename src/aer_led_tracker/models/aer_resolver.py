from aer_led_tracker.resolver import Resolver, alternatives_print
from procgraph import Block
from aer_led_tracker.motion import MaxVelMotion

class AERResolver(Block):
    Block.alias('aer_resolver')
    # Block.config('ntracks')
    Block.input('track_log')
    Block.output('hps')
    
    Block.config('min_track_dist', default=10)
    Block.config('max_vel', default=1000.0)
    Block.config('history', default=0.005)
    
    Block.config('max_hp', 'Maximum number of hypotheses to show',
                 default=10)
    
    def init(self):
        motion_model = MaxVelMotion(self.config.max_vel,
                                    self.config.min_track_dist)
        self.resolver = Resolver(motion_model=motion_model,
                                 history=self.config.history,
                                 min_track_dist=self.config.min_track_dist)
        
            
    def update(self):
        self.resolver.push(self.input.track_log)
        
        
        alts = self.resolver.compute_alternatives()
 
        if False:
            # check correct
            alts2 = self.resolver.compute_alternatives_combinatorial()
            alternatives_print(alts2, 'normal', n=4)
        
        alternatives_print(alts, 'fast', n=4)
 
        hps = alts
        N = self.config.max_hp
        if len(hps) > N:
            hps = hps[:N]
        
#        alternatives_print(hps)
        self.output.hps = hps
