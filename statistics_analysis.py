# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import pickle
import numpy as np
import scipy.stats as sc_stat
import matplotlib.pyplot as plt


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# safe_subjects = [60,62,63,66,69,70,71,73,74,75,77,78,79,81,82,83,84,85,86,87,90,93,95,97,98,99,100,102,104,105,106,107,110,111,112,113,114,115,116,118,120,125,126,129,132,133]
safe_subjects = [60, 62, 63, 66, 69, 70, 71, 73, 74, 75, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 90, 93, 95, 97, 98, 99,
                 102, 104, 105, 106, 107, 110, 111, 112, 113, 114, 115, 116, 118, 120, 125, 126, 129, 132, 133]


# safe_subjects = [60]

def read_all_subjects():
    """
    reads test data
    :return:
    """
    f = open("/home/varga/mer_data_processing/test", 'rb')

    dat = pickle.load(f)
    return dat


def generate_mask_for_subject(subj_ind, subj, side, anat_labels):
    subs = np.array(anat_labels[0])

    ind = np.where(subs == subj_ind)[0][0]

    res_mask = []
    start_end = []
    for i in range(subj.get_num_electrodes()):
        el_name = subj.get_electrode_name_by_index(i)
        top = anat_labels[1][side][el_name]['top'][ind]
        bot = anat_labels[1][side][el_name]['bot'][ind]
        # calc mask

        a = np.array(subj.distances)

        if top == np.nan:
            a[:] = False
            res_mask.append(a)
            continue
        r_tmp = (a >= top) & (a <= bot)
        res_mask.append(r_tmp)

    return res_mask


def combine_into_one_array(parsed_data):
    """

    :param parsed_data:
    :return:
    """

    comb_arr = parsed_data['right'] + parsed_data['left']

    comb_res = None
    for i in range(len(comb_arr)):
        if not (comb_arr[i] is None):
            for j in range(comb_arr[i].shape[0]):

                if comb_res is None:
                    comb_res = comb_arr[i][j]
                else:
                    if not (comb_arr[i] is None):
                        comb_res = np.concatenate((comb_res, comb_arr[i][j]))

    comb_arr = parsed_data['right_masks'] + parsed_data['left_masks']
    comb_masks = None
    for i in range(len(comb_arr)):
        if not (comb_arr[i] is None):
            ca = np.array(comb_arr[i])
            for j in range(ca.shape[0]):

                if comb_masks is None:
                    comb_masks = comb_arr[i][j]
                else:
                    if not (comb_arr[i] is None):
                        comb_masks = np.concatenate((comb_masks, comb_arr[i][j]))

    return [comb_res, comb_masks]


def plot_pause(data):
    stns = data[0][data[1]]
    #stns = sc_stat.lognorm.rvs(s=0.5,loc=1,size=10000)
    n_stns = data[0][~ data[1]]
    ax = plt.subplot(111)
    ax.hist(stns,50,density=True,facecolor = 'r',alpha=0.5)
    ax.hist(n_stns, 50,density=True,facecolor = 'b',alpha=0.5)
    #ax.set_xscale("log")

    shape,loc,scale = sc_stat.lognorm.fit(stns,loc=stns.mean())
    shape1,loc1,scale1 = sc_stat.lognorm.fit(n_stns)

    x = np.logspace(0, 5, 200)
    pdf = sc_stat.lognorm.pdf(x, shape, loc, scale)
    # pdf2 = sc_stat.lognorm.pdf(x, shape1, loc1, scale1)
    #
    plt.xlim(min(stns) -2 , max(stns) +2)
    ax.plot(x, pdf, 'r')
    # ax.plot(x, pdf2, 'g')


    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # parse_parameters

    preprocessed_data = read_all_subjects()

    comb_data = combine_into_one_array(preprocessed_data)
    plot_pause(comb_data)
    # a.get_anat_landmarks()
    # #a.rescale_signals()
    #
    # runner = proc.Processor()
    # runner.set_data(a)
    # runner.set_processes([
    #                       ad.covariance_method,
    #                       dat.normalise_mean_std,
    #                       fe.nrms_calculation])
    # a =runner.run()
    # dat = a.get_data()
    # for i in range(a.extracted_features.shape[0]):
    #     plt.plot(a.distances,a.extracted_features[i])
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
