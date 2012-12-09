from contracts import contract
import numpy as np

def vector_norm(x):
    return np.linalg.norm(x, 2)

@contract(a='seq[N,>=1](number)', b='seq[N](number)')
def vector_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return vector_norm(a - b)
