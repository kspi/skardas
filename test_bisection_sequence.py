import bisection_sequence
import math

def test_frequency_bisection_sequence():
    assert(list(bisection_sequence.frequency_bisection_sequence(100, 800, 0)) == [100, 800])
