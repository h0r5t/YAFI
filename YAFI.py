import YAFIApiWrapper
import Util

class YAFI:

    def __init__(self):
        sp500 = Util.loadSP500Symbols()

        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        price_obj = api_wrapper.getCurrentStockPrice("AAPL")
        print(price_obj.getParamList())
        print(price_obj.getData("price"))

if __name__ == "__main__":
    yafi = YAFI()
