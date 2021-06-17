# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import mer_lib.data as dat
import mer_lib.artefact_detection as ad
import mer_lib.processor as proc
import mer_lib.feature_extraction as fe
import matplotlib.pyplot as plt
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    #parse_parameters
    n = dat.parse_anatomical_labels("/home/varga/processing_data/participants-ED2.xlsx.ods")


    a = dat.MER_data("/data/home/shared/dbs/MRI/Ontario/Data_202012/selected_MER/sub-P060/ses-perisurg/ieeg/","sub-P060_ses-perisurg_run-01*")
    a.rescale_signals()

    runner = proc.Processor()
    runner.set_data(a)
    runner.set_processes([dat.demean_data,
                          ad.max_diff_psd,
                          fe.nrms_extraction])
    a =runner.run()
    dat = a.get_data()

    fig = plt.plot(dat[1])
    plt.show()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
