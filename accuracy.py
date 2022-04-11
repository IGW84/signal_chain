
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import argparse
import configparser as cp
from amp import Amp
from ref import Reference
# from adc import ADC
import random


def new_amp(amp_settings, temperature, time, cmv):
    s = amp_settings
    gain_err_temp_ppm  = random.uniform(-s.gain_drift_temp  , -s.gain_drift_temp   ) * (temperature - s['ref_temp'])
    gain_err_temp_ppm  = random.uniform(-s.gain_drift_time  , -s.gain_drift_time   ) * (time/1000)
    offset_err_temp_uV = random.uniform(-s.offset_drift_temp, -s.offset_drift_temp ) * (temperature - s['ref_temp'])
    offset_err_temp_uV = random.uniform(-s.offset_drift_time, -s.offset_drift_time ) * (time/1000)
    

    gain = s.
    amp = Amp(s.name,)
    return amp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monte-Carlo analysis of basic gain, ADC and reference signal chain")
    parser.add_argument('config', help=f'Config file')
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=100, help='Number of runs')

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
    print(f'{amp_settings['name']=}')
    print(f'{ref_settings['name']=}')
    print(f'{adc_settings['name']=}')

    sys_gain_nom = amp_gain_nom

    cmv_steps = new_func(cfg)
    v_steps = [float(f) for f in cfg['SYSTEM']['voltage_steps'].split(',')]
    temp_steps = [float(f) for f in cfg['SYSTEM']['temperature_steps'].split(',')]
    time_steps = [float(f) for f in cfg['SYSTEM']['time_steps'].split(',')]

    df = pd.DataFrame()

    cols = ['run','', 'amp']
    run = 0
    for i in range(args.num_runs):
    for cmv in cmv_steps:
        for t in temp_steps:
            for tm in time_steps:
                run += 1
                amp = Amp.new(amp_settings, args.cal)
                ref = Reference(ref_settings, args.cal)
                for v in v_steps:
                    out = amp.output(v)
                    err = v - out/gain_nom
                    data = [run, gain, gain_error, offset, cmrr, gain_drift_temp, gain_drift_time, offset_drift_temp, offset_drift_time, cmv, temperature, t, v, out, err]
                    df = df.append(pd.Series(data, cols), ignore_index=True)


    # df = estimateValues(args.R0, args.R0tol, args.Beta, args.Betatol,
    #                 args.Rpu, args.Rputol, args.T0,
    #                 args.Tmin, args.Tmax, args.Tstep,
    #                 args.vcc, args.vcctol,
    #                 )

    # if(args.voltage):
    #     plot_voltages(df, tolerences=(args.R0tol,args.Betatol,args.Rputol, args.vcctol), annotate=args.annotate)
    # else:
    #     plot_errors(df, tolerences=(args.R0tol,args.Betatol,args.Rputol, args.vcctol), annotate=args.annotate)




