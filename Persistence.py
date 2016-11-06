import os
import YAFIApiWrapper
import Util

def downloadIndexData(api_wrapper, start_date):
    #S&P500
    symbol = "^GSPC"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "historical", symbol + ".csv")
    file_handle = open(path, "w")

    hist_prices_obj_list = api_wrapper.getHistoricalAdjustedPriceData(symbol, start_date, Util.getCurrentDate(), "daily")
    if len(hist_prices_obj_list) == 0:
        # error occurred
        file_handle.close()
        return False

    for obj in hist_prices_obj_list:
        file_handle.write(obj.getAsString() + "\n")

    file_handle.close()
    return True

def downloadAllHistoricalDataBasedOnSP500(api_wrapper, start_date):
    counter = 0
    error_counter = 0
    checked_symbols = []
    for year in range(2008, 2018):
        print("--- " + str(year) + " ---")
        date = Util.UtilDate(year, 3, 3)
        sp500symbols = api_wrapper.getSP500ComponentsForDate(date)
        for symbol in sp500symbols:
            if symbol in checked_symbols:
                continue
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(dir_path, "historical", symbol + ".csv")
            if dataIsPresent(path):
                # data is already downloaded, check for updates
                updateHistoricalDataForSymbol(api_wrapper, symbol, start_date, path)
            else:
                no_error = downloadHistoricalDataForSymbol(api_wrapper, symbol, start_date)
                if not no_error:
                    # print(str(year) + " " + str(error_counter) + " " + symbol)
                    error_counter += 1
                    os.remove(path)
                    checked_symbols.append(symbol)
                    continue
                # print(str(counter) + " " + symbol)
                counter += 1

            checked_symbols.append(symbol)

    deleteEmptyFiles(api_wrapper, start_date)

def dataIsPresent(path):
    if os.path.isfile(path):
        return True
    return False

def getRecencyDate(path):
    file_handle = open(path, "r")
    first_line = file_handle.readline()
    date_string = first_line.split(",")[0]
    return Util.parseDateString(date_string)

def getLatestPossibleUpdateDay(api_wrapper, symbol, recency_date):
    today_date = Util.getCurrentDate()
    obj = api_wrapper.getHistoricalAdjustedPriceData(symbol, recency_date, today_date, "daily")
    if len(obj) == 0:
        # empty data returned from API, whatever the reason is
        return None
    date_string = obj[0].getData("date")
    return date_string

def deleteEmptyFiles(api_wrapper, start_date):
    # delete empty files
    for year in range(2008, 2018):
        date = Util.UtilDate(year, 3, 3)
        sp500symbols = api_wrapper.getSP500ComponentsForDate(date)
        for symbol in sp500symbols:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            path = os.path.join(dir_path, "historical", symbol + ".csv")
            if os.path.isfile(path):
                check = open(path, "r")
                if check.read() == "":
                    check.close()
                    os.remove(path)

def updateHistoricalDataForSymbol(api_wrapper, symbol, start_date, path):
    recency_date = getRecencyDate(path)
    latest_update_day_possible = getLatestPossibleUpdateDay(api_wrapper, symbol, recency_date)
    if latest_update_day_possible is None or recency_date is None:
        print("delisted " + symbol)
        return
    elif not Util.compareDateStrings(recency_date.getAsString(), latest_update_day_possible):
        # needs to be updated
        os.remove(path)
        downloadHistoricalDataForSymbol(api_wrapper, symbol, start_date)
        print("updated " + symbol)

def downloadHistoricalDataForSymbol(api_wrapper, symbol, start_date):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "historical", symbol + ".csv")
    file_handle = open(path, "w")

    hist_prices_obj_list = api_wrapper.getHistoricalAdjustedPriceData(symbol, start_date, Util.getCurrentDate(), "daily")
    if len(hist_prices_obj_list) == 0:
        # error occurred
        file_handle.close()
        return False

    for obj in hist_prices_obj_list:
        file_handle.write(obj.getAsString() + "\n")

    file_handle.close()
    return True

if __name__ == "__main__":
    api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
    deleteEmptyFiles(api_wrapper, Util.UtilDate(2000, 1, 1))
    downloadAllHistoricalDataBasedOnSP500(api_wrapper, Util.UtilDate(2000, 1, 1))
    downloadIndexData(api_wrapper, Util.UtilDate(2000, 1, 1))
