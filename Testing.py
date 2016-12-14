import Algorithm
import Calculations
import SimEnv
import Util
import YAFIApiWrapper


class PrintStuffAlgorithm(Algorithm.Algorithm):

    def __init__(self, sim_env, api_wrapper, cash=-1):
        self.init(sim_env, api_wrapper)
        self.setDaysToSkip(6)

    def prepare(self):
        pass

    def doLogic(self, date):
        print(date.getAsString())
        sp500symbols = self.api_wrapper.getSP500ComponentsForDate(date)
        momentum_dict, sorted_momentum_list, symbols_under_avg, symbols_with_gap = self.getMomentumData(date, sp500symbols)
        
        for i in range(0, 10):
            symbol = sorted_momentum_list[i]
            slope = momentum_dict[symbol].getSlope()
            print(symbol + ": " + str(slope))
        
        if "BBY" in momentum_dict:
            slope_bby = momentum_dict["BBY"].getSlope()
            print("BBY: " + str(slope_bby))

    def getMomentumData(self, date, sp500symbols):
        momentum_dict = {}
        symbols_with_gap = []
        symbols_under_avg = []
        counter = 0
        for symbol in sp500symbols:
            
            counter += 1
            price_stack = self.api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays(symbol, date, 105)
            if price_stack is None or price_stack.getSize() < 100:
                if symbol == "BBY":
                    print("bby stack error")
                continue
            current_price = float(price_stack.getLastObject().getData("adj_close"))
            avg_100 = Calculations.calculateMovingAverage(price_stack, 100)
            if current_price < avg_100:
                symbols_under_avg.append(symbol)
                if symbol == "BBY":
                    print("bby under avg")
                continue
            if Calculations.gapExists(price_stack, 100):
                symbols_with_gap.append(symbol)
                if symbol == "BBY":
                    print("bby gap exists")
                continue


            # get the momentum stuff
            slope = Calculations.getAdjustedAnnualizedSlope(price_stack)
            atr = Calculations.calculateATR(price_stack)

            momentum_data = Calculations.MomentumData(slope, atr)
            momentum_dict[symbol] = momentum_data

            # print("---")

        # sort momentum_dict descending by slope
        symbols_sorted = sorted(momentum_dict, key=lambda symbol: momentum_dict[symbol].slope, reverse=True)
        return (momentum_dict, symbols_sorted, symbols_under_avg, symbols_with_gap)

    def cleanUp(self):
        pass

if __name__ == "__main__":
    start_date = Util.UtilDate(2013, 1, 1)
    end_date = Util.UtilDate(2013, 12, 31)
    
    api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
    sim_env = SimEnv.SimEnv(start_date)
    algo = PrintStuffAlgorithm(sim_env, api_wrapper)

    sim_env.simulateAlgorithm(algo, start_date, end_date)
