#!/usr/bin/env python
"""
for python 2 or 3
Reader to import csvs exported from OpenVibe into mne.
The stimulations in the stim file should be in form of a OpenVibe label with a timestamp and a duration > 0.
Use datasets/onw/converter.xml to convert stim files with durations of 0

When executed it shows a simple view of the EEG with a bandpass filter applied
"""
import csv
import math
from collections import namedtuple

import numpy as np

import mne
from mne.io.base import BaseRaw
from mne.io.meas_info import create_info
from mne.utils import verbose
from mne.channels import Montage

from ten_five_coords import get_cartesian_coords


@verbose
def read_raw_ov_csv(signal_fname, stim_fname=None, misc=None,
                    scale=1e-6, preload=True, verbose=None):
    """
    Raw object from csv Files exported from OpenVibe
    Parameters
    ----------
    signal_fname : str
        Path to the OpenVibe signal csv file.
    stim_fname : str
        Path to the OpenVibe stimulation csv file.
    misc : list or tuple
        List of indices that should be designated MISC channels.
        Default is None. Possible use for sensor data.
    scale : float
        The scaling factor for EEG data. Units for MNE are in volts.
        OpenBCI data are typically stored in microvolts. Default scale
        factor is 1e-6.
    preload : bool
        If True, all data are loaded at initialization. (recommended)
        If False, data are not read until save.
    verbose : bool, str, int, or None
        If not None, override default verbose level (see mne.verbose).
    Returns
    -------
    raw : Instance of RawOvCsv
        A Raw object containing OpenVibe csv data.
    See Also
    --------
    mne.io.BaseRaw : Documentation of attribute and methods.
    """
    return RawOvCsv(signal_fname=signal_fname, stim_fname=stim_fname, misc=misc,
                    scale=scale, preload=preload, verbose=verbose)


class RawOvCsv(BaseRaw):
    """
    Raw object from OpenVibe csv Files.
    use read_raw_ov_csv() to create an instance
    """

    @verbose
    def __init__(self, signal_fname, stim_fname, misc, scale, preload, verbose):
        self.signal_fname = signal_fname
        self.scale = scale
        with open(signal_fname, 'r') as f_signal:
            signal_reader = csv.reader(f_signal, delimiter=";")
            header = next(signal_reader)
            # sfreq: Sampling frequency
            sfreq = int(next(signal_reader)[-1])

            # Count number of samples
            for n_samples, _ in enumerate(f_signal):
                pass
            n_samples += 2  # to compensate for the csvreader's reads

        # header format: Time (s); Channel 1; ..., Channel x; Sampling Frequency
        ch_names = header[1:-1]
        n_channels = len(ch_names)
        ch_types = ['eeg'] * n_channels
        if misc:
            for ii, mi in enumerate(misc):
                ch_names[mi] = 'MISC %03d' % (ii + 1)
                ch_types[mi] = 'misc'

        self.stim_channel = None
        if stim_fname is not None:
            # stimulations are converted to a signal (self.stim_channel, channel name 'STI 014')
            # as long as a stimulation is active, the stimulation channel has the value
            # of the stimulation
            with open(stim_fname, 'r') as f_stim:
                stim_reader = csv.reader(f_stim, delimiter=";")
                next(stim_reader)  # skip header
                stims = []
                Stimulation = namedtuple("Stimulation", ["start_index", "id", "len_samples"])
                for line in stim_reader:
                    stims.append(Stimulation(start_index=math.floor(float(line[0]) * sfreq),
                                             id=int(line[1]) - 0x00008100,  # OVTK_StimulationId_Label_00
                                             len_samples=math.floor(sfreq * float(line[2]))))

            self.stim_channel = np.zeros(n_samples)
            for stim in stims:
                self.stim_channel[stim.start_index: stim.start_index + stim.len_samples] = stim.id

            ch_names.append('STI 014')  # mne standard name for stim channel
            ch_types.append('stim')

        m_ch_names = []
        m_selection = []
        m_pos = []
        for channel_index in range(len(ch_names)):
            if ch_types[channel_index] == 'eeg':
                m_pos.append(get_cartesian_coords(ch_names[channel_index]))
                m_ch_names.append(ch_names[channel_index])
                m_selection.append(channel_index)

        info = create_info(ch_names, sfreq, ch_types,
                           Montage(np.array(m_pos), m_ch_names, 'standard_1005', np.array(m_selection)))
        info['buffer_size_sec'] = 1.  # not sure, taken from examples
        super(RawOvCsv, self).__init__(
            info,
            preload=preload,
            first_samps=(0,), last_samps=(n_samples - 1,),
            filenames=tuple(fname for fname in (signal_fname, stim_fname) if fname is not None),
            orig_format='double', dtype=np.float64,
            verbose=verbose
        )

    def _read_segment_file(self, data, idx, fi, start, stop, cals, mult):
        """
        Read a segment of data from a file.
        Not optimized for partial loading, best used with preload=True
        Required by mne.io.base.BaseRaw
        """
        with open(self.signal_fname, 'r') as f_signal:
            signal_reader = csv.reader(f_signal, delimiter=";")
            for _ in range(start + 1):
                next(signal_reader)
            data_raw = [row[1:-1] for row in signal_reader]

        data_source = self.scale * np.asarray(data_raw, dtype=np.float64).T  # rotate for mne
        if self.stim_channel is not None:
            data_source = np.append(data_source, [self.stim_channel[start:stop + 1]], axis=0)
        # not sure, copied from mne.io.utils._mult_cal_one
        if mult is not None:
            data[:] = np.dot(mult, data_source)
        else:
            if isinstance(idx, slice):
                data[:] = data_source[idx]
            else:
                np.take(data_source, idx, axis=0, out=data)
            if cals is not None:
                data *= cals

if __name__ == "__main__":
    import matplotlib
    matplotlib.use('TKAgg', warn=False, force=True)  # python2 + ubuntu: sudo apt-get install python-tk
    import matplotlib.pyplot as myplt

    raw = read_raw_ov_csv("test_signal.csv", "test_stim.csv", verbose='DEBUG')

    picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=True,
                           exclude='bads')

    # Show EEG data
    raw.filter(0.5, 30, fir_design="firwin")
    raw.plot()
    myplt.show()
