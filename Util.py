import sys
import os
sys.path.append('/finsymbols')
import datetime

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

class UtilDate():

    def __init__(self, year, month, day):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)

    def getYear(self):
        return self.year

    def getMonth(self):
        return self.month

    def getDay(self):
        return self.day

    def getAsString(self):
        return("" + str(self.year) + "-" + str(self.month) + "-" + str(self.day))

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
