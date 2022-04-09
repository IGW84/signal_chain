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
        self.__name = name
        self.__gain = gain
        self.__offset = offset
        self.__cmrr = cmrr
        self.__cmr_slope = cmr_slope
        self.__gain_drift_temp = gain_drift_temp
        self.__gain_drift_time = gain_drift_time
        self.__offset_drift_temp = offset_drift_temp
        self.__offset_drift_time = offset_drift_time
        self.__ref_temperature = ref_temperature
        self.__temperature = ref_temperature
        self.__time = 0
        self.__cmv = 0

    def get_gain(self):
        return self.__gain
    def set_gain(gain):
        self.__gain = gain
    temperature = property(get_gain, set_gain)

    def get_offset(self):
        return self.__offset
    def set_offset(self, offset):
        self.__offset = offset
    temperature = property(get_offset, set_offset)

    def get_temperature(self):
        return self.__temperature
    def set_temperature(self, temp):
        self.__temperature = temp
    temperature = property(get_temperature, set_temperature)

    def get_time(self):
        return self.__time
    def set_time(self, hours):
        self.__time = hours
    time = property(get_time, set_time)

    def get_cmv(self):
        return self.__cmv
    def set_cmv(self, volts):
        self.__cmv = volts
    cmv = property(get_cmv, set_cmv)

    def output(self, vin):
        # gain
        gain_error_temp_ppm = (self.__temperature - self.__ref_temperature) * self.__gain_drift_temp
        gain_error_time_ppm = self.__time/1000 * self.__gain_drift_time
        gain_error_ppm = gain_error_temp_ppm + gain_error_time_ppm
        gain = self.__gain * (1 + gain_error_ppm/1e6)
        offset_error_temp_uV = (self.__temperature - self.__ref_temperature) * self.__offset_drift_temp
        offset_error_time_uV = self.__time/1000 * self.__offset_drift_time # time drift is given in ppm per 1000 hours
        offset = (offset_error_temp_uV + offset_error_time_uV)/1e6
        cm_error = self.__cmv / 10**(self.__cmrr/20)
        if self.__cmr_slope == 'negative':
            cm_error = -cm_error
        return gain*vin + offset + cm_error


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Amplifier model")
    parser.add_argument('--cal','-c', default='none', help='Calibration setting: none, 1point, 2point, cm, temperature (default=none)')
    parser.add_argument('--num_runs','-n', type=int, default=1000, help='Number of runs')

    args = parser.parse_args()

    name = 'INA157'
    gain_nom = 0.5
    offset_max = 0.5
    cmrr_nom = 80
    cmrr_max = 1000
    gain_error = 0.05 # %
    gain_drift_temp_nom=10
    gain_drift_time_max=0
    offset_drift_temp_nom=20
    offset_drift_time_max=0.34
    ref_temperature=25
    slope_list = ['negative', 'positive']

    vsteps    = [-2, -1, 0, 1, 2, 2.45]
    cmv_steps = [-3, -1, 1, 3]
    time_steps = [0, 1000]
    temp_steps = [10,25,45]

    import random
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.DataFrame()

    gain_err_ratio = gain_error/100

    print(f'{args.cal=}')

    temperature = 25

    for i in range(args.num_runs):
        if args.cal == '1point':
            offset = 0.0
            gain = gain_nom + random.uniform(-gain_err_ratio, gain_err_ratio)
            cmrr = cmrr_nom
            gain_drift_temp = gain_drift_temp_nom
            offset_drift_temp = offset_drift_temp_nom
        elif args.cal == '2point':
            offset = 0.0
            gain = gain_nom
            cmrr = cmrr_nom
            gain_drift_temp = gain_drift_temp_nom
            offset_drift_temp = offset_drift_temp_nom
        elif args.cal == 'cm':
            offset = 0.0
            gain = gain_nom
            cmrr = cmrr_max
            gain_drift_temp = gain_drift_temp_nom
            offset_drift_temp = offset_drift_temp_nom
        elif args.cal == 'temperature':
            offset = 0.0
            gain = gain_nom
            cmrr = cmrr_max
            gain_drift_temp = 0.0
            offset_drift_temp = 0.0
        else:
            offset = random.uniform(-offset_max, offset_max)
            gain = gain_nom + random.uniform(-gain_err_ratio, gain_err_ratio)
            cmrr = cmrr_nom
            gain_drift_temp = gain_drift_temp_nom
            offset_drift_temp = offset_drift_temp_nom

        slope = random.choice(slope_list)
        gain_drift_time = random.uniform(-gain_drift_time_max, gain_drift_time_max)
        offset_drift_time = random.uniform(-offset_drift_time_max, offset_drift_time_max)
        amp = Amp(name, gain, offset, cmrr, gain_drift_temp, gain_drift_time, offset_drift_temp, offset_drift_time, ref_temperature, slope)

        cols = ['run', 'gain','offset','cmrr','gain drift temperature', 'gain drift time', 'offset drift temperature', 'offset drift time','cmv','temperature','time', 'voltage','output','error']
        run = 0
        for t in time_steps:
            amp.time = t
            for cmv in cmv_steps:
                run += 1
                if run % 10 == 0:
                    print('.')
                amp.cmv = cmv
                for v in vsteps:
                    out = amp.output(v)
                    err = v - out/gain_nom
                    data = [run, gain, offset, cmrr, gain_drift_temp, gain_drift_time, offset_drift_temp, offset_drift_time, cmv, temperature, t, v, out, err]
                    df = df.append(pd.Series(data, cols), ignore_index=True)
    
    print(df)
    vin_to_plot = 2.0
    df2 = df[abs(df['voltage'] - vin_to_plot) < 0.001] # select but with a tolerance
    print(df2['error'])
    plt.hist(df2['error'])

    # print(f'{type(out_list)=}')
    # print(f'{len(out_list)=}')
    # print(f'{type(err_list)=}')
    # print(f'{len(err_list)=}')
    # print(f'{err_list[-1]=}')
    # for es in err_list:

    #     plt.plot(vsteps,es)
    plt.xlabel('Error mV')
    plt.ylabel('Count')
    plt.title(f'Error Distribution @ Vin={vin_to_plot}V')
    plt.show()

