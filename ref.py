
import random

class Reference:

    def __init__(self,
                name,
                initial_voltage,
                drift_temp=0,
                drift_time=0,
                hysterisis=0,
                ref_temperature = 25
                ):
        self.name = name
        self.voltage = initial_voltage
        self.drift_temp = drift_temp
        self.drift_time = drift_time
        self.hysterisis = hysterisis
        self.ref_temperature = ref_temperature
        self.temperature = ref_temperature
        self.time = 0

    def __repr__(self):
        s = f'name: {self.name}\n'
        s += f'\tvoltage : {self.voltage:.5f} temp drift (ppm/degC): {self.drift_temp:.3f} time drift (ppm/1000hr): {self.drift_time:.3f}\n'
        s += f'\thysterisis (ppm): {self.hysterisis} Ref Temp: {self.ref_temperature}\n'
        return s


    def calc_voltage(self, temp=None, time=None):
        if temp is None:
            temp = self.temperature
        if time is None:
            time = self.time
        drift_temp_ppm = (temp - self.ref_temperature) * self.drift_temp
        drift_time_ppm = time/1000 * self.drift_time # time drift is given in ppm per 1000 hours
        error_ppm = drift_temp_ppm + drift_time_ppm
        v = self.voltage * (1 + error_ppm/1e6)
        return v
    
    def new(nom_settings, cal_method):
        s = nom_settings
        if cal_method in ['1point', '2point', 'cm']:
            voltage = s['voltage']
            drift_temp = random.uniform(-s['drift_temp'], s['drift_temp'])
        elif cal_method == 'temperature':
            voltage =  s['voltage']
            drift_temp = 0.0
        else:
            voltage =  s['voltage'] * (1 + random.uniform(-s['accuracy'], s['accuracy'])/100) # accuracy is in percent
            drift_temp = random.uniform(-s['drift_temp'], s['drift_temp'])
        drift_time = random.uniform(-s['drift_time'], s['drift_time'])
        ref = Reference(s['name'], voltage, drift_temp, drift_time, s['ref_temp'])
        return ref

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Amplifier model")
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=1000, help='Number of runs')
    parser.add_argument('--col',default='error',help='column to plot')

    args = parser.parse_args()

    ref_settings = {
        'name'       : 'ADR431A',
        'voltage'    : 2.5,
        'accuracy'   : 0.12, # %
        'drift_temp' : 10,   # ppm per deg C
        'drift_time' : 40,   # ppm in 1st 1000 hours
        'hysterisis' : 20,   # ppm 
        'ref_temp'   : 25,   # deg C
    }


    time_steps = [0, 1000]
    temp_steps = [10,25,45]

    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    df = pd.DataFrame()

    print(f'{args.cal=}')

    temperature = 25

    slist = []

    run = 0
    total_runs = args.num_runs * len(time_steps) * len(temp_steps)

    cols = ['run', 'voltage nominal','drift temperature', 'drift time', 'temperature','time', 'voltage','error']
    run = 0
    for i in range(args.num_runs):
        ref = Reference.new(ref_settings, args.cal)
        for t in time_steps:
            ref.time = t
            for temp in temp_steps:
                run += 1
                if run % 10 == 0:
                    print(str(run) + '/' + str(total_runs))
                v = ref.calc_voltage(temp=temp, time=t)
                err = (ref_settings['voltage'] - v) * 1000  # error in mV
                data = [run, ref.voltage, ref.drift_temp, ref.drift_time, temp, t, v, err]
                slist.append(data)
                # df = df.append(pd.Series(data, cols), ignore_index=True)
    print(str(run) + '/' + str(total_runs))

    df = pd.DataFrame(slist, columns = cols)
    xs = np.arange(-5.25, 5.25, 0.5)
    plt.hist(df[args.col], xs)

    plt.xlabel(args.col)
    plt.ylabel('Count')
    plt.xticks(xs)
    plt.title(f'Distribution')
    plt.show()

