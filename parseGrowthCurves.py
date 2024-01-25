import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys


substrates = {
    'GLC': [list(range(1, 5)), 1],
    'TD01': [list(range(5, 9)), 2],
    'TD03': [list(range(9, 13)), 3],
    'PD': [list(range(13, 17)), 7],
    'LT': [list(range(17, 21)), 6],
    'IM': [list(range(21, 25)), 5],
    'RMF': [list(range(25, 29)), 4],
    'MIX': [list(range(29, 33)), 0]
}


def meltDataFrame(substrates):
    data = glob.glob('data/*.xlsx')
    for d in data:
        key = os.path.basename(d.split('.')[0])
        day = key.split('_')[1]
        plate = key.split('_')[3]
        df = pd.read_excel(d, sheet_name='Sheet9')
        timevalues = [((v.hour * 60 + v.minute) * 60 + v.second)
                      for v in df['Time'].values.tolist()]
        output_name = f"{key}.txt"
        with open(output_name, 'w') as out:
            for count, col in enumerate(df.columns):
                cval = col.split('.')[0]
                if count == 0:
                    pass
                else:
                    for substrate in substrates:
                        if count in substrates[substrate][0]:
                            current_sub = substrate
                    values = [timevalues, df[col].values.tolist(),
                              [current_sub] * len(df[col]), [cval] * len(df[col]), [day] * len(df[col]), [plate] * len(df[col])]
                    for v1, v2, v3, v4, v5, v6 in zip(values[0], values[1], values[2], values[3], values[4], values[5]):
                        writeline = '\t'.join([str(v)
                                               for v in [v1, v2, v3, v4, v5, v6]]) + '\n'
                        out.write(writeline)
    return 0


def getGrowthIntervalFromFull(all_times, all_values):
    # Step 1: create a window of size N and get the slope
    start_index = 0
    start_growth_time = all_times[0]
    start_growth_value = all_values[0]
    steps = 0
    step_threshold_start = 7
    window_size = 3
    window_end = len(all_values) - (window_size - 1)
    for window in range(window_end):
        current_values = all_values[window:window + window_size]
        if current_values[-1] > current_values[0]:
            if steps == 0:
                seed_time = all_times[window]
                seed_value = all_values[window]
                seed_index = window
            steps += 1
        else:
            steps = 0
        if steps > step_threshold_start:
            start_growth_time, start_growth_value = seed_time, seed_value
            start_index = seed_index
            break
    steps = 0
    step_threshold_end = 2
    window = 2
    for window in range(start_index, window_end):
        current_values = all_values[window:window + window_size]
        # Below, we can attenuate the ramp rate for better end prediction
        if current_values[0] > current_values[-1]:
            if steps == 0:
                seed_time = all_times[window]
                seed_value = all_values[window]
                seed_index = window
            steps += 1
        else:
            steps = 0
        if steps > step_threshold_end:
            end_growth_time, end_growth_value = seed_time, seed_value
            end_index = seed_index
            return [start_index, end_index, start_growth_time, start_growth_value,
                    end_growth_time, end_growth_value]
    end_index = window
    # Below, since > 24 hours, need to manually specify 24 hours + 7 seconds
    end_growth_time, end_growth_value = 80000, all_values[-1]
    return [start_index, end_index, start_growth_time, start_growth_value,
            end_growth_time, end_growth_value]


def getMuFromLists(times, values):
    max_slope = 0
    max_time = 0
    for count in range(len(times) - 6):
        x_delta1 = times[count + 1] - times[count]
        y_delta1 = values[count + 1] - values[count]
        x_delta2 = times[count + 2] - times[count + 1]
        y_delta2 = values[count + 2] - values[count + 1]
        x_delta3 = times[count + 3] - times[count + 2]
        y_delta3 = values[count + 3] - values[count + 2]
        x_delta4 = times[count + 4] - times[count + 3]
        y_delta4 = values[count + 4] - values[count + 3]
        x_delta5 = times[count + 5] - times[count + 4]
        y_delta5 = values[count + 5] - values[count + 4]
        x_delta6 = times[count + 6] - times[count + 5]
        y_delta6 = values[count + 6] - values[count + 5]
        slope1 = y_delta1 / x_delta1
        slope2 = y_delta2 / x_delta2
        slope3 = y_delta3 / x_delta3
        slope4 = y_delta4 / x_delta4
        slope5 = y_delta5 / x_delta5
        slope6 = y_delta6 / x_delta6
        slope = (slope1 + slope2 + slope3 + slope4 + slope5 + slope6) / 6
        if slope > max_slope:
            max_slope = slope
            max_time = times[count + 3]
    return [max_slope, max_time]


def plotCurve(x, y, start, end, mu, label):
    plt.scatter(x=x, y=y, label=label)
    plt.axhline(y=start, color='r', linestyle='-')
    plt.axhline(y=end, color='r', linestyle='-')
    plt.axvline(x=mu, color='b', linestyle='-')
    plt.title(label)
    plt.savefig(f"PyPlots/{label}.png")
    plt.clf()
    plt.cla()
    plt.close()
    return 0


def meltDataFrameDeltas(substrates, plot):
    data = glob.glob('data/Day_*.xlsx')
    for d in data:
        key = os.path.basename(d.split('.')[0])
        day = key.split('_')[1]
        plate = key.split('_')[3]
        df = pd.read_excel(d, sheet_name='Sheet9')
        output_name = f"{key}-DELTA-Passages-All.tab"
        with open(output_name, 'w') as out:
            for count, col in enumerate(df.columns):
                cval = col.split('.')[0]
                if count == 0:
                    pass
                else:
                    pass
                    for substrate in substrates:
                        if count in substrates[substrate][0]:
                            current_sub = substrate
                            complexity = substrates[substrate][1]
                    all_times = [((v.hour * 60 + v.minute) * 60 + v.second)
                                 for v in df['Time'].values.tolist()]
                    all_values = np.log10(df[col].values.tolist())
                    start_index, end_index, start_growth_time, start_growth_value, end_growth_time, end_growth_value = getGrowthIntervalFromFull(
                        all_times, all_values)
                    growth_times = all_times[start_index:end_index]
                    growth_values = all_values[start_index:end_index]
                    max_slope, max_time = getMuFromLists(
                        growth_times, growth_values)
                    start = float(all_values[start_index])
                    delta = float(all_values[end_index] - start)
                    values = [cval, current_sub, complexity, delta,
                              day, plate, max_time, max_slope, start_growth_time, start_growth_value, end_growth_time, end_growth_value]
                    writeline = '\t'.join(str(v) for v in values) + '\n'
                    out.write(writeline)
                    # Savefig to look at
                    label = f"{day}-{plate}-{cval}-{current_sub}"
                    print(f'Now plotting: {label}')
                    if plot:
                        plotCurve(all_times, all_values, all_values[start_index],
                                  all_values[end_index], max_time, label)
    return 0


meltDataFrameDeltas(substrates, plot=True)
