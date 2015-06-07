import numpy as np
from rawlogs.library import RawTextLog
from aer.types import aer_raw_event_dtype, aer_imu6_dtype, aer_frame_dtype
import warnings
from rawlogs.library.textlog import RawTextSignal



__all__ = ['AER2TXTLog']


class AER2TXTLog(RawTextLog):

    def __init__(self, filename):
        dtypes = {}
        dtypes['events'] = aer_raw_event_dtype
        dtypes['frame'] = aer_frame_dtype
        dtypes['imu6'] = aer_imu6_dtype

        RawTextLog.__init__(self,
                            filename=filename,
                            dtypes=dtypes,
                            parse_function=aer2_txt_parse)

    def read(self, topics, start=None, stop=None):

        allofthem = RawTextSignal(self.filename,
                                   parse_function=self.parse_function,
                                   time_reference='unused',
                                   select=topics,
                                   dtype='unused')

        events = []

        def aggregate(es):
            a = np.array(es)
            return a

        for time, (name, value) in allofthem.read(start, stop):
            assert name in topics

            if name == 'events':
                events.append(value)
            else:
                if events:
                    yield float(events[0]['timestamp']), ('events', aggregate(events))
                    events = []

                yield time, (name, value)

        if events:
            yield float(events[0]['timestamp']), ('events', aggregate(events))
            events = []


def aer2_txt_parse_polarity(tokens):
    # POLARITY_EVENT 22 900541285 1 165 150
    if not len(tokens) == 6:
        msg = 'Invalid line.'
        raise ValueError(msg)

    ts_mus = int(tokens[2])
    pol = int(tokens[3])
    x = int(tokens[4])
    y = int(tokens[5])

    a = np.zeros(dtype=aer_raw_event_dtype, shape=())
    ts = float(ts_mus / (1000.0 * 1000.0))
    a['timestamp'] = ts
    a['sign'] = +1 if pol == 1 else -1
    a['x'] = x
    a['y'] = y
    data = [(ts, 'events', a)]

    return data

def s_from_mus(mus):
    ts = float(int(mus) / (1000.0 * 1000.0))
    return ts


def aer2_txt_parse_imu6(tokens):
    # IMU6_EVENT 900517372  7.938965 7.033447 0.478760  0.991821 1.632690 999.496399
    if len(tokens) != 8:
        msg = 'Invalid line (expected 8 tokens, got %r).' % tokens
        raise ValueError(msg)

    ts = s_from_mus(tokens[1])

    ax = float(tokens[2])
    ay = float(tokens[3])
    az = float(tokens[4])
    gx = float(tokens[5])
    gy = float(tokens[6])
    gz = float(tokens[7])

    a = np.zeros(dtype=aer_imu6_dtype, shape=())
    
    a['accel'] = np.array([ax, ay, az])
    a['gyro'] = np.array([gx, gy, gz])

    return [(ts, 'imu6', a)]


def aer2_txt_parse_frame(tokens):
    # FRAME_EVENT 0  900437716 900479782 42066   900456749 900460751 4002   240 180   0 0 64 0

    assert 'FRAME_EVENT' == tokens.pop(0)
    _ = tokens.pop(0)

    ts_startframe = s_from_mus(tokens.pop(0))
    ts_endframe = s_from_mus(tokens.pop(0))
    _ = tokens.pop(0)

    ts_startexposure = s_from_mus(tokens.pop(0))
    ts_endexposure = s_from_mus(tokens.pop(0))
    exposure = s_from_mus(tokens.pop(0))

    width = int(tokens.pop(0))
    height = int(tokens.pop(0))

    n = width * height

    if len(tokens) != n:
        msg = 'Expected %d pixels, got %s' % (n, len(tokens))
        raise ValueError(msg)

#     pixels = np.array(map(int, tokens), dtype='uint16').reshape((height, width))

    warnings.warn('Change back when fixing the stuff')

    pixels = np.array(map(int, tokens), dtype='uint16').reshape((width, height))
    pixels = pixels.T
#     pixels = np.flipud(pixels)

    e = np.zeros(dtype=aer_frame_dtype, shape=())
    e['ts_startframe'] = ts_startframe
    e['ts_endframe'] = ts_endframe
    e['ts_startexposure'] = ts_startexposure
    e['ts_endexposure'] = ts_endexposure
    e['ts_exposure'] = exposure
    e['pixels'] = pixels

    return [(ts_startframe, 'frame', e)]



messages = {
    'IMU6_EVENT': aer2_txt_parse_imu6,
    'FRAME_EVENT': aer2_txt_parse_frame,
    'POLARITY_EVENT': aer2_txt_parse_polarity,
}

def aer2_txt_parse(line):
    if '#' in line:
        return None
    
    elements = line.strip().split()

    if len(elements) == 0:
        msg = 'Invalid line (empty).'
        raise ValueError(msg)

    message = elements[0]

    if message in messages:
        return messages[message](elements)
    else:
        msg = 'Unknown message type %r.' % message
        raise ValueError(msg)
    
