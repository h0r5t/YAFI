import YAFIApiWrapper
import Util
import SimEnv
import Algorithm
import Calculations
import time
import View

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        start_date = Util.UtilDate(2015, 10, 1)
        end_date = Util.UtilDate(2016, 10, 20)

        graph = View.Graph("Adj. Close", "day", "value")
        view1 = View.PriceView(api_wrapper, "INTC", start_date, end_date)
        view2 = View.PriceView(api_wrapper, "MSFT", start_date, end_date)
        graph.addView(view1)
        graph.addView(view2)

        graph.show()

if __name__ == "__main__":
    yafi = YAFI()
