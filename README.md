* Amp+ADC+Ref Chain Production Error Spread

Copyright (C) 2024 Ian Wilson of Considered Solutions Pty Ltd.

Author: Ian Wilson
Email: i.wilson.aust@gmail.com

Python CLI application and helpers that calculates the production (voltage) error spread for a signal chain of Amplifier & ADC & Reference.

These scripts were written for my own use and have not necessarily been fully validated. Anyone using this work does so completely at their own risk. 

These scripts are release under the GPL V3 license.

## Models
In the models the values are floating point and the following units are used:
- gains are as ratio
- accuracys units are percentage
- gain temperature drift units are ppm per degC
- time drift units are are ppm per 1000 hours.
- offset units are mV
- offset temperature drifts are uV per degC
- offset time drift units are uV per 1000 hours
- CMRR units are dB
- Reference hysterisis units are ppm

Amplifier model is:
- gain
- offset
- CMRR (defaults to 80 dB if not given)
- Gain drift with temperature (gain_drift_temp) defaults to 0
- Gain drift with time (gain_drift_time) defaults to 0
- Offset drift with temperature (offset_drift_temp) defaults to 0
- Offset drift with time (offset_drift_time) defaults to 0
- Reference temperature for gain and offset values (ref_temperature) defaults to 25
- CMRR slope (cmr_slope) 'positive' or 'negative defaults to 'positive',

Voltage Reference Model:
- Voltage (initial_voltage)
- Drift with temperature (drift_temp) defaults to 0
- Drift with time (drift_time) defaults to 0
- Hysterisis defaults to 0
- Reference temperature for voltage value (ref_temperature) defaults to 25

ADC Model:
- Number of bits        
- Gain
- Offset
- Gain drift with temperature (gain_drift_temp) defaults to 0
- Gain drift with time (gain_drift_time) defaults to 0,
- Offset drift with temperature (offset_drift_temp) defaults to 0
- Offset drift with time (offset_drift_time) defaults to 0
- Reference temperature for gain and offset values (ref_temperature) defaults to 25

## Configuration File
The signal chain is defined by a configuration file.  See examples for format.

Note: The example configurations may include a [CONTROL] section. This is deprecated and no longer used.

## Accuracy Script
`accuracy.py` is the basic analysis engine.  The `process` function within runs the simulation across the common mode raange and number of runs given required (passed in). Results are plotted (which can then be saved).

`python accuracy.py --help` will show the possible command line options and usage.

## Compare Script
'compare.py` calls `accuracy.process` on a number of different calibration scenarios and plots the comparison.

The `--cal` command line option takes a comma seperated list of calibration methods for example:
`python compare.py basic.cfg --cal none,2point,cm`

Important Note: as at 2024/04/05 there is a discrepancy between calling compare with no calibration (`--cal none`) for `accuracy` and for `compare`. This is unexpected. Results of `compare` with `none` calibration included should not be trusted.

## Calibration Methods
The factory calibration method used can be set on the command line.

(Any references to the calibration method in the configuration file are ignored. This configuration file setting should no longer be used.)

Possible calibration options are:
`none`: no calibration is assumed
`1point`: offset voltages are assumed to be read and stored during factory calibration. Simulation sets offsets to 0 mV.
`2point`: gain error and offset voltages are assumed to be calibrated (at 0 volts common mode voltage only). Simulation sets gain error to 0 and offsets to 0 mV.
`cm`: gain error and offset voltages assumed to be calibrated at multiple points across the common mode range. The correction is crude and simply increases the models CMRR value by 10 dB.
`temperature`: gain error and offset voltages assumed to be calibrated across multiple temperatures (but this does not include any common mode effect calibration (i.e. the effect itroduced by the `cm` method is not also included.)
