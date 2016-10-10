import YAFIApiWrapper

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        price_obj = api_wrapper.getCurrentStockPrice("AAPL")
        print(price_obj.getParamList())
        print(price_obj.getData("price"))

if __name__ == "__main__":
    yafi = YAFI()
