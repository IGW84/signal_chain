
import random


class ADC:
    def __init__(self,
                name,
                bits,          
                gain, offset,
                gain_drift_temp=0, gain_drift_time=0,
                offset_drift_temp=0, offset_drift_time=0,
                ref_temperature=25,
                ):
        self.name = name
        self.bits = bits
        self.gain = gain
        self.offset = offset
        self.gain_drift_temp = gain_drift_temp
        self.gain_drift_time = gain_drift_time
        self.offset_drift_temp = offset_drift_temp
        self.offset_drift_time = offset_drift_time
        self.ref_temperature = ref_temperature
        self.temperature = ref_temperature
        self.time = 0
    
    def __repr__(self):
        s = f'name: {self.name}\n'
        s += f'\tbits : {self.bits}\n'
        s += f'\tgain : {self.gain:.3f} temp drift (ppm/degC): {self.gain_drift_temp:.3f} time drift (ppm/1000hr): {self.gain_drift_time:.3f}\n'
        s += f'\toffset (mV): {self.offset:.3f} temp drift (uV/degC): {self.offset_drift_temp:.3f} time drift (uV/1000hr): {self.offset_drift_time:.3f}\n'
        s += f'\tRef Temp: {self.ref_temperature}\n'
        return s

    def sample(self, vin, vref, temp=None, time=None):
        if temp is None:
            temp = self.temperature
        if time is None:
            time = self.time

        #gain
        gain_error_temp_ppm = (temp - self.ref_temperature) * self.gain_drift_temp
        gain_error_time_ppm = time/1000 * self.gain_drift_time
        gain_error_ppm = gain_error_temp_ppm + gain_error_time_ppm
        gain = self.gain * (1 + gain_error_ppm/1e6)

        # offset
        offset_error_temp_uV = (temp - self.ref_temperature) * self.offset_drift_temp
        offset_error_time_uV = time/1000 * self.offset_drift_time # time drift is given in ppm per 1000 hours
        offset = self.offset/1e3 + (offset_error_temp_uV + offset_error_time_uV)/1e6
        # 'analog' chain output
        v_intermediate =  gain * vin + offset
        # Sampling
        if vref is None:
            vref = self.ref_voltage
        resolution = vref / (2**(self.bits-1) - 1)
        code_float = v_intermediate / resolution
        code = int(code_float)
        return (code, code_float)

    def new(nom_settings, cal_method):
        s = nom_settings
        if cal_method == '1point':
            gain = 1 + random.uniform(-s['gain_accuracy'], s['gain_accuracy'])/100 # accuracy is in %
            offset = 0.0
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])
        elif cal_method in ['2point', 'cm']:
            gain = 1.0
            offset = 0.0
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])
        elif cal_method == 'temperature':
            gain = 1.0
            offset = 0.0
            gain_drift_temp = 0.0
            offset_drift_temp = 0.0
        else:
            gain = 1 + random.uniform(-s['gain_accuracy'], s['gain_accuracy'])/100
            offset = random.uniform(-s['offset'], s['offset'])
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])

        gain_drift_time = random.uniform(-s['gain_drift_time'], s['gain_drift_time'])
        offset_drift_time = random.uniform(-s['offset_drift_time'], s['offset_drift_time'])
        amp = ADC(
                    s['name'], s['bits'],
                    gain, offset,
                    gain_drift_temp, gain_drift_time,
                    offset_drift_temp, offset_drift_time,
                    s['ref_temp'],
                )
        return amp

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Amplifier model")
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=1000, help='Number of runs')
    parser.add_argument('--col',default='Estimate Error (mV)',help='column to plot')
    parser.add_argument('--fixx','-x', action='store_true', help='If given, histogram bins are fixed')

    args = parser.parse_args()

    adc_settings = {
        'name' : 'ADS1178',
        'bits' : 16,
        'gain_accuracy' : 0.5,
        'offset' : 2,
        'gain_drift_temp' : 2,
        'gain_drift_time' : 0,
        'offset_drift_temp' : 2,
        'offset_drift_time' : 0,
        'ref_temp' : 25,
    }


    vsteps    = [-1, -.5, 0, .5, 1, 1.225]
    time_steps = [0]
    # time_steps = [0, 1000]
    # temp_steps = [10,25,45]
    temp_steps=[25]

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    df = pd.DataFrame()

    print(f'{args.cal=}')

    temperature = 25
    cols = ['run', 'gain', 'offset','gain drift temperature', 'gain drift time',
            'offset drift temperature', 'offset drift time','temperature','time',
            'voltage','code float', 'code', 'Estimated Voltage', 'Estimate Error (mV)']
    vref = 2.5
    resolution = vref/(2**(adc_settings['bits'] - 1) - 1)
    
    slist = []

    run = 0
    total_runs = args.num_runs * len(temp_steps) * len(time_steps)
    for i in range(args.num_runs):
        adc = ADC.new(adc_settings, args.cal)
        if i in [0,7,19]:
            print(adc)
        for temp in temp_steps:
            for t in time_steps:
                run += 1
                if run % 10 == 0:
                    print(str(run) + '/' + str(total_runs))
                for v in vsteps:
                    (code, code_float) = adc.sample(v, vref, temp, t)
                    estimated_v = code * resolution
                    estimate_err = (v - estimated_v)*1000
                    data = [
                            run, adc.gain, adc.offset,
                            adc.gain_drift_temp, adc.gain_drift_time,
                            adc.offset_drift_temp, adc.offset_drift_time,
                            temp, t,
                            v, code_float, code, estimated_v, estimate_err
                            ]
                    slist.append(data)
    print(str(run) + '/' + str(total_runs))

    df = pd.DataFrame(slist, columns = cols)
    if args.fixx:
        xs = np.arange(-8.5, 9.5, 1.0)
    else:
        xs = None   
    
    vin_to_plot = 1.0
    df2 = df[abs(df['voltage'] - vin_to_plot) < 0.001] # select but with a tolerance
    print(df2[args.col])
    plt.hist(df2[args.col], xs)

    plt.xlabel(args.col)  # Todo - pretty up this label and add units
    plt.ylabel('Count')
    plt.xticks(xs)
    plt.title(f'Distribution @ Vin={vin_to_plot}V')
    plt.show()

