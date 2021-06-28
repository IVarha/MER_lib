import numpy as np
import matplotlib.pyplot as plt

def rms_extraction(data):
    msk_threshold = data.mask_label_threshold

    a = data.get_data()
    freqs = data.get_freqs()

    [times, ordered] = data.get_anat_landmarks()
    ###################calculate RMS

    ######unite chunks  for getting one RMS

    uniq_distances = sorted(set(ordered))  # set formed from distances
    ordered = np.array(ordered)
    res_distance_indices = [np.where(ordered == distance) for distance in uniq_distances]

    res = [[] for i in range(a.shape[0])]
    for i in range(len(res_distance_indices)):
        indices = res_distance_indices[i][0]

        for i_elect in range(a.shape[0]):
            tmp = None
            freq = freqs[i_elect]
            for ind in indices:
                if ind < ordered.shape[0] - 1:  # to avoid last indices
                    if tmp is None:
                        tmp = a[i_elect, int(times[ind] * freq):int(times[ind + 1] * freq)]
                    else:
                        tmp = np.concatenate((tmp, a[i_elect, int(times[ind] * freq):int(times[ind + 1] * freq)]))
                else:
                    if tmp is None:
                        tmp = a[i_elect, int(times[ind] * freq):]
                    else:
                        tmp = np.concatenate((tmp, a[i_elect, int(times[ind] * freq):]))
            rms_value = np.sqrt(np.nanmean(np.power(tmp, 2)))
            res[i_elect].append(rms_value)

    data.extracted_features = np.array(res)
    data.distances = uniq_distances
    return data


def nrms_calculation(data):
    if not hasattr(data, "distances"):
        data = rms_extraction(data)
    # for i in range(data.extracted_features.shape[0]):
    #     plt.plot(data.distances,data.extracted_features[i])
    # plt.show()
    mask = np.array(data.distances) < -4
    res_nrms = []
    for i in range(data.extracted_features.shape[0]):
        t_dat = data.extracted_features[i, mask]
        mn = np.nanmean(t_dat)
        res_nrms.append(data.extracted_features[i] / mn)
    data.extracted_features = np.array(res_nrms)
    return data
