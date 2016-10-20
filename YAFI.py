import YAFIApiWrapper
import Util

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        a = api_wrapper.getAdjustedPriceDataForDate("AAPL", Util.UtilDate(2010, 10, 9))
        print(a.getAsString())

if __name__ == "__main__":
    yafi = YAFI()
