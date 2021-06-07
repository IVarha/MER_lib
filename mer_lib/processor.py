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

    def run(self,**kwargs):
        a = copy.copy(self.__data)
        for i in range(len(self.__processes)):
            a = self.__processes[i](a)

        return a
