from . import aer_raw_event_dtype, np, logger
from StringIO import StringIO


def aer_raw_sequence(line_stream):
    """ Yields a sequence of events from a stream.
        Returns a raw_event_dtype.
     """
    for line in line_stream:
        io = StringIO(line)  # XXX inefficient
        try:
            a = np.genfromtxt(io, dtype=aer_raw_event_dtype)
        except ValueError as e:
            msg = 'Could not read line %r: %s' % (line, e)
            logger.error(msg)
            raise
                
        a['timestamp'] = a['timestamp'] * 0.001 * 0.001
        if a['sign'] == 0:
            a['sign'] = -1
        yield a
