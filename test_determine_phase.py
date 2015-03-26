import determine_phase
import numpy
import numpy.random
import math

def test_sin_fit():
    numpy.random.seed(1)

    n = 1000
    epsilon = 1e-3

    for freq in [1e-3, 1e-4, 50e-4]:
        for c in range(-3, 4):
            for s in range(-3, 4):
                for intercept in range(-3, 4):
                    ts = numpy.arange(n)
                    ws = 2 * numpy.pi * ts * freq
                    xs = c * numpy.cos(ws) + s * numpy.sin(ws) + intercept
                    c_, s_, intercept_ = determine_phase.sin_fit(xs, freq)
                    assert(abs(c - c_) < epsilon)
                    assert(abs(s - s_) < epsilon)
                    assert(abs(intercept - intercept_) < epsilon)

                    for sigma in [epsilon, 1e-1]:
                        xs += numpy.random.normal(scale=sigma, size=n)
                        c_, s_, intercept_ = determine_phase.sin_fit(xs, freq)
                        assert(abs(c - c_) < 10 * sigma)
                        assert(abs(s - s_) < 10 * sigma)
                        assert(abs(intercept - intercept_) < 10 * sigma)

def angle_mod(x, m):
    return math.fmod(math.fmod(x, m) + m, m)

def angle_difference(x, y):
    return angle_mod(x - y + math.pi, 2 * math.pi) - math.pi

def test_angle_difference():
    assert(angle_difference(0, 1) == -1)
    assert(angle_difference(-1, 0) == -1)
    assert(angle_difference(1, 0) == 1)
    assert(angle_difference(0, -1) == 1)

def test_sin_phase():
    numpy.random.seed(1)

    n = 1000
    freq = 1e-3
    epsilon = 1e-2

    for phase in numpy.arange(0, 2 * numpy.pi, numpy.pi / 8):
        for intercept in range(-3, 4):
            ts = numpy.arange(n)
            ws = 2 * numpy.pi * ts * freq + phase
            xs = numpy.sin(ws) + intercept
            phase_ = determine_phase.sin_phase(xs, freq)
            assert(abs(angle_difference(phase, phase_)) < epsilon)
            for sigma in [1e-2, 1e-1, 0.2]:
                xs += numpy.random.normal(scale=sigma, size=n)
                phase_ = determine_phase.sin_phase(xs, freq)
                assert(abs(angle_difference(phase, phase_)) < 1e-1)
