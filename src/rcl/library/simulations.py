from . import np, logger
from rcl.library import SpikingSensor
from vehicles import VehicleSimulation, VehiclesConfig
import os
from rcl.library.spiking import event_dtype

def get_simulation_data(id_world, id_vehicle, command, dt, length, spike_threshold):
    """
        Returns a dictionary with the following fields:
        
        - "events": numpy array with fields
        
            timestamp
            index
            sign
            value     
            
        - "observations":  array[K]
        
            timestamp
            observations
            pose
            velocity
            
        - "directions": list of array[3], directions on the sphere
        
        - "map"  

    """
        
    all_events = []
    observations = []
    
    vsim = vehicle_simulation(id_world, id_vehicle, command, dt, length)
    for data in spiking_vehicle_simulation(spike_threshold, vsim):
        all_events.extend(data['events'])
        
        y = data['observations']
        n = len(y)
        
        obs_dtype = [('timestamp', 'float'),
                     ('observations', ('float', n)),
                     ('pose', ('float', (4, 4))),
                     ('velocity', ('float', (4, 4)))]
        
        obs = np.array((data['timestamp'], data['observations'],
                         data['pose'], data['velocity']),
                         dtype=obs_dtype)
        
        print obs.size, obs.dtype
        
        observations.append(obs)
    
    observations = np.array(observations, dtype=obs.dtype)
    all_events = np.array(all_events, dtype=event_dtype)
    
    print observations.size, observations.dtype
    print all_events.size, all_events.dtype
    
    directions = vs.get_vehicle().sensors[0].directions
    log = {}
    log['observations'] = observations
    log['events'] = all_events
    log['directions'] = directions
    log['map'] = None  # XXX
    return log
    
def spiking_vehicle_simulation(threshold, vsim):
    """ Yields a sequence of dictionary with fields:
    
        - "timestamp"
        - "events":
        - "observations": array of N sensels
        - "pose"
        - "velcoity"
    """
    spiking_sensor = SpikingSensor(threshold)
    for vs in vsim:
        observations = vs.compute_observations()
        timestamp = vs.get_timestamp()
        events = spiking_sensor.push(timestamp, observations)
        pose, vel = vs.get_vehicle().get_configuration() 
        data = {}
        data['timestamp'] = timestamp
        data['observations'] = observations
        data['events'] = events
        data['pose'] = pose
        data['velocity'] = vel
        yield data


def vehicle_simulation(id_world, id_vehicle, command, dt, length):
    """ Yields a simulation """
    vehicle = VehiclesConfig.vehicles.instance(id_vehicle)  # @UndefinedVariable
    world = VehiclesConfig.worlds.instance(id_world)  # @UndefinedVariable
    simulation = VehicleSimulation(vehicle, world)    
    simulation.new_episode()

    n = int(np.ceil(length / dt)) + 1    
    for i in xrange(n):
        t = i * dt

        yield simulation
        
        commands = command(t)
        simulation.simulate(commands, dt)
    


def write_logs(dirname, sim, spiking_sensor, write_yaml=True):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    logger.info('Writing to directory %r.' % dirname)
    yaml_log = os.path.join(dirname, 'vehicles_log.yaml')
    events_log = os.path.join(dirname, 'events.txt')
    obs_log = os.path.join(dirname, 'observations.txt')
    f = open(yaml_log, 'w')
    f_ev = open(events_log, 'w')
    f_obs = open(obs_log, 'w')
    
    for i, simulation in enumerate(sim):
        observations = simulation.compute_observations()
        timestamp = simulation.get_timestamp()
        events = spiking_sensor.push(timestamp, observations)
        
        logger.info('Step %d: %d events' % (i, len(events)))
        
        for timestamp, index, sign in events:
            f_ev.write('%s %s %s\n' % (timestamp, index, sign))
            f_ev.flush()
            
        if True:
            s = " ".join(map(str, observations)) + '\n'
            f_obs.write(s)
            f_obs.flush()
            
        if write_yaml:
            sim_state = simulation.to_yaml()
            f.write('---\n')
            f.write(str(sim_state))
            f.write('\n')
            


