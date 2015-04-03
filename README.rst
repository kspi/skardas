skardas
=======

A tool for measuring the frequency response of passive or active filters and
possibly other electronic circuits.

Uses the Siglent SDG10x0 function generator together with the Rigol DS1052E
oscilloscope. The function generator generates a sine wave in the various
frequencies, the filter is connected between them and the oscilloscope is used
for measuring the response.


Installation and usage
----------------------

The program requires `setuptools` for installation. You can install it by
running `./setup.py install` (which may require root) or with `pip`. The
dependencies should be installed automatically from PyPI.

The signal generator's channel 1 should be connected to the filter's input and
the filter's output should be connected to the scope's channel 1. The signal
generator's sync out (on the back panel) should be connected to the scope's
external trigger input. Then you can run the analysis with::

    skardas start_frequency end_frequency

(substituting the appropriate frequency numbers in Hz)


TODO
----

In general order of importance.

- Test recent changes (new API, adaptive scales, responsive UI).

- Be more robust in case of resonant tank circuit (measure response
  frequency?)

- Multiple plot interface.

  * Phase measurement.
  * Distortion measurement.

- Upload to PyPI.
