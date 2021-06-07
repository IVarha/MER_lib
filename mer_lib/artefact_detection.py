import math

import numpy as np


def max_diff_psd(data):


    psd_thr = 0.01

    dat  = data.get_data()
    freqs = data.get_freqs()

    for i in range(len(dat)):
        seconds = math.ceil(dat[i].shape/freqs[i])
        fs = freqs[i]

        for secs in range(seconds):
            s_e = [int(secs*fs), min(int((secs+1)*fs),int(dat[i].shape[0]))]  #start end
            feat = _compute_features(dat[i],s_e,fs)

def _compute_features(signal,start_end,freq):

    feat_vals = []
    np.NAN

    pass






    pass
