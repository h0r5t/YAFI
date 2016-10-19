from urllib.request import urlopen
import csv
import codecs
import YAFIObjects
import os
import Util

class YAFIApiWrapper:

    def __init__(self):
        self.SP500HistoricalComponentsDict = {}
        self.loadSP500HistoricalData()
        return

    def getCurrentStockPrice(self, symbol):
        URL1 = "http://finance.yahoo.com/d/quotes.csv?s="
        URL2 = "&f=snat1"
        csv_dict = self.getCSVDictForApiCall(URL1 + symbol + URL2)
        price_obj = YAFIObjects.YAFIObjectCurrentStockPrice(csv_dict[0])
        return price_obj

    def getCSVDictForApiCall(self, url):

        response = urlopen(url)
        text = response.read().decode('utf8')
        dict1 = self.getDictFromCsvString(text)

        return dict1

    def getSP500HistoricalComponentsDict(self):
        return self.SP500HistoricalComponentsDict

    def getSP500ComponentsForDate(self, date):
        if date.getYear() < 2008:
            print("only data before 2008...")
            return None
        elif date.getYear() < 2009:
            return self.SP500HistoricalComponentsDict["2008"]
        elif date.getYear() < 2010:
            return self.SP500HistoricalComponentsDict["2009"]
        elif date.getYear() < 2011:
            return self.SP500HistoricalComponentsDict["2010"]
        elif date.getYear() < 2012:
            return self.SP500HistoricalComponentsDict["2011"]
        elif date.getYear() < 2013:
            return self.SP500HistoricalComponentsDict["2012"]
        elif date.getYear() < 2014:
            return self.SP500HistoricalComponentsDict["2013"]
        elif date.getYear() < 2015:
            return self.SP500HistoricalComponentsDict["2014"]
        elif date.getYear() < 2016:
            return self.SP500HistoricalComponentsDict["2015"]
        elif date.getYear() < 2017:
            if date.getMonth() < 6:
                return self.SP500HistoricalComponentsDict["2016"]
        return Util.loadSP500Symbols()

    def getDictFromCsvString(self, text):
        split = text.split(',')

        dict1 = {}
        counter = 0
        dict1[0] = []
        for element in split:
            element = element.replace('"','')
            if "\n" in element:
                newline_split = element.split("\n")
                dict1[counter].append(newline_split[0])
                if newline_split[1] == "":
                    break
                else:
                    dict1[counter+1] = []
                    dict1[counter+1].append(newline_split[1])
                    counter += 1
            else:
                dict1[counter].append(element)

        return dict1

    def loadSP500HistoricalData(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, "data", "sp500components_historical.csv")
        response = open(path)
        text = response.read()
        dict1 = self.getDictFromCsvString(text)

        list2016=[]
        list2015=[]
        list2014=[]
        list2013=[]
        list2012=[]
        list2011=[]
        list2010=[]
        list2009=[]
        list2008=[]
        for counter in range(0, len(dict1)):
            dataLine = dict1[counter]
            symbol = dataLine[0]

            if dataLine[2] == 'X':
                list2016.append(symbol)
            if dataLine[3] == 'X':
                list2015.append(symbol)
            if dataLine[4] == 'X':
                list2014.append(symbol)
            if dataLine[5] == 'X':
                list2013.append(symbol)
            if dataLine[6] == 'X':
                list2012.append(symbol)
            if dataLine[7] == 'X':
                list2011.append(symbol)
            if dataLine[8] == 'X':
                list2010.append(symbol)
            if dataLine[9] == 'X':
                list2009.append(symbol)
            if dataLine[10] == 'X':
                list2008.append(symbol)

        self.SP500HistoricalComponentsDict["2008"] = list2008
        self.SP500HistoricalComponentsDict["2009"] = list2009
        self.SP500HistoricalComponentsDict["2010"] = list2010
        self.SP500HistoricalComponentsDict["2011"] = list2011
        self.SP500HistoricalComponentsDict["2012"] = list2012
        self.SP500HistoricalComponentsDict["2013"] = list2013
        self.SP500HistoricalComponentsDict["2014"] = list2014
        self.SP500HistoricalComponentsDict["2015"] = list2015
        self.SP500HistoricalComponentsDict["2016"] = list2016
