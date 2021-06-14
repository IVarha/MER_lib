
import pyedflib.highlevel as edreader




class MER_data():

    __read_data = None

    __is_read = False
    __data = None
    __electrode_description = None

    _freqs = []



    def __init__(self, filename=None):
        if filename is None:
            return
        self.__read_data = edreader.read_edf(filename)
        self.__data = self.__read_data[0]

        self.__electrode_description = self.__read_data[1]
        self.__is_read = True

        self._freqs  = [ x['sample_rate'] for x in self.__electrode_description]

    def __copy__(self):
        newone = type(self)()
        newone.__data = self.__data.copy()
        newone._freqs = self._freqs.copy()
        newone.__electrode_description = self.__electrode_description.copy()
        newone.__is_read = self.__is_read
        return newone

    def get_data(self):
        return self.__data


    def set_data(self,data):
        self.__data = data

    def get_freqs(self):
        return self._freqs

