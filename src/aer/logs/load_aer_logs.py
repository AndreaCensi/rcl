from aer import aer_raw_event_dtype, logger
from io import BufferedReader
import io
import numpy as np
import sys
import csv


def aer_raw_events_from_file(filename):
    """ 
        Yields a sequence of arrays of aer_raw_event_dtype from file.
         
        If fake_interval is not None, it is used as the delta
        between successive events (in case timestamps are screwed).
    
    """
    events = aer_load_from_file(filename)
    count = 0
    for ts_mus, x, y, s in events:
        a = np.zeros(dtype=aer_raw_event_dtype, shape=())
        a['timestamp'] = ts_mus / (1000.0 * 1000.0)
        a['x'] = x 
        a['y'] = y
        a['sign'] = s
        yield a
        count += 1
        

def aer_raw_events_from_file_all(filename, limit=None):
    """ Returns an array of raw events """
    logger.info('Reading from %s ' % filename)
    f, _ = read_aer_header(filename)

    rest = f.read() 
    data = np.fromstring(rest, dtype=np.uint32).newbyteorder('>')
    nevents = data.size / 2
    
    if limit is not None:
        nevents = limit

    logger.info('Reading %d events...' % nevents)

    e = np.zeros(shape=nevents, dtype=aer_raw_event_dtype)
    e_x = e['x']
    e_y = e['y']
    e_ts = e['timestamp']
    e_s = e['sign']
    
    for i in xrange(nevents):
        address = data[i * 2]
        timestamp = data[i * 2 + 1]
        x, y, s = address2xys(address)
        e_s[i] = s
        e_x[i] = x
        e_y[i] = y
        e_ts[i] = timestamp * 0.000001

    logger.info('... done')
    
    return e

def aer_raw_events_from_csv(filename):
    timestamps = []
    x = []
    y = []
    sign = []
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if len(row) < 4:
                print('Invalid row: %r' % row)
            else:
                rt,rx,ry,rs = row[0:4]
                try:
                    timestamps.append(float(rt)*0.000001)
                    rx = int(float(rx))
                    ry = int(float(ry))
                    x.append(rx)
                    y.append(ry)
                    rs = int(rs)
                    if rs > 0:
                        rs = 1
                    else:
                        rs = -1
                    sign.append(rs)
                except Exception as ex:
                    msg = 'Invalid %r: %r ' % (row, ex)
                    raise ValueError(msg)
    n = len(timestamps)
    print('read %r events from file %r. '% (n, filename))
    e = np.zeros(shape=n, dtype=aer_raw_event_dtype)
    e['timestamp'] = timestamps
    e['sign'] = sign
    e['x'] =x
    e['y'] =y
            
    return e

def aer_raw_events_from_file_all_faster(filename, limit=None):
    """ Returns an array of raw events """
    logger.info('Reading from %s ' % filename)
    f, _ = read_aer_header(filename)

    rest = f.read() 
    logger.info('Read log with length %s' % len(rest))
    m = 4
    if len(rest) % m != 0:
        n = int(np.floor(len(rest) / m))
        extra = len(rest) - n * m 
        msg = 'The log is truncated -- reading only %d entries (%d extra bytes)' % (n, extra)
        logger.error(msg)
        rest = rest[:n * m]
    data = np.fromstring(rest, dtype=np.uint32).newbyteorder('>')
    nevents = data.size / 2
    
    if limit is not None:
        nevents = limit

    logger.info('Reading %d events...' % nevents)

    e = np.zeros(shape=nevents, dtype=aer_raw_event_dtype)
    e_x = e['x']
    e_y = e['y']
    e_ts = e['timestamp']
    e_s = e['sign']
    
    addresses = data[::2]
    timestamps = data[1::2]
    
    x = (addresses & 0x00FE) >> 1
    x = 127 - x
    y = (addresses & 0x7F00) >> 8
    s = addresses & 1
    
    s[s == 0] = -1    

    e_s[:] = s
    e_x[:] = x
    e_y[:] = y
    e_ts[:] = timestamps * 0.000001
    
    
    assert timestamps[0] < timestamps[-1]
    assert e_ts[0] < e_ts[-1]
    
    if True:
        assert np.all(np.diff(timestamps) >= 0)
    
    logger.info('... done')
    
    return e


def aer_load_from_file(filename, read_as_block=True):
    """ Yields tuples (ts_mus, x,y,s) """
    f, _ = read_aer_header(filename)
    
    if read_as_block:
        return read_block(f)
    else:
        return read_incrementally(f)
    
def read_aer_header(filename):
    f = io.open(filename, 'r+b') 
    f = BufferedReader(f)
    comments = read_comments(f)
    if comments:
        if not 'AER-DAT2.0' in comments[0]:
            msg = 'Can only read 2.0 files'
            raise ValueError(msg)
    return f, comments
    
def read_block(f):
    rest = f.read() 
    data = np.fromstring(rest, dtype=np.uint32).newbyteorder('>')
    nevents = data.size / 2
    for i in xrange(nevents):
        address = data[i * 2]
        timestamp = data[i * 2 + 1]
        x, y, s = address2xys(address)
        
        if i % 100000 == 0:
            print('%3.1f%% %6s/%6s' % (i * 100.0 / data.size, i, data.size))
        yield timestamp, x, y, s

def read_incrementally(f):
    while f:
        s = f.read(4)
        if len(s) != 4:
            break
        address = np.fromstring(s, dtype=np.uint32).newbyteorder('>')
        x, y, s = address2xys(address)

        ts_str = f.read(4)          
        ts = np.fromstring(ts_str, dtype=np.uint32).newbyteorder('>')

        yield ts[0], x, y, s

def address2xys(address):
    """ Converts an int32 "address" into x,y,sign """
    x = (address & 0xFE) >> 1
    x = 127 - x
    y = (address & 0x7F00) >> 8
    s = address & 1
    if s == 0:
        s = -1    
    return x, y, s

def read_comments(f):
    lines = []
    while True:
        line = read_comment_line(f)
        if line is not None:
            lines.append(line)
        else:
            break
    return lines
        
def read_comment_line(f):
    first = f.peek()[0]
    if first == '#':
        s = ""
        c = None
        while True:
            if c == '\n':
                break
            c = f.read(1)
            s += c
        return s   
    else:
        return None
        

def main():
    events = aer_load_from_file(sys.argv[1])
    for ts, x, y, s in events:  # @UnusedVariables
        print('%.10f %5d %5d %2d' % (ts, x, y, s))
        pass


if __name__ == '__main__':
    main()
