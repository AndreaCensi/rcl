

aer_raw_event_dtype = [('timestamp', 'float'), ('x', 'int'),
                   ('y', 'int'), ('sign', 'int')]

aer_filtered_event_dtype = [('timestamp', 'float'),
#                        ('timestamp_prev', 'float'),
                         ('x', 'int'), ('y', 'int'), ('sign', 'int'),
                    ('delta', 'float'), ('frequency', 'float'),
                    ('valid', 'bool'), ('same', 'bool'),
#                    ('sign_prev', 'int'),
#                    ('delta_same', 'float'),
#                    ('frequency_same', 'float')
                    ]
