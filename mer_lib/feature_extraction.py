import numpy as np


def nrms_extraction( data):

    msk_threshold = data.mask_label_threshold

    a = data.divide_1s_chunks()

    # masks = [None] * len(a)
    # for i in range(len(a)):
    #     start = 0
    #     masks[i] = []
    #     for j in range(len(a[i])):
    #         msk_T = msk_threshold[i,start:start+a[i][j].shape[0]]
    #         masks[i].append(msk_T)
    #         start += a[i][j].shape[0]

    ###################calculate NRMS

    res = [None] * len(a)
    for i in range(len(a)):
        res[i] = []
        for j in range(len(a[i])):

            if msk_threshold[i][j] == True:
                tmp = np.sqrt(np.nanmean(np.power(a[i][j],2)))
                res[i].append(tmp)


            else:
                res[i].append(np.NAN)

    data.extracted_features = np.array(res)
    return data