import numpy as np
from contracts import contract
import itertools


def md_argmax(a):
    """ Returns the value and the index coordinate of a multidimensional array """
#    min_value = np.min(a)
    index_flat = np.argmax(a)
    ij = np.unravel_index(index_flat, a.shape)
    ij = tuple(ij)
    # assert_allclose(a[ij], min_value)
    return a[ij], ij

def construct_matrix_iterators(iterators, function):
    
    elements = map(list, iterators)
    shape = map(len, elements)
    
    def element(*args):  # args is a tuple of indices = (i, j, k, ...)
        assert len(args) == len(shape)
        combination = [a[i] for a, i in zip(elements, args)]
        return function(*combination)
        
    return construct_matrix(shape, element)
    
def iterate_indices(shape):
    if len(shape) == 2:
        for i, j in itertools.product(range(shape[0]), range(shape[1])):
            yield i, j
    else:
        raise NotImplementedError
        assert(False)

@contract(shape='tuple(>0,>0)')       
def construct_matrix(shape, function, dtype='float'):
    ndim = len(shape)
    if ndim != 2:
        msg = 'Sorry, not implemented for ndim != 2 (got %d).' % ndim
        raise NotImplementedError(msg)
    D = np.zeros(shape, dtype=dtype) 
    for indices in iterate_indices(shape):
        result = function(*indices)
        if not isinstance(result, (float, int)):
            raise ValueError('%s(%s) = %s' % 
                             (function.__name__, indices, result))
        D[indices] = result
    return D
