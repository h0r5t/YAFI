import YAFIApiWrapper
import Util
import SimEnv
import Algorithm
import Calculations
import time

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()

        # sim_env = SimEnv.SimEnv()
        # algo = Algorithm.TestAlgorithm(sim_env, api_wrapper)
        # sim_env.simulateAlgorithm(algo, Util.UtilDate(2009, 1, 1), Util.UtilDate(2009, 3, 30), 1)

        obj = api_wrapper.getHistoricalAdjustedPriceData("^GSPC", Util.UtilDate(2016, 10, 22), Util.UtilDate(2016, 11, 25), "daily")
        for key in obj:
            print(key.getData("date") + " " + key.getData("adj_close"))

        return

        price_stack = api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays("AAPL", Util.UtilDate(2016, 10, 22), 105)
        avg_100 = Calculations.calculateMovingAverage(price_stack, 100)
        atr = Calculations.calculateATR(api_wrapper, price_stack)
        print(atr)
        print(avg_100)
        print(Calculations.calculatePositionSize(100000, atr))

        return

        start_time = time.time()
        print("starting...")
        best_dict = {}
        date = Util.UtilDate(2013, 1, 1)
        sp500symbols = api_wrapper.getSP500ComponentsForDate(date)
        for symbol in sp500symbols:
            adj_slope = Calculations.getAdjustedAnnualizedSlope(api_wrapper, symbol, date)
            print(symbol + ": " + str(adj_slope))
            if adj_slope > 100:
                best_dict[symbol] = adj_slope
        print("computed in: " + str(time.time() - start_time))

        print("\nTOP MOMENTUM:")
        for key in best_dict:
            print(key + ": " + str(best_dict[key]))

if __name__ == "__main__":
    yafi = YAFI()
