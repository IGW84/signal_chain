
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import argparse
import configparser as cp
from amp import Amp
from ref import Reference
from adc import ADC
import random
import numpy as np

def process(amp_settings, ref_settings, adc_settings, cmv_steps, v_steps, temp_steps, time_steps, cal_method='none', num_runs=10):

    sys_gain_nom = amp_settings['gain'] # todo

    df = pd.DataFrame()

    ideal_resolution = ref_settings['voltage'] / (2**(adc_settings['bits']-1)-1)

    slist = []

    cols = [
        'Run', 'CMV', 'Temperature', 'Time', 'Input Voltage',
        'Amp Gain Nominal', 'Amp Gain', 'Amp Offset (mV)', 'Amp Vout', 'Amp Error (mV)',
        'Ref V Nominal', 'Ref V', 'Ref Err (mV)',
        'ADC Offset', 'ADC Code (float)', 'ADC Code',
        'System Estimate', 'System Error (mV)', 'Cal Method']
    run = 0
    total_runs = num_runs * len(cmv_steps) * len(time_steps) * len(temp_steps)
    for i in range(num_runs):
        amp = Amp.new(amp_settings, cal_method)
        ref = Reference.new(ref_settings, cal_method)
        adc = ADC.new(adc_settings, cal_method)
        for cmv in cmv_steps:
            amp.cmv = cmv
            for t in temp_steps:
                amp.temperature = t
                for tm in time_steps:
                    run += 1
                    if run % 10 == 0:
                        print(str(run) + '/' + str(total_runs))
                    amp.time = tm
                    v_ref = ref.calc_voltage(temp=t, time=tm)
                    v_ref_err = (ref_settings['voltage'] - v_ref) * 1000   # errors in mV
                    for v in v_steps:
                        v_amp = amp.output(v)
                        v_amp_err = v_amp / amp_settings['gain']
                        (code, code_float) = adc.sample(v_amp, v_ref, t, tm)

                        v_estimate = (code * ideal_resolution) / sys_gain_nom
                        err = (v - v_estimate) * 1000  # errors in mV
                        data = [
                            run,
                            cmv, t, tm, v,
                            amp_settings['gain'], amp.gain, amp.offset, v_amp, v_amp_err,
                            ref_settings['voltage'], v_ref, v_ref_err,
                            adc.offset, code_float, code,
                            v_estimate, err,
                            cal_method,
                        ]
                        slist.append(data) # todo - this is slow and gets slower as df grows. Consider keeping list of pd.Series and making df in one hit
    print(str(run) + '/' + str(total_runs))

    df = pd.DataFrame(slist, columns = cols)

    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monte-Carlo analysis of basic gain, ADC and reference signal chain")
    parser.add_argument('config', help=f'Config file')
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=10, help='Number of runs')
    parser.add_argument('--col',default='System Error (mV)',help='column to plot')

    args = parser.parse_args()

    cfg = cp.ConfigParser()
    cfg.read(args.config)

    cmv_steps = [float(f) for f in cfg['SYSTEM']['cmv_steps'].split(',')]
    v_steps = [float(f) for f in cfg['SYSTEM']['voltage_steps'].split(',')]
    temp_steps = [float(f) for f in cfg['SYSTEM']['temperature_steps'].split(',')]
    time_steps = [float(f) for f in cfg['SYSTEM']['time_steps'].split(',')]

    amp_settings = {
        'name' : cfg['DIFFAMP']['Name'],
        'gain' : float(cfg['DIFFAMP']['Gain']),
        'gain_accuracy' : float(cfg['DIFFAMP']['GainError']),
        'offset' : float(cfg['DIFFAMP']['VOffsetMax']),
        'gain_drift_temp' : float(cfg['DIFFAMP']['GainDriftTemp']),
        'gain_drift_time' : float(cfg['DIFFAMP']['GainDriftTime']),
        'offset_drift_temp' : float(cfg['DIFFAMP']['VOffsetDriftTemp']),
        'offset_drift_time' : float(cfg['DIFFAMP']['VOffsetDriftTime']),
        'cmrr' : float(cfg['DIFFAMP']['CMRR']),
        'ref_temp' : float(cfg['DIFFAMP']['ReferenceTemperature']),
    }

    ref_settings = {
        'name' : cfg['REFERENCE']['Name'],
        'voltage' : float(cfg['REFERENCE']['Voltage']),
        'accuracy' : float(cfg['REFERENCE']['Accuracy']),
        'drift_temp' : float(cfg['REFERENCE']['DriftTemp']),
        'drift_time' : float(cfg['REFERENCE']['DriftTime']),
        'hysterisis' : float(cfg['REFERENCE']['Hysterisis']),
        'ref_temp' : float(cfg['REFERENCE']['ReferenceTemperature']),
    }

    adc_settings = {
        'name' : cfg['ADC']['Name'],
        'bits' : float(cfg['ADC']['Bits']),
        'gain_accuracy' : float(cfg['ADC']['GainError']),
        'offset' : float(cfg['ADC']['VOffsetMax'])    ,
        'gain_drift_temp' : float(cfg['ADC']['GainDriftTemp']),
        'gain_drift_time' : float(cfg['ADC']['GainDriftTime']),
        'offset_drift_temp' : float(cfg['ADC']['VOffsetDriftTemp']),
        'offset_drift_time' : float(cfg['ADC']['VOffsetDriftTime']),
        'ref_temp' : float(cfg['ADC']['ReferenceTemperature']),
    }

    print(f'{cmv_steps=}')
    print(f'{v_steps=}')
    print(f'{temp_steps=}')
    print(f'{time_steps=}')
    print(f'{amp_settings["name"]=}')
    print(f'{ref_settings["name"]=}')
    print(f'{adc_settings["name"]=}')

    sys_gain_nom = amp_settings['gain'] # todo

    cmv_steps = [float(f) for f in cfg['SYSTEM']['cmv_steps'].split(',')]
    v_steps = [float(f) for f in cfg['SYSTEM']['voltage_steps'].split(',')]
    temp_steps = [float(f) for f in cfg['SYSTEM']['temperature_steps'].split(',')]
    time_steps = [float(f) for f in cfg['SYSTEM']['time_steps'].split(',')]

    df = process(amp_settings, ref_settings, adc_settings, cmv_steps, v_steps, temp_steps, time_steps, args.cal, args.num_runs)

    print(df)
    xs = np.arange(-7.25, 7.75, 0.5)
    vin_to_plot = 6.0
    df2 = df[abs(df['Input Voltage'] - vin_to_plot) < 0.001] # select but with a tolerance
    print(df2[args.col])
    plt.hist(df2[args.col], xs)

    plt.xlabel(args.col)  # Todo - pretty up this label and add units
    plt.ylabel('Count')
    plt.title(f'Distribution @ Vin={vin_to_plot}V')
    plt.show()


