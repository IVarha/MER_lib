# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import pickle
import numpy as np
import scipy.stats as sc_stat
import matplotlib.pyplot as plt
import scipy.io as sc_io
import statistics_analysis as sa
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# safe_subjects = [60,62,63,74,69,70,71,73,74,75,77,78,79,81,82,83,84,85,86,87,90,93,95,97,98,99,100,102,104,105,106,107,110,111,112,113,114,115,116,118,120,125,126,129,132,133]
safe_subjects = [60, 62, 63, 66, 69, 70, 71, 73, 74, 75, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 90, 93, 95, 97, 98, 99,
                 102, 104, 105, 106, 107, 110, 111, 112, 113, 114, 115, 116, 118, 120, 125, 126, 129, 132, 133]



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    eb_data = sc_io.loadmat("/home/shared/dbs/MRI/Ontario/canada_imaging_segmentation/_prep_MER/featureDataOntarioDataV2-gmss1.2-20210611-194816-SelSubjStrict-metadata.mat")
    eb_data = sc_io.loadmat("/home/varga/mer_data_processing/rms_ids.mat")

    rms = eb_data['rms_vals']
    rms = rms.transpose()[0]
    traj_id = eb_data['trajId']
    traj_id = traj_id.transpose()[0]
    un_elecrodes = np.unique(traj_id)

    area_t = eb_data['area']
    area = []
    for i in range(area_t.shape[0]):
        if eb_data['area'][i][0][0].upper() == 'STN':
            area.append(True)
        else:
            area.append(False)
    area = np.array(area)

    for i in range(un_elecrodes.shape[0]):
        el_num = un_elecrodes[i]
        rms[traj_id == el_num] = rms[traj_id == el_num] / np.mean(rms[traj_id == el_num][:5])

    sa.plot_pause([rms,area])


    left = [7411,7412,7413,7414,7415]
    right = [7421, 7422, 7423, 7424, 7425]

    plt.figure()
    for ind in left:
        plt.plot(rms[traj_id==ind] / np.mean(rms[traj_id == ind][:5]  ))
    plt.show()

    plt.figure()
    for ind in right:
        plt.plot(rms[traj_id == ind] / np.mean(rms[traj_id == ind][:5]  ))
    plt.show()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/
