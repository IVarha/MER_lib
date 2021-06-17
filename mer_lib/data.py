import fnmatch

import pyedflib.highlevel as edreader
import csv

import numpy as np
import os
import math

class MER_data():

    __read_data = None

    __is_read = False
    __data = None
    __electrode_description = None

    _freqs = []


    _recording_data_notations = None


    def __init__(self, dirname = None,file_pattern =None):
        filename = None
        if dirname is None:
            return
        for file in os.listdir(dirname):
            if fnmatch.fnmatch(file, file_pattern + "*.edf"):
                filename = dirname + os.sep + file
                break


        if filename is None:
            return
        self.__read_data = edreader.read_edf(filename)
        self.__data = self.__read_data[0]

        self.__electrode_description = self.__read_data[1]
        self.__is_read = True

        self._freqs  = [ x['sample_rate'] for x in self.__electrode_description]
        self._recording_data_notations = self._read_anatomical(dirname,file_pattern + "annotations.tsv")

    def __copy__(self):
        newone = type(self)()
        newone.__data = self.__data.copy()
        newone._freqs = self._freqs.copy()
        newone.__electrode_description = self.__electrode_description.copy()
        newone.__is_read = self.__is_read
        newone._recording_data_notations = self._recording_data_notations
        return newone

    def get_data(self):
        return self.__data


    def set_data(self,data):
        self.__data = data

    def get_freqs(self):
        return self._freqs


    def _read_anatomical(self,dirname, patern_name):
        fm = None
        for file in os.listdir(dirname):
            if fnmatch.fnmatch(file, patern_name):
                fm = dirname + os.sep + file
                break


        with open(fm, newline='') as tsvfile:
            reader = csv.reader(tsvfile,dialect='excel-tab')
            r = 0

            vals = []
            depths = []
            for row in reader:
                if r == 0:
                    r= r+1
                else:
                    vals.append(float(row[0]))
                    depths.append(float(row[4].split(' ')[1]))
                pass
        return [vals,depths]

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
                a[i].append(self.__data[i,s_e[0]:s_e[1]])
        return a


    def rescale_signals(self):
        s = self.__data

        for i in range(len(self.__electrode_description)):
            mn = np.nanmin(s[i])
            mx = np.nanmax(s[i])
            cm = np.nanmean(s[i])

            s[i] = (s[i] - mn)/(mx-mn) *(self.__electrode_description[i]['physical_max']
                                         -self.__electrode_description[i]['physical_min'] ) + self.__electrode_description[i]['physical_min']

        self.__data = s

#parse labels from
def parse_anatomical_labels(filename_xls):
    from pandas_ods_reader import read_ods
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
    df[sb]

    RS = [
        [df[RCT].values,df[RCB].values],
        [df[RAT].values, df[RAB].values],
        [df[RPT].values, df[RPB].values],
        [df[RMT].values, df[RMB].values],
        [df[RLT].values, df[RLB].values]
    ]

    LS = [
        [df[LCT].values,df[LCB].values],
        [df[LAT].values, df[LAB].values],
        [df[LPT].values, df[LPB].values],
        [df[LMT].values, df[LMB].values],
        [df[LLT].values, df[LLB].values]
    ]

    for el in RS:
        for a in el:
            a[np.where(a=="n/a")] = np.nan
            a[np.where(a == "nil")] = np.nan

    return [subs,LS,RS]


################process

def demean_data(data):

    da  = data.get_data()
    mn1 =  da.mean(axis=1)
    for i in range(mn1.shape[0]):
        da[i,:] = da[i,:] - mn1[i]

    data.set_data(da)
    return data