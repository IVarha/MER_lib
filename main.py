# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import pickle
import numpy as np

import mer_lib.data as dat
import mer_lib.artefact_detection as ad
import mer_lib.processor as proc
import mer_lib.feature_extraction as fe
import matplotlib.pyplot as plt
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

#safe_subjects = [60,62,63,66,69,70,71,73,74,75,77,78,79,81,82,83,84,85,86,87,90,93,95,97,98,99,100,102,104,105,106,107,110,111,112,113,114,115,116,118,120,125,126,129,132,133]
safe_subjects = [60,62,63,66,69,70,71,73,74,75,77,78,79,81,82,83,84,85,86,87,90,93,95,97,98,99,102,104,105,106,107,110,111,112,113,114,115,116,118,120,125,126,129,132,133]

#safe_subjects = [60]

def read_all_subjects():

    runner = proc.Processor()
    runner.set_processes([])
    runner.set_processes([
                          ad.covariance_method,
                          #dat.normalise_mean_std,
                          fe.nrms_calculation])

    res = {'right': [],'left' : []}
    # for sub in safe_subjects:
    #     if sub < 100:
    #         dat1 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P0"
    #                             + str(sub) + os.sep + "/ses-perisurg/ieeg/", "*run-01*")
    #     else:
    #         dat1 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P"
    #                             + str(sub) + os.sep + "/ses-perisurg/ieeg/","*run-01*")
    #     print(dat1.get_side())

    for sub in safe_subjects:
        print("----------------"+str(sub)+ "------------------------")

        if sub < 100:
            dat1 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P0"
                                + str(sub) + os.sep + "/ses-perisurg/ieeg/","*run-01*")
            dat2 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P0"
                                + str(sub) + os.sep + "/ses-perisurg/ieeg/", "*run-02*")
            dat1.rescale_signals()
            dat2.rescale_signals()
            dat1 = runner.run(dat1)
            dat2 = runner.run(dat2)
            res["right"].append(dat1)
            res["left"].append(dat2)
        else:
            dat1 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P"
                                + str(sub) + os.sep + "/ses-perisurg/ieeg/","*run-01*")

            dat2 = dat.MER_data("/home/varga/mer_data_processing/mer/sub-P"
                                + str(sub) + os.sep + "/ses-perisurg/ieeg/", "*run-02*")
            dat1.rescale_signals()
            dat2.rescale_signals()
            if (dat2.get_freqs() != []):
                dat2 = runner.run(dat2)
                res['left'].append(dat2)
            else:
                res['left'].append(None)
            if (dat1.get_freqs() != []):
                dat1 = runner.run(dat1)
                res["right"].append(dat1)
            else:
                res["right"].append(None)
            plt.figure()
        for k in range(dat1.extracted_features.shape[0]):
            plt.plot(dat1.distances,dat1.extracted_features[k])
        plt.show()


    return res


def generate_mask_for_subject(subj_ind,subj,side,anat_labels):


    subs = np.array( anat_labels[0])


    ind = np.where(subs == subj_ind)[0][0]

    res_mask = []
    start_end = []
    for i in range(subj.get_num_electrodes()):
        el_name = subj.get_electrode_name_by_index(i)
        top = anat_labels[1][side][el_name]['top'][ind]
        bot = anat_labels[1][side][el_name]['bot'][ind]
        #calc mask



        a = np.array(subj.distances)

        if top == np.nan:
            a[:] = False
            res_mask.append(a)
            continue
        r_tmp = (a >= top ) & (a <= bot)
        res_mask.append(r_tmp)

    return res_mask



def process_subjects(parsed_data,an_lab):


    right_masks = []
    left_masks = []

    right_els = []
    left_els = []

    for i in range(len(safe_subjects)):

        right = parsed_data['right'][i]
        left = parsed_data['left'][i]
        if right is None:
            right_mask = None
            right_els.append(None)
        else:
            right_mask = generate_mask_for_subject(safe_subjects[i],right,"right",an_lab)
            right_els.append(right.extracted_features)
        if left is None:
            left_mask = None
            left_els.append(None)
        else:
            left_mask = generate_mask_for_subject(safe_subjects[i],left,"left",an_lab)
            left_els.append(left.extracted_features)
        left_masks.append(left_mask)
        right_masks.append(right_mask)



    r = { "right": right_els,"left": left_els,"right_masks" : right_masks,"left_masks": left_masks}
    with open("/home/varga/mer_data_processing/test","wb") as fl:
        pickle.dump(r,fl)















# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')


    #parse_parameters
    an_labels = dat.parse_anatomical_labels("/home/varga/processing_data/participants-ED2.xlsx.ods")
    a = dat.MER_data("/data/home/shared/dbs/MRI/Ontario/Data_202012/selected_MER/sub-P060/ses-perisurg/ieeg/", "*run-01*")

    preprocessed_data = read_all_subjects()

    process_subjects(preprocessed_data,an_labels)


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
