from mat_loader import load_identifier
from csv_writer import write_files
from format_data import format_data
from sys import argv
from os import path


def format_mat_data(data_path, file_type):
    data = load_identifier(data_path or '')
    result = format_data(data, list(range(10)))
    write_files(data=result, file_type=file_type, shuffle_data=True)


if len(argv) > 1:
    project_path = argv[1]
    test_path = path.join(project_path, 'test')
    train_path = path.join(project_path, 'train')
    format_mat_data(test_path, 'test')
    format_mat_data(train_path, 'train')
else:
    print('Missing path to the bci data')


# print(format_trial(data[0], [1, 2, 3, 4, 5]))
# write_csv_files(data=data, file_name='test')
