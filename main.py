# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import mer_lib.data as dat
import mer_lib.artefact_detection as ad
import mer_lib.processor as proc

import matplotlib.pyplot as plt
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    a = dat.MER_data("/data/home/shared/dbs/MRI/Ontario/Data_202012/selected_MER/sub-P061/ses-perisurg/ieeg/sub-P061_ses-perisurg_run-02_ieeg.edf")

    runner = proc.Processor()
    runner.set_data(a)
    runner.set_processes([ad.max_diff_psd])
    runner.run()
    dat = a.get_data()

    fig = plt.plot(dat[0,0:100])
    plt.show()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
