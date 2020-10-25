import scipy.io as sio
import os

freq_list = {
    8: 0x00008101,
    14: 0x00008102,
    28: 0x00008103,
}


def get_mat_files(folder):
    root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), folder)
    files = os.listdir(root_path)
    paths = map(lambda file: os.path.join(root_path, file), files)
    filtered = list(filter(lambda file: file.endswith('.MAT') is True, paths))
    return filtered


def create_stim_dict(data, freq):
    sample_count = data['EEGdata'].shape[1]
    length = (1.0/256) * sample_count

    return {
        'freq': freq,
        'data': data,
        'length': length,
        'sample_count': sample_count,
        'start_delay': 5,
        'identifier': freq_list[freq],
        'duration': 15,
    }

def load_mat_files(paths):
    files = list(map(lambda path: sio.loadmat(path), paths))
    return files


def create_sims(folder, freq):
    files = get_mat_files(folder)
    return list(map(lambda data: create_stim_dict(freq=freq, data=data), files))


def load_identify_data(identifier, folder):
    return list(map(lambda file: create_stim_dict(data=file, freq=identifier), load_mat_files(get_mat_files(folder))))


def load_identifier(data_folder):
    return {
        '8': load_identify_data(8, os.path.join(data_folder, '8Hz')),
        '14': load_identify_data(14, os.path.join(data_folder, '14Hz')),
        '28': load_identify_data(28, os.path.join(data_folder, '28Hz')),
    }