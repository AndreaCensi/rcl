import sys
from io import BufferedReader
import io

import numpy as np
from rcl.library.aerlog.types import aer_raw_event_dtype

def aer_raw_events_from_file(filename):
    """ Yields a sequence of arrays of aer_raw_event_dtype from file. """
    events = aer_load_from_file(filename)
    for ts_mus, x, y, s in events:
        a = np.zeros(dtype=aer_raw_event_dtype, shape=())
        a['timestamp'] = ts_mus / (1000.0 * 1000.0)
        a['x'] = x 
        a['y'] = y
        a['sign'] = s
        yield a

def aer_load_from_file(filename):
    """ Yields tuples (ts_mus, x,y,s) """
    f = io.open(filename, 'r+b') 
    f = BufferedReader(f)
    comments = read_comments(f)
    if not 'AER-DAT2.0' in comments[0]:
        msg = 'Can only read 2.0 files'
        raise ValueError(msg) 
    while f:
        ts_str = f.read(4)
        if len(ts_str) != 4:
            break
#        
#        ts1 = ord(ts_str[0])
#        ts2 = ord(ts_str[1])
#        ts3 = ord(ts_str[2])
#        ts4 = ord(ts_str[3])
#        ts_ = ts1 * 256 * 256 * 256 + ts2 * 256 * 256 + ts3 * 256 + ts4
         
        ts = np.fromstring(ts_str, dtype=np.uint32).newbyteorder('>')
        ts_mus = ts[0]
        
#        print ts_, ts_mus
#        print ('%3d %3d %3d %3d' % (ts1, ts2, ts3, ts4))
        address = np.fromstring(f.read(4), dtype=np.int32).newbyteorder('>')
        x, y, s = address2xys(address)
        yield ts_mus, x, y, s

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
        pass




if __name__ == '__main__':
    main()
