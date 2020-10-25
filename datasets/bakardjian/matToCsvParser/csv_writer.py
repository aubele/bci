import csv
from os import path
from random import shuffle

def write_files(data, file_type, shuffle_data=False):
    signal_writer = csv_writer(path.join('csv', file_type + '_signal.csv'), gen_signal_header(data))
    signal_writer.__next__()
    stim_writer = csv_writer(path.join('csv', file_type + '_stim.csv'), ['Time (s)', 'Identifier', 'Duration'])
    stim_writer.__next__()
    start_time = 0

    trials = extract_trials(data)
    if shuffle_data:
        shuffle(trials)

    for trial in trials:
        start_time = write_trial(trial=trial, start_time=start_time, signal_writer=signal_writer, stim_writer=stim_writer)
    stim_writer.send([start_time, 0x00008002, 0])

def extract_trials(data):
    trials = []
    data_keys = data.keys()
    for key in data_keys:
        for trial in data[key]:
            trials.append(trial)
    return trials


def write_trial(trial, start_time, signal_writer, stim_writer):
    stim_writer.send([start_time + trial['start_delay'], trial['identifier'], trial['duration']])
    write_signal_data(trial['data'], trial['sample_count'], signal_writer, start_time)
    return start_time + 21

def write_signal_data(electrodes, length, writer, start_time):
    for x in range(length-1):
        row = [(1/256 * x) + start_time]
        for electrode in electrodes.keys():
            row.append(electrodes[electrode][x])
        if x == 0:
            row.append('256')
        writer.send(row)


def gen_signal_header(data):
    trial = data[list(data.keys())[0]][0]
    header = ['Time (s)']
    for x in range(1, len(trial['data'])+1):
        header.append('Channel ' + str(x))
    header.append('Sampling Rate')
    return header


def csv_writer(file_name, header):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        while True:
            row = yield
            writer.writerow(row)