from StringIO import StringIO
from aer_led_tracker.logio import aer_track_parse_stream_as_blocks
from aer_led_tracker.resolver import Resolver, MaxVelMotion, alternatives_print

tests = []

# Outlier
log1 = """     
0  t1  1 0   0 0   0.1
1  t1  2 0   0 1   0.1
1  t1  2 1   0 6   0.1
2  t1  1 0   0 2   0.1
3  t1  1 0   0 3   0.1
4  t1  1 0   0 4   0.1
"""
def check1(resolver):
    res = resolver.compute_alternatives_combinatorial()
    alts = res['alts']
    assert len(alts) == 2
    alternatives_print(alts)



    
tests.append(
    dict(log=log1,
         resolver_params=dict(min_track_dist=1,
                              motion_model=MaxVelMotion(max_vel=2),
                              history=1000),
         check_function=check1))




def check_resolver1(log, resolver_params, check_function):
    resolver = Resolver(**resolver_params)
    tracks = aer_track_parse_stream_as_blocks(StringIO(log))
    for d in tracks:
        resolver.push(d)
    check_function(resolver)

def test_resolver1():
    for test_data in tests:
        check_resolver1(**test_data)
        
    
