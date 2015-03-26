import numpy

def bisection_triangle_row(n, previous):
    if n == 0:
        yield 0.5
    else:
        for x in previous:
            yield x - 2**(-n - 1)
            yield x + 2**(-n - 1)

def bisection_sequence(max_depth=numpy.inf):
    n = 0
    row = []
    while n < max_depth:
        row = list(bisection_triangle_row(n, row))
        for x in row:
            yield x
        n += 1
