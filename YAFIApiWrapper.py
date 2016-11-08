from urllib.request import urlopen
from urllib.error import HTTPError
import csv
import codecs
import YAFIObjects
import SimEnv
import os
import Util
import finsymbols

class YAFIApiWrapper:

    def __init__(self):
        self.SP500HistoricalComponentsDict = {}
        self.loadSP500HistoricalData()
        self.sp500symbols = []
        self.price_history_cache = {}

    def cachePriceData(self, symbol):
        file_name = Util.getHistoricalDataFilename(symbol)
        if not os.path.isfile(file_name):
            return False
        fhandle = open(file_name, "r")
        csv_dict = Util.getDictFromCsvString(fhandle.read())
        self.price_history_cache[symbol] = csv_dict
        return True

    def getAdjustedPriceDataRangeStack(self, symbol, start_date, end_date):
        if symbol not in self.price_history_cache:
            successful = self.cachePriceData(symbol)
            if not successful:
                return None
        csv_dict = self.price_history_cache[symbol]
        stack = YAFIObjects.HistoricalAdjustedPriceRangeStack()
        in_range = False
        for index in csv_dict:
            date_string = csv_dict[index][0]
            cur_date = Util.parseDateString(date_string)
            if not in_range:
                if cur_date < end_date or cur_date == end_date:
                    in_range = True
                    hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
                    stack.addPriceObject(hist_price_obj)
            else:
                if cur_date < start_date:
                    break
                else:
                    hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
                    stack.addPriceObject(hist_price_obj)
        return stack

    def getAdjustedPriceDataRangeStackForAmountOfDays(self, symbol, end_date, days):
        if symbol not in self.price_history_cache:
            successful = self.cachePriceData(symbol)
            if not successful:
                return None
        csv_dict = self.price_history_cache[symbol]
        stack = YAFIObjects.HistoricalAdjustedPriceRangeStack()
        in_range = False
        for index in csv_dict:
            date_string = csv_dict[index][0]
            cur_date = Util.parseDateString(date_string)
            if not in_range:
                if cur_date < end_date or cur_date == end_date:
                    in_range = True
                    hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
                    stack.addPriceObject(hist_price_obj)
            else:
                if days == 1:
                    break
                else:
                    hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
                    stack.addPriceObject(hist_price_obj)
                    days -= 1
        return stack

    def getAdjustedPriceForDate(self, symbol, date, recursion_counter=7):
        data = self.getAdjustedPriceDataForDate(symbol, date)
        if data is None:
            return self.getAdjustedPriceForDate(symbol, date.getBeforeDate(1), recursion_counter-1)
        return float(data.getData("adj_close"))

    def getAdjustedPriceDataForDate(self, symbol, date):
        if symbol not in self.price_history_cache:
            successful = self.cachePriceData(symbol)
            if not successful:
                return None
        csv_dict = self.price_history_cache[symbol]
        for index in csv_dict:
            date_string = csv_dict[index][0]
            if Util.compareDateStrings(date_string, date.getAsString()):
                hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
                return hist_price_obj
        # return self.getRecursiveAdjPrice(5, symbol, date.getNextDayDate())
        return None

    def getHistoricalAdjustedPriceData(self, symbol, start_date, end_date, time_interval):
        d1 = str(start_date.getDay())
        m1 = str(start_date.getMonth() - 1)
        y1 = str(start_date.getYear())
        d2 = str(end_date.getDay())
        m2 = str(end_date.getMonth() - 1)
        y2 = str(end_date.getYear())

        if time_interval == "daily":
            time_interval = "d"
        elif time_interval == "weekly":
            time_interval = "w"
        elif time_interval == "monthly":
            time_interval = "m"

        URL = "http://ichart.finance.yahoo.com/table.csv?s=" + symbol + "&b=" + d1
        URL += "&a=" + m1 + "&c=" + y1 + "&e=" + d2 + "&d=" + m2 + "&f=" + y2 + "&g="
        URL += time_interval + "&ignore=.cvs"

        csv_dict = self.getCSVDictForApiCall(URL)
        price_obj_list = []
        for index in csv_dict:
            if (str(index) == "0"):
                continue
            hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(csv_dict[index])
            price_obj_list.append(hist_price_obj)
        return price_obj_list

    def getPositionHistoryActionListForDateRange(self, depot_name, portfolio_name, symbol, start_date, end_date):
        posh_file = Util.getPositionHistoryFilename(depot_name, portfolio_name, symbol)
        fileh = open(posh_file, "r")
        csv_dict = Util.getDictFromCsvString(fileh.read())

        pos_his_action_list = []
        in_range = False
        for index in csv_dict:
            date_string = csv_dict[index][0]
            cur_date = Util.parseDateString(date_string)
            if not in_range:
                if cur_date < end_date or cur_date == end_date:
                    in_range = True
                    action_string = csv_dict[index][1]
                    amount = int(csv_dict[index][2])
                    price = float(csv_dict[index][3])
                    action = SimEnv.PositionHistoryAction(cur_date, action_string, amount, price)
                    pos_his_action_list.append(action)
            else:
                if cur_date < start_date:
                    break
                else:
                    action_string = csv_dict[index][1]
                    amount = int(csv_dict[index][2])
                    price = float(csv_dict[index][3])
                    action = SimEnv.PositionHistoryAction(cur_date, action_string, amount, price)
                    pos_his_action_list.append(action)
        return pos_his_action_list


    def getCurrentStockPrice(self, symbol):
        URL1 = "http://finance.yahoo.com/d/quotes.csv?s="
        URL2 = "&f=snat1"
        csv_dict = self.getCSVDictForApiCall(URL1 + symbol + URL2)
        price_obj = YAFIObjects.YAFIObjectCurrentStockPrice(csv_dict[0])
        return price_obj

    def getCSVDictForApiCall(self, url):
        dict1 = {}
        try:
            response = urlopen(url)
            text = response.read().decode('utf8')
            dict1 = Util.getDictFromCsvString(text)
        except HTTPError:
            pass

        return dict1

    def getSP500Symbols(self):
        if len(self.sp500symbols) == 0:
            dict1 = finsymbols.get_sp500_symbols()
            self.sp500symbols = []
            for element in dict1:
                self.sp500symbols.append(element["symbol"])
            return self.sp500symbols
        else:
            return self.sp500symbols

    def getSP500HistoricalComponentsDict(self):
        return self.SP500HistoricalComponentsDict

    def getSP500ComponentsForDate(self, date):
        # CARE: FAKE FOR TESTING

        # return ["AAPL", "MSFT", "BAC", "NFLX", "ORCL", "AGN", "BBY", "EBAY"]

        # FAKE END
        if date.getYear() < 2008:
            print("only data after 2008...")
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
        return self.getSP500Symbols()

    def loadSP500HistoricalData(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(dir_path, "data", "sp500components_historical.csv")
        response = open(path)
        text = response.read()
        dict1 = Util.getDictFromCsvString(text)

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

            symbol = symbol.replace(".", "-")
            #symbol = symbol.replace(" (Old)", "")

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
