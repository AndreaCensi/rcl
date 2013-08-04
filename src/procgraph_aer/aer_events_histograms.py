from aer.stats import aer_histogram, aer_histogram_sign
from procgraph import simple_block
from aer.stats.histo import aer_histogram_fancy


@simple_block
def aer_events_hist(events):
    return aer_histogram(events)

@simple_block
def aer_events_hist_sign(events):
    return aer_histogram_sign(events)

@simple_block
def aer_events_hist_fancy(events):
    return aer_histogram_fancy(events)



@simple_block
def aer_filter_pos(events):
    select = events['sign'] > 0
    return events[select]

@simple_block
def aer_filter_neg(events):
    select = events['sign'] < 0
    return events[select]


@simple_block
def aer_transpose(e):
    """ Tmp util to switch the axes """
    x = e['x']
    y = e['y']
    e = e.copy()
    e['x'] = 127 - y
    e['y'] = x
    return e
    
