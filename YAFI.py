import YAFIApiWrapper
import Util
import SimEnv
import Algorithm
import Calculations
import time
import View
import os


class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()

        graph = View.generateBuySellGraph(api_wrapper, "test_depot", "test_portfolio", "SNDK", Util.UtilDate(2011, 10, 1), Util.UtilDate(2012, 3, 1))
        graph.show()

if __name__ == "__main__":
    yafi = YAFI()
