import numpy
import math


def bisection_triangle_row(n, previous):
    if n == 0:
        yield 0.5
    else:
        for x in previous:
            yield x - 2**(-n - 1)
            yield x + 2**(-n - 1)


def bisection_sequence(depth=numpy.inf):
    n = 0
    row = []
    while n < depth:
        row = list(bisection_triangle_row(n, row))
        yield from row
        n += 1


def frequency_bisection_sequence(start, end, depth=numpy.inf):
    logstart = math.log(start)
    logend = math.log(end)
    yield start
    yield end
    for x in bisection_sequence(depth):
        yield math.exp((logend - logstart) * x + logstart)
