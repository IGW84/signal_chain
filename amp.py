
import random

slope_list = ['negative', 'positive']

class Amp:
    def __init__(self,
                name,
                gain,
                offset,
                cmrr=80,
                gain_drift_temp=0, gain_drift_time=0,
                offset_drift_temp=0, offset_drift_time=0,
                ref_temperature=25,
                cmr_slope='positive',
                ):
        self.name = name
        self.gain = gain
        self.offset = offset
        self.cmrr = cmrr
        self.cmr_slope = cmr_slope
        self.gain_drift_temp = gain_drift_temp
        self.gain_drift_time = gain_drift_time
        self.offset_drift_temp = offset_drift_temp
        self.offset_drift_time = offset_drift_time
        self.ref_temperature = ref_temperature
        self.temperature = ref_temperature
        self.time = 0
        self.cmv = 0
    
    def __repr__(self):
        s = f'name: {self.name}\n'
        s += f'\tgain : {self.gain:.5f} temp drift (ppm/degC): {self.gain_drift_temp:.3f} time drift (ppm/1000hr): {self.gain_drift_time:.3f}\n'
        s += f'\toffset (mV): {self.offset:.3f} temp drift (uV/degC): {self.offset_drift_temp:.3f} time drift (uV/1000hr): {self.offset_drift_time:.3f}\n'
        s += f'\tCMRR: {self.cmrr} CMRR slope: {self.cmr_slope} Ref Temp: {self.ref_temperature}\n'
        return s

    def output(self, vin, cmv=None, temp=None, time=None):
        if cmv is None:
            cmv = self.cmv
        if temp is None:
            temp = self.temperature
        if time is None:
            time = self.time
        # gain
        gain_error_temp_ppm = (temp - self.ref_temperature) * self.gain_drift_temp
        gain_error_time_ppm = time/1000 * self.gain_drift_time
        gain_error_ppm = gain_error_temp_ppm + gain_error_time_ppm
        gain = self.gain * (1 + gain_error_ppm/1e6)
        # offset
        offset_error_temp_uV = (temp - self.ref_temperature) * self.offset_drift_temp
        offset_error_time_uV = time/1000 * self.offset_drift_time # time drift is given in ppm per 1000 hours
        offset = self.offset/1e3 + (offset_error_temp_uV + offset_error_time_uV)/1e6
        #common mode
        cm_error = cmv / 10**(self.cmrr/20)
        if self.cmr_slope == 'negative':
            cm_error = -cm_error
        return gain*vin + offset + cm_error

    def new(nom_settings, cal_method):
        s = nom_settings
        if cal_method == '1point':
            offset = 0.0
            gain = s['gain'] + random.uniform(-s['gain_accuracy'], s['gain_accuracy'])/100 # gain accuracies are in %
            cmrr = s['cmrr']
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])
        elif cal_method == '2point':
            offset = 0.0
            gain = s['gain']
            cmrr = s['cmrr']
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])
        elif cal_method == 'cm':
            offset = 0.0
            gain = s['gain']
            cmrr = s['cmrr'] + 10 # assume it improves CMRR by 10 dB
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])
        elif cal_method == 'temperature':
            offset = 0.0
            gain = s['gain']
            cmrr = s['cmrr']
            gain_drift_temp = 0.0
            offset_drift_temp = 0.0
        else:
            offset = random.uniform(-s['offset'], s['offset'])
            gain = s['gain'] * (1 + random.uniform(-s['gain_accuracy'], s['gain_accuracy'])/100)
            cmrr = s['cmrr']
            gain_drift_temp = random.uniform(-s['gain_drift_temp'], s['gain_drift_temp'])
            offset_drift_temp = random.uniform(-s['offset_drift_temp'], s['offset_drift_temp'])

        slope = random.choice(slope_list)
        gain_drift_time = random.uniform(-s['gain_drift_time'], s['gain_drift_time'])
        offset_drift_time = random.uniform(-s['offset_drift_time'], s['offset_drift_time'])
        amp = Amp(s['name'], gain, offset, cmrr,
                  gain_drift_temp, gain_drift_time,
                  offset_drift_temp, offset_drift_time,
                  s['ref_temp'], slope)
        return amp

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Amplifier model")
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=1000, help='Number of runs')
    parser.add_argument('--col',default='error',help='column to plot')

    args = parser.parse_args()

    amp_settings = {
        'name'              : 'INA157',
        'gain'              :  0.5,
        'gain_accuracy'     :  0.05,
        'offset'            :  0.5,
        'gain_drift_temp'   : 10,
        'gain_drift_time'   :  0,
        'offset_drift_temp' : 20,
        'offset_drift_time' :  0.34,
        'cmrr'              : 80,
        'ref_temp'          : 25,
    }

    vsteps    = [-2, -1, 0, 1, 2, 2.45]
    cmv_steps = [-3, -1, 1, 3]
    time_steps = [0, 1000]
    temp_steps = [10,25,45]

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    df = pd.DataFrame()

    print(f'{args.cal=}')

    temperature = 25
    cols = ['run', 'gain','offset','cmrr','gain drift temperature', 'gain drift time',
            'offset drift temperature', 'offset drift time','cmv','temperature','time',
            'voltage','output','error']

    slist = []
    run = 0
    total_runs = args.num_runs * len(temp_steps) * len(time_steps) * len(cmv_steps)
    for i in range(args.num_runs):
        amp = Amp.new(amp_settings, args.cal)
        for temp in temp_steps:
            amp.temperature = temp
            for t in time_steps:
                amp.time = t
                for cmv in cmv_steps:
                    run += 1
                    if run % 10 == 0:
                        print(str(run) + '/' + str(total_runs))
                    amp.cmv = cmv
                    for v in vsteps:
                        out = amp.output(v, cmv=cmv, temp=temp, time=t)
                        err = (v - out/amp_settings['gain']) * 1000 # error is in mV
                        data = [
                            run, amp.gain, amp.offset, amp.cmrr, amp.gain_drift_temp, amp.gain_drift_time,
                            amp.offset_drift_temp, amp.offset_drift_time, cmv, temp, t, v, out, err,
                            ]
                        # df = df.append(pd.Series(data, cols), ignore_index=True)
                        slist.append(data)
    print(str(run) + '/' + str(total_runs))

    df = pd.DataFrame(slist, columns = cols)
    xs = np.arange(-3.25, 3.75, 0.5)
    
    print(df)
    vin_to_plot = 2.0
    df2 = df[abs(df['voltage'] - vin_to_plot) < 0.001] # select but with a tolerance
    print(df2[args.col])
    plt.hist(df2[args.col], xs)

    plt.xlabel(args.col)  # Todo - pretty up this label and add units
    plt.ylabel('Count')
    plt.xticks(xs)
    plt.title(f'Distribution @ Vin={vin_to_plot}V')
    plt.show()

