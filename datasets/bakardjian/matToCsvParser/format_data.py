
def format_data(data, electrode_ids):
    data_keys = data.keys()
    formatted_data = {}
    for key in data_keys:
        formatted_data[key] = []
        for trial in data[key]:
            formatted_data[key].append(format_trial(trial, electrode_ids))
    return formatted_data

def format_trial(trial, electrode_ids=list()):
    formatted_data = {
        'data': {},
        'duration': trial['duration'],
        'identifier': trial['identifier'],
        'start_delay': trial['start_delay'],
    }
    eeg_data = trial['data']['EEGdata']
    if len(electrode_ids) == 0:
        electrode_ids = list(range(eeg_data.shape[0]))

    last_data_index = get_last_useable_index(trial=trial)
    formatted_data['sample_count'] = last_data_index + 1
    for electrode_id in electrode_ids:
        formatted_data['data'][electrode_id] = eeg_data[electrode_id][0:last_data_index]
    return formatted_data


def get_last_useable_index(trial, max_length=21):
    cut_length = trial['length'] - max_length
    delete_count = 0
    if cut_length > 0:
        delete_count = cut_length / (1.0 / 256)
    return int(trial['sample_count'] - delete_count)

# test = trim_train_data({'length': 24.7265625})
# print(str((6330 - test) * (1.0/256)))