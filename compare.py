
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import argparse
import configparser as cp
import accuracy
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monte-Carlo analysis of basic gain, ADC and reference signal chain")
    parser.add_argument('config', help=f'Config file')
    parser.add_argument('--cal','-c', default='none', help='Calibration settings - list of: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=10, help='Number of runs')
    parser.add_argument('--col',default='System Error (mV)',help='column to plot')
    # parser.add_argument('--fixx','-x', action='store_true', help='If given, histogram bins are fixed')
    parser.add_argument('--minx', type=float, help='Left hand edge of left hand bin')
    parser.add_argument('--maxx', type=float, help='Left hand edge of right hand bin')
    parser.add_argument('--bins', type=int, default=21, help='Number of bins (default=21)')

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

    cal_list = args.cal.split(',')

    df_list = []

    for cal in cal_list:
        df = accuracy.process(amp_settings, ref_settings, adc_settings, cmv_steps, v_steps, temp_steps, time_steps, cal, args.num_runs)
        df_list.append(df)
        print(f'{len(df)=}')

    plt.figure(figsize=(12,4))
    plt.tight_layout()
    plt.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.9)

    if (args.minx is not None) and (args.maxx is not None):
        xs = np.arange(args.minx, args.maxx, (args.maxx - args.minx)/args.bins)
    else:
        xs = None

    vin_to_plot = 6.0
    for cal, df in zip(cal_list, df_list):
        df2 = df[abs(df['Input Voltage'] - vin_to_plot) < 0.001] # select but with a tolerance
        df3 = df2[df2['Cal Method'] == cal]
        if xs is not None:
            plt.hist(df3[args.col], xs, alpha=0.5, label=cal)
        else:
            plt.hist(df3[args.col], alpha=0.5, label=cal, bins = args.bins)


    plt.xlabel(args.col)  # Todo - pretty up this label and add units
    plt.xticks(xs, fontsize='x-small')
    plt.ylabel('Count')
    plt.title(f'Distribution @ Vin={vin_to_plot}V')
    plt.legend()
    plt.show()


