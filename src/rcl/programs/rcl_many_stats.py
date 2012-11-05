from . import logger, np
from ..utils import wrap_script_entry_point
from optparse import OptionParser
from vehicles.configuration.master import VehiclesConfig
from rcl.library.simulations import get_simulation_data

def rcl_many_stats_main(args):
    parser = OptionParser(usage="")
    parser.disable_interspersed_args()

    parser.add_option("--vehicle", default='d_SE2_rb_v-cam_f180_n16_gn01',
                      help="ID vehicle [%default].")
    parser.add_option("--world", default='stochastic_box_10',
                       help="ID world [%default].")
    
    parser.add_option("--outdir", "-o", default='rcl_demo_vehicles',
                    help="output directory [%default]")

    parser.add_option("--resolution", default=0.01, type='float')
    parser.add_option("--length", default=1.0, type='float')
    parser.add_option("--threshold", default=0.05, type='float')
    
    parser.add_option("--nsims", default=2, type='int')

    parser.add_option("--seed", default=None, type='int')
    
    (options, args) = parser.parse_args(args)
    
    if args:
        raise Exception()
    
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
    
    command = lambda _: np.array([1, 0, 0])
    

    dt = options.resolution
    length = options.length
    threshold = options.threshold
    nsims = options.nsims

    simconf = dict(id_world=id_world,
                   id_vehicle=id_vehicle,
                   command=command,
                   dt=dt, length=length, spike_threshold=threshold)

    simulations = jobs_many_stats(nsims, simconf)


def jobs_many_stats(nsims, simconf):
    simulations = []
    for _ in range(nsims):
        simdata = get_simulation_data(**simconf)
        simulations.append(simdata)
    return simulations
    

def main():
    wrap_script_entry_point(rcl_many_stats_main, logger)
