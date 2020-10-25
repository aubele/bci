#!/usr/bin/env python3

"""
Generate csv-Files for OpenVIBE
Format documentation: http://openvibe.inria.fr/documentation/1.2.0/Doc_BoxAlgorithm_CSVFileReader.html
Data: http://bci.med.tsinghua.edu.cn/download.html

Creates 4 files: 2 for training, 2 for testing
The 2 files are respectively
- One containing the signal data
- One containing the stimulations

Files are created inside the configured csvPath
"""

import scipy.io
import os
import csv
import json

# local file stimulator_stim_codes.py
import stimulator_stim_codes as stim_codes


__author__ = "Philipp Weber"
__email__ = "Philipp.Weber@hs-augsburg.de"


class Settings:
    def __init__(self):
        self.frequencyValues = (9, 11, 13.2)
        """frequencies of which recordings are included, between 8 and 15.8 hz in 0.2 steps"""

        self.twentyTwentySpots = ('PZ', 'PO3', 'PO4', 'O1', 'Oz', 'O2', 'PO7', 'PO8')
        """positions of the desired electrodes"""

        self.subjects = (1,)
        """tuple of subjects, e. g. (1,2,3,6). Each *.mat file corresponds to a subject"""

        self.trainBlocks = tuple(range(4))
        """tuple of blocks (trials) which are used in the training files"""

        self.testBlocks = (4, 5)
        """tuple of blocks (trials) which are used in the test files"""

        self.dataDir = "data" + os.sep
        """path which should contain the .mat files"""

        self.csvDir = "csv" + os.sep
        """output directory"""

        if not os.path.exists(self.csvDir):
            os.mkdir(self.csvDir)
        if not os.path.exists(self.dataDir):
            os.mkdir(self.dataDir)

    def get_channels(self):
        """
        :return: the channels for the selected electrode positions
        """
        return [twentyTwentyIndex[tt_spot] for tt_spot in self.twentyTwentySpots]

    def get_frequencies(self):
        """
        :return: the Frequency instances for the selected electrode positions
        """
        frequencies = []
        for i, value in enumerate(self.frequencyValues):
            frequencies.append(Frequency(value, stim_codes.OVTK_StimulationId_Label_01 + i))
        return frequencies


class Constants:
    """
    from Readme.txt
    """
    samplingRate = 250  # samples per second
    signalLength = 6  # seconds
    signalOffset = 0.5  # seconds
    stimLength = 5  # seconds


def write_data(settings):
    """
    Extract data and write them to csv readable to OpenVibe.
    Also create a JSON document describing the Data.
    :param settings: Instance of settings class describing the desired data and output dir
    """
    try:
        # write the training data
        write_data_stim_files(
            settings.subjects,
            settings.get_channels(),
            settings.get_frequencies(),
            settings.trainBlocks,
            settings.dataDir,
            settings.csvDir + "train_signal.csv",
            settings.csvDir + "train_stim.csv")
        # write the test data
        write_data_stim_files(
            settings.subjects,
            settings.get_channels(),
            settings.get_frequencies(),
            settings.testBlocks,
            settings.dataDir,
            settings.csvDir + "test_signal.csv",
            settings.csvDir + "test_stim.csv")
    except FileNotFoundError:
        print("Download files from http://bci.med.tsinghua.edu.cn/download.html and move them into the %s folder!" %
              settings.dataDir)
    with open(settings.csvDir + "settings.json", mode="w+") as settings_json:
        json.dump(settings.__dict__, settings_json, indent=4)


def write_data_stim_files(subjects, channels, frequencies, blocks, data_dir, signal_out, stim_out):
    """
    Concatenate the desired data of each subject and write it to the output files
    :param subjects: Tuple/List of subject indices
    :param channels: List of indices from the desired channels
    :param frequencies: List of Frequency objects
    :param blocks: List/Tuple of the desired blocks(=trials)
    :param data_dir: Directory with the .mat files
    :param signal_out: Signal csv output file
    :param stim_out: Stimulation csv output file
    """
    with open(signal_out, "w+") as data_csv, open(stim_out, "w+") as stim_csv:
        data_writer = csv.writer(data_csv, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        stim_writer = csv.writer(stim_csv, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        data_writer.writerow(["Time (s)"] +
                             ["Channel " + str(x + 1) for x in range(len(channels))] + ["Sampling Rate"])
        stim_writer.writerow(["Time (s)", "Identifier", "Duration"])
        offset = 0
        for subject in subjects:
            data = scipy.io.loadmat(data_dir + os.sep + ("S%i.mat" % subject))["data"]
            write_subject_data(data, channels, frequencies, blocks, offset, data_writer, stim_writer)
            offset += Constants.signalLength * len(frequencies) * len(blocks)
        stim_writer.writerow([offset, stim_codes.OVTK_StimulationId_ExperimentStop, 0])


def write_subject_data(data, channels, frequencies, blocks, offset, signal_writer, stim_writer):
    """
    Append the desired data to the signal and stim files
    :param data: Data array for a subject extracted from a .mat file
    :param channels: List of indices from the desired channels
    :param frequencies: List of Frequency objects
    :param blocks: List/Tuple of the desired blocks(=trials)
    :param offset: Time offset, length of data already written
    :param signal_writer: csv.writer for the signal data
    :param stim_writer: csv.writer of the stimulation data
    """
    for block in blocks:
        for frequency in frequencies:
            stim_writer.writerow([offset + Constants.signalOffset,
                                  frequency.stimCode, Constants.stimLength])

            for time_step in range(data.shape[1]):
                data_row = [data[channel][time_step][frequency.index][block] for channel in channels]
                if offset == 0 and time_step == 0:
                    data_row.append(Constants.samplingRate)
                signal_writer.writerow([time_step / Constants.samplingRate + offset] + data_row)
            offset += Constants.signalLength


class Frequency:
    def __init__(self, value, stim_code):
        """
        :param value: between 8 and 15.8 hz in 0.2 steps
        """
        self.value = value
        # see Readme.txt
        self.index = int((value - 8) / 0.2)
        self.stimCode = stim_code


twentyTwentyIndex = {'CB1': 59, 'CP4': 39, 'P6': 50, 'C2': 28, 'M2': 42, 'PO3': 54, 'AF4': 4, 'FC3': 16, 'O1': 60,
                     'PO4': 56, 'CP3': 35, 'F4': 11, 'C1': 26, 'CP5': 34, 'PO5': 53, 'C6': 30, 'FC1': 17, 'AF3': 3,
                     'FT7': 14, 'F3': 7, 'Cz': 27, 'CP1': 36, 'P1': 46, 'FT8': 22, 'FP1': 0, 'F5': 6, 'F8': 13,
                     'CB2': 63, 'F6': 12, 'F7': 5, 'Oz': 61, 'PO8': 58, 'CP2': 38, 'FCz': 18, 'FC5': 15, 'FP2': 2,
                     'FZ': 9, 'C4': 29, 'M1': 32, 'CP6': 40, 'CPZ': 37, 'P3': 45, 'P8': 51, 'FC2': 19, 'F2': 10,
                     'TP7': 33, 'P5': 44, 'C5': 24, 'FC6': 21, 'P2': 48, 'FC4': 20, 'C3': 25, 'T7': 23, 'T8': 31,
                     'TP8': 41, 'P4': 49, 'PZ': 47, 'F1': 8, 'PO7': 52, 'P7': 43, 'FPZ': 1, 'POz': 55, 'PO6': 57,
                     'O2': 62}
"""
Indices taken from 64-channels.loc
"""

if __name__ == "__main__":
    """
    Write data with default settings
    """
    write_data(Settings())
