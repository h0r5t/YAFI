
class YAFIObject:

    def parse(self, unnamed_list):
        self.named_dict = {}
        counter = 0
        for element in unnamed_list:
            self.named_dict[self.parameter_names_list[counter]] = element
            counter += 1

    def setParameterNames(self, parameter_names_list):
        self.parameter_names_list = parameter_names_list

    def getParamList(self):
        return self.parameter_names_list

    def getData(self, parameter):
        return self.named_dict[parameter]


class YAFIObjectCurrentStockPrice(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["symbol", "name", "price", "time"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)
