import numpy
import numpy.linalg
import math

def sin_fit(xs, frequency):
    ts = numpy.arange(len(xs))
    ws = 2 * numpy.pi * frequency * ts
    a = numpy.vstack([
        numpy.cos(ws),
        numpy.sin(ws),
        numpy.ones(len(ws))
    ]).T
    c, s, intercept = numpy.linalg.lstsq(a, xs)[0]
    return (c, s, intercept)

def sin_phase(xs, frequency):
    c, s, intercept = sin_fit(xs, frequency)
    return math.atan2(c, s)
