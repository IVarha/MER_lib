import copy


class Processor():

    __processes = None
    __data = None


    def __init__(self):
        self.__processes = []

    def set_data(self,data ):
        self.__data = data

    def set_processes(self,processes):
        self.__processes = processes

    def run(self,data =None):
        if data is None:
            a = copy.copy(self.__data)
        else:
            a = data
        for i in range(len(self.__processes)):
            a = self.__processes[i](a)

        return a
