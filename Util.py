import datetime
import os
import sys
import time

import SimEnv
import YAFIObjects
import numpy as np


sys.path.append('/finsymbols')


class Timer():

    def __init__(self):
        self.last_time = 0
        self.times_dict = {}

    def start(self):
        self.last_time = time.time()

    def addTime(self, name):
        self.times_dict[name] = time.time() - self.last_time
        self.last_time = time.time()

    def printTimes(self):
        for key in self.times_dict:
            print(key + " " + str(self.times_dict[key]))
            
def getDepotValueForSimulation(year):
    yearly_yields = {}
    yearly_yields[1999] = 41
    yearly_yields[2000] = -9.6
    yearly_yields[2001] = -0.7
    yearly_yields[2002] = -3
    yearly_yields[2003] = 41.8
    yearly_yields[2004] = 13.7
    yearly_yields[2005] = 9.3
    yearly_yields[2006] = 2.4
    yearly_yields[2007] = 17.3
    yearly_yields[2008] = -8.5
    yearly_yields[2009] = 14.0
    yearly_yields[2010] = 11.7
    yearly_yields[2011] = -9.3
    yearly_yields[2012] = 18.9
    yearly_yields[2013] = 37.5
    yearly_yields[2014] = 18.4
    
    value = 100000
    year_counter = 1999
    
    while True:
        if year_counter < year:
            value = value + value * (yearly_yields[year_counter] * 0.01)
            year_counter += 1
        else:
            break
        
    return int(value)

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
        element = element.replace('"', '')
        if "\n" in element:
            newline_split = element.split("\n")
            dict1[counter].append(newline_split[0])
            if newline_split[1] == "":
                break
            else:
                dict1[counter + 1] = []
                dict1[counter + 1].append(newline_split[1])
                counter += 1
        else:
            dict1[counter].append(element)

    return dict1

def parseDateString(date_string):
    s1 = date_string.split("-")
    year1 = int(s1[0])
    month1 = int(s1[1])
    day1 = int(s1[2])

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

def getBalanceStateFilename(depot_name, portfolio_name, symbol):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "depots", depot_name, portfolio_name, symbol + ".bal")
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
    day1 = int(s1[2])

    s2 = date_str_2.split("-")
    year2 = int(s2[0])
    month2 = int(s2[1])
    day2 = int(s2[2])

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
            action_obj = SimEnv.PositionHistoryAction(date, api_obj.getData("action_string"), api_obj.getData("amount"), api_obj.getData("price"), api_obj.getData("reason"))
            list_of_actions.append(action_obj)
        return SimEnv.PositionHistory(symbol, list_of_actions)
    else:
        return SimEnv.PositionHistory(symbol, [])
    
def loadBalanceState(depot_name, portfolio_name, symbol):
    filename = getBalanceStateFilename(depot_name, portfolio_name, symbol)
    if os.path.exists(filename):
        fileh = open(filename, "r")
        value = int(fileh.read())
        return SimEnv.BalanceState(value)
    return SimEnv.BalanceState(0)

def getFileList(path):
    return os.listdir(path)

def floatToStr(number):
    return "{:.2f}".format(number)

class UtilDate():

    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.month_days_dict = {}
        self.month_days_dict[1] = 31
        self.month_days_dict[2] = 28 + int(self.year % 4 == 0)
        self.month_days_dict[3] = 31
        self.month_days_dict[4] = 30
        self.month_days_dict[5] = 31
        self.month_days_dict[6] = 30
        self.month_days_dict[7] = 31
        self.month_days_dict[8] = 31
        self.month_days_dict[9] = 30
        self.month_days_dict[10] = 31
        self.month_days_dict[11] = 30
        self.month_days_dict[12] = 31

        if self.day > self.month_days_dict[self.month]:
            self.day = self.month_days_dict[self.month]

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

    def getBeforeDayDate(self):
        return self.getBeforeDate(1)

    def getAfterDate(self, days):
        return parseDateString(str(np.datetime64(self.getAsString()) + np.timedelta64(days, 'D')))

    def getNextDayDate(self):
        return self.getAfterDate(1)
    
    def getNextYearDate(self):
        return UtilDate(self.year + 1, self.month, self.day)

    def getBeforeDate(self, days):
        return parseDateString(str(np.datetime64(self.getAsString()) - np.timedelta64(days, 'D')))
