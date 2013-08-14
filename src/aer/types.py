

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
