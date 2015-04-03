from skardas import bisection_sequence


def test_frequency_bisection_sequence():
    assert(list(bisection_sequence.frequency_bisection_sequence(100, 800, 0)) == [100, 800])
