import fnmatch
from pathlib import Path
from typing import Union

import pyedflib.highlevel as edreader
import csv

import numpy as np
import os
import math
from pandas_ods_reader import read_ods


class MER_data():
    """
    Class to represent Microelectrode recording (MER) data.
    """
    __read_data = None

    __is_read = False
    __data = None
    __electrode_description = None

    _freqs = []

    _recording_data_notations = None

    def __init__(self, dirname: Union[str, Path] = None, file_pattern: str = None):
        """
        Initializes a new instance of the MER_data class.
        :param dirname: str, the directory path containing the data.
        :param file_pattern: str, the file pattern to match in the directory.
        """
        filename = None
        if dirname is None:
            return
        if isinstance(dirname, str):
            dirname = Path(dirname)
        for file in dirname.iterdir():
            if fnmatch.fnmatch(file.name, file_pattern + "*.edf"):
                filename = dirname / file
                break

        if filename is None:
            return
        self.__read_data = edreader.read_edf(str(filename))
        self.__data = self.__read_data[0]

        self.__electrode_description = self.__read_data[1]
        self.__is_read = True

        self._freqs = [x['sample_rate'] for x in self.__electrode_description]
        self._recording_data_notations = self._read_anatomical(dirname, file_pattern + "annotations.tsv")

    def __copy__(self):
        """
        Creates and returns a copy of the current instance.
        """
        newone = type(self)()
        newone.__data = self.__data.copy()
        newone._freqs = self._freqs.copy()
        newone.__read_data = self.__read_data
        newone.__electrode_description = self.__electrode_description.copy()
        newone.__is_read = self.__is_read
        newone._recording_data_notations = self._recording_data_notations
        return newone

    @property
    def data(self):
        """
        Gets the data.
        :return: np.ndarray, the data.
        """
        return self.__data

    def set_data(self, data):
        self.__data = data

    def get_freqs(self):
        return self._freqs

    def get_anat_landmarks(self):
        """
        Gets anatomical landmarks.
        :return: list, a list of the times and depths of the anatomical landmarks.
        """
        lm = self.__read_data[2]['annotations']

        times = []
        depths = []

        for i in range(len(lm)):
            times.append(round(float(lm[i][0]), 1))
            depths.append(round(float(lm[i][2].split(' ')[1]), 1))

        return [times, depths]

    def get_electrode_index(self, name):
        """
        Gets the index of an electrode by its name.
        :param name: str, the name of the electrode.
        :return: int, the index of the electrode.
        """
        for i in range(len(self.__read_data[1])):
            if self.__read_data[1][i]['label'] == name:
                return i

    def get_side(self):
        """
        Gets the side of the brain that was recorded from.
        :return: str, the side of the brain that was recorded from.
        """
        return self.__read_data[2]['admincode']

    def get_num_electrodes(self):
        return len(self.__read_data[1])

    def get_electrode_name_by_index(self, index):
        """Gets electrode name by its index"""
        return self.__read_data[1][index]['label']

    def _read_anatomical(self, dirname: Union[Path,str], patern_name):
        fm = None
        if isinstance(dirname,str):
            dirname = Path(dirname)

        for file in dirname.iterdir():
            if fnmatch.fnmatch(file.name, patern_name):
                fm = file
                break

        with open(fm, newline='') as tsvfile:
            reader = csv.reader(tsvfile, dialect='excel-tab')
            r = 0

            vals = []
            depths = []
            for row in reader:
                if r == 0:
                    r = r + 1
                else:
                    vals.append(float(row[0]))
                    depths.append(float(row[4].split(' ')[1]))
                pass
        return [vals, depths]

    def divide_1s_chunks(self):

        a = [None] * len(self._freqs)
        for i in range(len(self._freqs)):
            if a[i] is None:
                a[i] = []

            seconds = math.ceil(self.__data[i].shape / self._freqs[i])
            fs = self._freqs[i]
            data_sub = []
            for secs in range(seconds):
                s_e = [int(secs * fs), min(int((secs + 1) * fs), int(self.__data[i].shape[0]))]  # start end
                a[i].append(self.__data[i, s_e[0]:s_e[1]])
        return a

    def rescale_signals(self):
        s = self.__data

        for i in range(len(self.__electrode_description)):
            mn = np.nanmin(s[i])
            mx = np.nanmax(s[i])
            cm = np.nanmean(s[i])

            s[i] = (s[i] - mn) / (mx - mn) * (self.__electrode_description[i]['physical_max']
                                              - self.__electrode_description[i]['physical_min']) + \
                   self.__electrode_description[i]['physical_min']

        self.__data = s


# parse labels from
def parse_anatomical_labels(filename_xls):
    """:return [ list of subjects, Left Side, Right Side ]
    in Right Side [centr,ant,posterior,med, lateral ]
    each of them have [TOP and BOTTOM] lists"""

    df = read_ods(filename_xls, "surgical")

    sb = "subject"

    LCT = "LCTopSurg"
    LCB = "LCBotSurg"

    LAT = "LATopSurg"
    LAB = "LABotSurg"

    LPT = "LPTopSurg"
    LPB = "LPBotSurg"

    LMT = "LMTopSurg"
    LMB = "LMBotSurg"

    LLT = "LLTopSurg"
    LLB = "LLBotSurg"
    ###############

    RCT = "RCTopSurg"
    RCB = "RCBotSurg"

    RAT = "RATopSurg"
    RAB = "RABotSurg"

    RPT = "RPTopSurg"
    RPB = "RPBotSurg"

    RMT = "RMTopSurg"
    RMB = "RMBotSurg"

    RLT = "RLTopSurg"
    RLB = "RLBotSurg"

    ###get subjects
    subs = df[sb].values.astype(np.int).tolist()
    ###get su

    RS = {
        "cen": {"top": df[RCT].values, "bot": df[RCB].values},
        "ant": {"top": df[RAT].values, "bot": df[RAB].values},
        "pos": {"top": df[RPT].values, "bot": df[RPB].values},
        "med": {"top": df[RMT].values, "bot": df[RMB].values},
        "lat": {"top": df[RLT].values, "bot": df[RLB].values},
    }
    LS = {
        "cen": {"top": df[LCT].values, "bot": df[LCB].values},
        "ant": {"top": df[LAT].values, "bot": df[LAB].values},
        "pos": {"top": df[LPT].values, "bot": df[LPB].values},
        "med": {"top": df[LMT].values, "bot": df[LMB].values},
        "lat": {"top": df[LLT].values, "bot": df[LLB].values},
    }

    for el in RS:

        for a in RS[el]:
            RS[el][a][np.where(RS[el][a] == "n/a")] = np.nan
            RS[el][a][np.where(RS[el][a] == "nil")] = np.nan
            RS[el][a][np.where(RS[el][a] is None)] = np.nan

    for el in LS:

        for a in LS[el]:
            LS[el][a][np.where(LS[el][a] == "n/a")] = np.nan
            LS[el][a][np.where(LS[el][a] == "nil")] = np.nan
            LS[el][a][np.where(LS[el][a] is None)] = np.nan

    return [subs, {"left": LS, "right": RS}]


################process

def demean_data(data):
    da = data.data
    mn1 = da.mean(axis=1)
    for i in range(mn1.shape[0]):
        da[i, :] = da[i, :] - mn1[i]

    data.set_data(da)
    return data


def normalise_mean_std(data):
    da = data.data
    mn1 = np.nanmean(da, axis=1)
    cov = np.nanstd(da, axis=1)
    for i in range(mn1.shape[0]):
        da[i, :] = (da[i, :] - mn1[i]) / cov[i]
    data.set_data(da)
    return data
