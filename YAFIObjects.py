
class YAFIObject:

    def parse(self, unnamed_list):
        self.unnamed_list = unnamed_list
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

    def getAsString(self):
        string = ""
        for a in self.unnamed_list:
            string += str(a)
            string += ","
        string = string[:-1]
        return string

class YAFIObjectCurrentStockPrice(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["symbol", "name", "price", "time"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)

class YAFIObjectHistoricalPrice(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["date", "open", "low", "high", "close", "volume", "adj_close"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)

class YAFIObjectHistoricalComponents(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["symbol", "company", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)

class YAFIObjectPositionHistoryAction(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["date", "action_string", "amount", "price"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)

class YAFIObjectDepotInfo(YAFIObject):

    def __init__(self, unnamed_list):
        param_list = ["cash"]
        YAFIObject.setParameterNames(self, param_list)
        YAFIObject.parse(self, unnamed_list)

class HistoricalAdjustedPriceRangeStack():

    def __init__(self):
        self.stack = []

    def getSize(self):
        return len(self.stack)

    def getList(self):
        return self.stack

    def addPrice(self, price_num):
        # instance of YAFIObjectHistoricalPrice
        self.stack.insert(0, price_num)

    def popPrice(self):
        return self.stack.pop(0)

    def hasMore(self):
        return not (len(self.stack) == 0)
