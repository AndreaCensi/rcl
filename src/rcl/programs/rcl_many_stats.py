from . import logger, np
from quickapp import QuickApp
from rcl.library.simulations import get_simulation_data
from vehicles import VehiclesConfig


class RCLStatsApp(QuickApp):
    
    def define_options(self, params):
        params.add_string("vehicle", default='d_SE2_rb_v-cam_f180_n16_gn01',
                          help="ID vehicle.")
        params.add_string("world", default='stochastic_box_10', help="ID world")
        params.add_float_list("resolution", default=[0.01])
        params.add_float_list("length", default=[1.0])
        params.add_float_list("threshold", default=[0.05])
        params.add_int("nsims", default=2)
        params.add_int("seed", default=None)
        
    def define_jobs(self, options, rm):
        id_vehicle = options.vehicle
        id_world = options.world
    
        logger.info('id_vehicle: %s' % id_vehicle)
        logger.info('  id_world: %s' % id_world)
    
        if options.seed is None:
            options.seed = np.random.randint(1000000)
    
        np.random.seed(seed=options.seed)
        logger.info('Using seed %s (your lucky number is %s)' % 
                    (options.seed, np.random.randint(1000)))
    
    
        VehiclesConfig.load()
        
        def get_default_dir():
            from pkg_resources import resource_filename  # @UnresolvedImport
            directory = resource_filename("rcl", "configs")
            return directory
        
        VehiclesConfig.load(get_default_dir())
    
        simconf = dict(id_world=id_world,
                       id_vehicle=id_vehicle,
                       command=command,
                       dt=self.choice(options.resolution),
                       length=self.choice(options.length),
                       spike_threshold=self.choice(options.threshold),
                       iteration=self.choice(range(options.nsims)))
    
        jobs = self.comp_comb(run_simulation, **simconf)
            
#        for param2, samples in jobs.groups_by_field_value('param2'):
#            rj = comp(report, param2, samples)
#            rm.add(rj, 'report', param2=param2)



def command(t):
    return np.array([1, 0, 0])
    
def run_simulation(iteration, **simconf):
    return get_simulation_data(**simconf)

def main():
    RCLStatsApp().main()
    
