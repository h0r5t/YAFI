import YAFIApiWrapper
import Util

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        price_obj = api_wrapper.getCurrentStockPrice("AAPL")

        sp500TEST = api_wrapper.getSP500ComponentsForDate(Util.UtilDate(2015, 5, 10))
        print(sp500TEST)

if __name__ == "__main__":
    yafi = YAFI()
