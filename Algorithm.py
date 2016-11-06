import SimEnv
import YAFIApiWrapper
import Util
import Calculations

class Algorithm:

    def init(self, sim_env, api_wrapper):
        self.sim_env = sim_env
        self.api_wrapper = api_wrapper
        self.day_counter = 0
        self.days_to_skip = 0

    def setDaysToSkip(self, days):
        self.days_to_skip = days

    def prepare(self):
        pass

    def preLogic(self, date):
        if self.day_counter == 0:
            self.doLogic(date)
        self.day_counter += 1
        if self.day_counter > self.days_to_skip:
            self.day_counter = 0

    def doLogic(self, date):
        pass

    def cleanUp(self):
        pass

class TestAlgorithm(Algorithm):

    def __init__(self, sim_env, api_wrapper):
        self.init(sim_env, api_wrapper)
        self.depot = SimEnv.Depot(sim_env, api_wrapper, "test_depot", 10000)
        self.portfolio = SimEnv.Portfolio(sim_env, self.depot, "test_portfolio")
        self.depot.addPortfolio(self.portfolio)
        self.setDaysToSkip(6)
        self.balance_day = False

    def prepare(self):
        pass

    def doLogic(self, date):
        print(date.getAsString())
        print("momentum")
        sp500symbols = self.api_wrapper.getSP500ComponentsForDate(date)
        momentum_dict, sorted_momentum_list, symbols_under_avg, symbols_with_gap = self.getMomentumData(date, sp500symbols)

        # SELL
        print("sell")
        symbols_to_sell = self.getSymbolsToSell(date, sorted_momentum_list, symbols_under_avg, symbols_with_gap, sp500symbols)
        for symbol in symbols_to_sell:
            self.portfolio.sellAll(symbol)

        # BALANCE
        print("balance")
        if self.balance_day:
            self.balancePositions(momentum_dict)
            self.balance_day = False
        else:
            self.balance_day = True

        # BUY
        print("buy")
        if self.sp500IndexIsAbove200Avg(date):
            symbols_in_portfolio = self.portfolio.getSymbols()
            for symbol in sorted_momentum_list:
                optimal_amount = momentum_dict[symbol].calculatePositionSize(self.depot.getCurrentValue())
                money_left = True
                if symbol not in symbols_in_portfolio:
                    money_left = self.portfolio.buy(symbol, optimal_amount)
                else:
                    current_amount = self.portfolio.getPosition(symbol).getCurrentAmount()
                    if optimal_amount > current_amount:
                        money_left = self.portfolio.buy(symbol, optimal_amount - current_amount)
                if money_left == False:
                    break

    def sp500IndexIsAbove200Avg(self, date):
        price_stack = self.api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays("^GSPC", date, 205)
        if price_stack is None or price_stack.getSize() < 200:
            return False
        current_price = float(price_stack.getLastObject().getData("adj_close"))
        avg_200 = Calculations.calculateMovingAverage(price_stack, 200)
        return current_price > avg_200

    def balancePositions(self, momentum_dict):
        for pos in self.portfolio.getPositions():
            symbol = pos.getSymbol()
            cur_amount = pos.getCurrentAmount()
            new_amount = momentum_dict[symbol].calculatePositionSize(self.depot.getCurrentValue())
            delta = new_amount - cur_amount
            if delta > 0:
                self.portfolio.buy(symbol, delta)
            elif delta < 0:
                self.portfolio.sell(symbol, abs(delta))

    def getSymbolsToSell(self, date, sorted_momentum_list, symbols_under_avg, symbols_with_gap, sp500symbols):
        symbols_to_sell = []
        top100_list = sorted_momentum_list[:100]
        for pos in self.portfolio.getPositions():
            symbol = pos.getSymbol()
            if symbol not in sp500symbols:
                symbols_to_sell.append(symbol)
                continue
            if symbol not in top100_list:
                symbols_to_sell.append(symbol)
                continue
            elif symbol in symbols_under_avg:
                symbols_to_sell.append(symbol)
                continue
            elif symbol in symbols_with_gap:
                symbols_to_sell.append(symbol)

        return symbols_to_sell

    def getMomentumData(self, date, sp500symbols):
        momentum_dict = {}
        symbols_with_gap = []
        symbols_under_avg = []
        counter = 0
        for symbol in sp500symbols:
            counter += 1
            price_stack = self.api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays(symbol, date, 105)
            if price_stack is None or price_stack.getSize() < 90:
                continue
            current_price = float(price_stack.getLastObject().getData("adj_close"))
            avg_100 = Calculations.calculateMovingAverage(price_stack, 100)
            if current_price < avg_100:
                symbols_under_avg.append(symbol)
                continue
            if Calculations.gapExists(price_stack, 100):
                symbols_with_gap.append(symbol)
                continue
            
            # get the momentum stuff
            slope = Calculations.getAdjustedAnnualizedSlope(price_stack)
            atr = Calculations.calculateATR(price_stack)
            momentum_data = Calculations.MomentumData(slope, atr)
            momentum_dict[symbol] = momentum_data

        # sort momentum_dict descending by slope
        symbols_sorted = sorted(momentum_dict, key = lambda symbol: momentum_dict[symbol].slope, reverse=True)
        return (momentum_dict, symbols_sorted, symbols_under_avg, symbols_with_gap)

    def cleanUp(self):
        self.depot.save()

if __name__ == "__main__":
    api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
    sim_env = SimEnv.SimEnv()
    algo = TestAlgorithm(sim_env, api_wrapper)

    start_date = Util.UtilDate(2015, 1, 1)
    end_date = Util.UtilDate(2015, 2, 1)
    sim_env.simulateAlgorithm(algo, start_date, end_date)
