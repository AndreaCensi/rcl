

aer_raw_event_dtype = [
    ('timestamp', 'float'),
    ('x', 'int16'),
    ('y', 'int16'),
    ('sign', 'int8')
]

aer_filtered_event_dtype = [
    ('timestamp', 'float'),
    ('x', 'int16'),
    ('y', 'int16'),
    ('sign', 'int8'),
    ('delta', 'float'), ('frequency', 'float32'),
    ('valid', 'bool'), ('same', 'bool'),
]


# this one has float coordinates
aer_floatcoord_event_dtype = [
    ('timestamp', 'float'),
    ('x', 'float'),
    ('y', 'float'),
    ('sign', 'int8')
]

aer_imu6_dtype = [
#     ('timestamp', 'float'),
#     ('ax', 'float'),
#     ('ay', 'float'),
#     ('az', 'float'),
#     ('gx', 'float'),
#     ('gy', 'float'),
#     ('gz', 'float'),

    ('accel', ('float', 3)),
    ('gyro', ('float', 3)),
]

aer_frame_dtype = [
    ('ts_startframe', 'float'),
    ('ts_endframe', 'float'),
    ('ts_startexposure', 'float'),
    ('ts_endexposure', 'float'),
    # exposure in seconds (difference of previous two fields)
    ('ts_exposure', 'float'),
    ('pixels', ('uint16', (180, 240))),
]
    
