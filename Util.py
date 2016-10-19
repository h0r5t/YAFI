import sys
sys.path.append('/finsymbols')
import finsymbols

def loadSP500Symbols():
    dict1 = finsymbols.get_sp500_symbols()
    list_of_symbols = []
    for element in dict1:
        list_of_symbols.append(element["symbol"])
    return list_of_symbols

class UtilDate():

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def getYear(self):
        return self.year

    def getMonth(self):
        return self.month

    def getDay(self):
        return self.day

    def getString(self):
        return("" + self.year + "-" + self.month + "-" + self.day) 
