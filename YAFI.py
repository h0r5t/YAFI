import YAFIApiWrapper
import Util
import SimEnv
import Algorithm
import Calculations
import time
import Plotting
import os


class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()

        graph = Plotting.generateBuySellGraph(api_wrapper, "test_depot", "test_portfolio", "EBAY", Util.UtilDate(2011, 10, 1), Util.UtilDate(2012, 12, 1))
        graph.show()

if __name__ == "__main__":
    yafi = YAFI()
