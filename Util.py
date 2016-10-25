import sys
import os
sys.path.append('/finsymbols')
import datetime
import SimEnv
import YAFIObjects

def removeCommasInQuotes(text):
    index = 0
    inQuote = False
    for char in text:
        if char == '"':
            inQuote = not inQuote
        elif char == ',':
            if inQuote:
                text = text[:index] + "-" + text[index + 1:]
        index += 1
    return text

def getDictFromCsvString(text):
    text = removeCommasInQuotes(text)
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

def parseDateString(date_string):
    s1 = date_string.split("-")
    year1 = int(s1[0])
    month1 = int(s1[1])
    day1 =int(s1[2])

    return UtilDate(year1, month1, day1)

def getCurrentDate():
    now = datetime.datetime.now()
    date = UtilDate(int(now.year), int(now.month), int(now.day))
    return date

def getHistoricalDataFilename(symbol):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "historical", symbol + ".csv")
    return path

def getDepotFolder(depot_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "depots", depot_name)
    return path

def getDepotInfoFile(depot_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "depots", depot_name, "info.depot")
    return path

def getPositionHistoryFilename(depot_name, portfolio_name, symbol):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "depots", depot_name, portfolio_name, symbol + ".posh")
    return path

def getPortfolioFolder(depot_name, portfolio_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "depots", depot_name, portfolio_name)
    return path

def compareDateStrings(date_str_1, date_str_2):
    if date_str_1 is None or date_str_2 is None:
        return False
    s1 = date_str_1.split("-")
    year1 = int(s1[0])
    month1 = int(s1[1])
    day1 =int(s1[2])

    s2 = date_str_2.split("-")
    year2 = int(s2[0])
    month2 = int(s2[1])
    day2 =int(s2[2])

    if year1 == year2 and month1 == month2 and day1 == day2:
        return True
    return False

def loadDepotInfo(depot_name):
    filename = getDepotInfoFile(depot_name)
    if os.path.exists(filename):
        fileh = open(filename, "r")
        csv_dict = getDictFromCsvString(fileh.read())
        info_obj = YAFIObjects.YAFIObjectDepotInfo(csv_dict[0])
        return info_obj
    return None

def loadPositionHistory(depot_name, portfolio_name, symbol):
    filename = getPositionHistoryFilename(depot_name, portfolio_name, symbol)
    if os.path.exists(filename):
        list_of_actions = []
        fileh = open(filename, "r")
        csv_dict = getDictFromCsvString(fileh.read())
        for key in csv_dict:
            api_obj = YAFIObjects.YAFIObjectPositionHistoryAction(csv_dict[key])
            date = parseDateString(api_obj.getData("date"))
            action_obj = SimEnv.PositionHistoryAction(date, api_obj.getData("action_string"), api_obj.getData("amount"), api_obj.getData("price"))
            list_of_actions.append(action_obj)
        return SimEnv.PositionHistory(symbol, list_of_actions)
    else:
        return SimEnv.PositionHistory(symbol, [])

def getFileList(path):
    return os.listdir(path)

def floatToStr(number):
    return "{:.2f}".format(number)

class UtilDate():

    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

    def __eq__(self, other):
        if self.year == other.getYear():
            if self.month == other.getMonth():
                if self.day == other.getDay():
                    return True
        return False

    def __lt__(self, other):
        if self.year < other.getYear():
            return True
        elif self.year == other.getYear():
            if self.month < other.getMonth():
                return True
            elif self.month == other.getMonth():
                if self.day < other.getDay():
                    return True
        return False

    def __gt__(self, other):
        if self.year > other.getYear():
            return True
        elif self.year == other.getYear():
            if self.month > other.getMonth():
                return True
            elif self.month == other.getMonth():
                if self.day > other.getDay():
                    return True
        return False

    def getYear(self):
        return self.year

    def getMonth(self):
        return self.month

    def getDay(self):
        return self.day

    def getAsString(self):
        day_string = str(self.day)
        month_string = str(self.month)
        if self.day - 10 < 0:
            day_string = "0" + str(self.day)
        if self.month - 10 < 0:
            month_string = "0" + str(self.month)
        return("" + str(self.year) + "-" + month_string + "-" + day_string)

    def getAfterDate(self, days):
        if self.day + days > 30:
            month = self.month + 1
            day = days - (30 - self.day)
            year = self.year
            if month == 13:
                month = 1
                year = self.year + 1
            return UtilDate(year, month, day)
        return UtilDate(self.year, self.month, self.day+days)

    def getNextDayDate(self):
        if self.day + 1 > 30:
            day = 1
            month = self.month + 1
            year = self.year
            if month > 12:
                year += 1
                month = 1
            return UtilDate(year, month, day)
        return UtilDate(self.year, self.month, self.day+1)

    def getBeforeDate(self, days):
        if self.day - days < 1:
            month = self.month - 1
            day = 30 - (days - self.day)
            year = self.year
            if month == 0:
                month = 12
                year = self.year - 1
            return UtilDate(year, month, day)
        return UtilDate(self.year, self.month, self.day-days)
