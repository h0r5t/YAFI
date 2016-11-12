import Algorithm
import Calculations
import Plotting
import SimEnv
import Util
import YAFIApiWrapper


class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()

        graph = Plotting.generateBuySellGraph(api_wrapper, "test_depot", "test_portfolio", "BEN", Util.UtilDate(2009, 1, 1), Util.UtilDate(2009, 12, 31))
        graph.show()

if __name__ == "__main__":
    yafi = YAFI()
