from os import path
import shutil

import Calculations
import SimEnv
import Util
import YAFIApiWrapper


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

    def __init__(self, sim_env, api_wrapper, cash=-1, risk_factor=0.002, costs_per_order=6, intelligent_balancing_threshold=500, verbose=False):
        self.init(sim_env, api_wrapper)
        self.sim_env = sim_env
        self.api_wrapper = api_wrapper
        
        self.cash = cash
        self.risk_factor = risk_factor
        self.costs_per_order = costs_per_order
        self.intelligent_balancing = True
        self.intelligent_balancing_threshold = intelligent_balancing_threshold
        self.balancing_trades = 0
        self.verbose = verbose
        
        self.is_completed = False
        
    def isCompleted(self):
        return self.is_completed
    
    def getRiskFactor(self):
        return self.risk_factor
    
    def getCPO(self):
        return self.costs_per_order
    
    def getIntBalTreshold(self):
        return self.intelligent_balancing_threshold

            
    def deleteDepot(self, name):
        depot_folder = Util.getDepotFolder(name)
        if path.exists(depot_folder):
            shutil.rmtree(depot_folder)
    
    def prepare(self, start_date, end_date):
        if self.cash == -1:
            self.starting_cash = Util.getDepotValueForSimulation(sim_env.getCurrentDate().getYear())
        else:
            self.starting_cash = self.cash
        if self.verbose:
            print("initial cash: " + str(self.starting_cash) + "")
        depot_name = str(start_date.getYear()) + "-" + str(end_date.getYear()) + "_rf=" + str(self.risk_factor) + "_bt=" + str(self.intelligent_balancing_threshold)
        self.deleteDepot(depot_name)
        self.depot = SimEnv.Depot(self.sim_env, self.api_wrapper, depot_name, self.starting_cash)
        self.portfolio = SimEnv.Portfolio(self.sim_env, self.depot, "test_portfolio", self.costs_per_order)
        self.depot.addPortfolio(self.portfolio)
        self.setDaysToSkip(6)
        self.balance_day = False
        
        self.pos_num_list = []

    def doLogic(self, date):
        if self.verbose:
            print(date.getAsString())
        sp500symbols = self.api_wrapper.getSP500ComponentsForDate(date)
        momentum_dict, sorted_momentum_list, symbols_under_avg, symbols_with_gap = self.getMomentumData(date, sp500symbols)

        # SELL
        symbols_to_sell, reasons_to_sell = self.getSymbolsToSell(date, sorted_momentum_list, symbols_under_avg, symbols_with_gap, sp500symbols)
        for i in range(0, len(symbols_to_sell)):
            self.portfolio.sellAll(symbols_to_sell[i], reasons_to_sell[i])

        # BALANCE
        if self.balance_day:
            self.balancePositions(momentum_dict, date)
            self.balance_day = False
        else:
            self.balance_day = True

        # BUY
        if self.sp500IndexIsAbove200Avg(date):
            symbols_in_portfolio = self.portfolio.getSymbols()
            for symbol in sorted_momentum_list:
                optimal_amount = int(momentum_dict[symbol].calculatePositionSize(self.depot.getCurrentValue(), self.risk_factor))
                money_left = True
                if symbol not in symbols_in_portfolio:
                    money_left = self.portfolio.buy(symbol, optimal_amount, "new")
                else:
                    current_amount = int(self.portfolio.getPosition(symbol).getCurrentAmount())
                    if optimal_amount > current_amount:
                        money_left = self.portfolio.buy(symbol, int(optimal_amount - current_amount), "buy")
                if money_left == False:
                    break
                
        # MAKE TRADES

        # MAKE SNAPSHOT
        # self.portfolio.makeSnapshot()
        pos_num = len(self.portfolio.getPositions())
        self.pos_num_list.append(pos_num)
        
        if self.verbose:
            print("cash: " + str(self.depot.getCash()))

    def sp500IndexIsAbove200Avg(self, date):
        price_stack = self.api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays("^GSPC", date, 205)
        if price_stack is None or price_stack.getSize() < 200:
            return False
        current_price = float(price_stack.getLastObject().getData("adj_close"))
        avg_200 = Calculations.calculateMovingAverage(price_stack, 200)
        return current_price > avg_200

    def balancePositions(self, momentum_dict, date):
        depot_val = self.depot.getCurrentValue()
        for pos in self.portfolio.getPositions():
            symbol = pos.getSymbol()
            cur_amount = int(pos.getCurrentAmount())
            new_amount = momentum_dict[symbol].calculatePositionSize(depot_val, self.risk_factor)
            atr_string = str(momentum_dict[symbol].getATR())
            delta = int(new_amount - cur_amount)
            if delta > 0:
                if self.intelligent_balancing == False:
                    self.portfolio.buy(symbol, delta, "balancing (atr=" + atr_string + ")")
                    self.balancing_trades += 1
                else:
                    # balance_state_amount = pos.getBalanceState().getBalanceAmount()
                    price_for_one = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, date))
                    value_of_balancing = delta * price_for_one
                    if value_of_balancing > self.intelligent_balancing_threshold:
                        self.portfolio.buy(symbol, delta, "balancing (atr=" + atr_string + ")")
                        self.balancing_trades += 1
                    
            elif delta < 0:
                if self.intelligent_balancing == False:
                    self.portfolio.sell(symbol, abs(delta), "balancing (atr=" + atr_string + ")")
                    self.balancing_trades += 1
                else:
                    # balance_state_amount = pos.getBalanceState().getBalanceAmount()
                    price_for_one = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, date))
                    value_of_balancing = delta * price_for_one
                    if value_of_balancing < -self.intelligent_balancing_threshold:
                        self.portfolio.sell(symbol, abs(delta), "balancing (atr=" + atr_string + ")")
                        self.balancing_trades += 1

    def getSymbolsToSell(self, date, sorted_momentum_list, symbols_under_avg, symbols_with_gap, sp500symbols):
        symbols_to_sell = []
        reasons_to_sell = []
        top100_list = sorted_momentum_list[:100]
        for pos in self.portfolio.getPositions():
            symbol = pos.getSymbol()
            if symbol not in sp500symbols:
                symbols_to_sell.append(symbol)
                reasons_to_sell.append("out of sp500")
                continue
            elif symbol in symbols_under_avg:
                symbols_to_sell.append(symbol)
                reasons_to_sell.append("under 100 day avg")
                continue
            elif symbol in symbols_with_gap:
                symbols_to_sell.append(symbol)
                reasons_to_sell.append("gap too big")
                continue
            elif symbol not in top100_list:
                symbols_to_sell.append(symbol)
                reasons_to_sell.append("not top 100 momentum")
                continue

        return (symbols_to_sell, reasons_to_sell)

    def getMomentumData(self, date, sp500symbols):
        momentum_dict = {}
        symbols_with_gap = []
        symbols_under_avg = []
        counter = 0
        for symbol in sp500symbols:
            counter += 1
            price_stack = self.api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays(symbol, date, 105)
            if price_stack is None or price_stack.getSize() < 100:
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

            # print("---")

        # sort momentum_dict descending by slope
        symbols_sorted = sorted(momentum_dict, key=lambda symbol: momentum_dict[symbol].slope, reverse=True)
        return (momentum_dict, symbols_sorted, symbols_under_avg, symbols_with_gap)

    def cleanUp(self):
        self.depot.save()

        # p_composition_history = self.portfolio.getCompositionHistory()
            
        self.depot_end_val = self.depot.getCurrentValue()
        result = (self.depot_end_val - self.starting_cash) / self.starting_cash
        self.result_yield = result * 100            
            
        self.total_trades = self.portfolio.getTotalAmountOfTrades()
        
        self.transaction_costs = self.total_trades * self.costs_per_order
        
        sum1 = 0
        for n in self.pos_num_list:
            sum1 += n
        self.avg_position_num = int(sum1 / len(self.pos_num_list))
        
        # top trades
        symbol_revenue = {}
        for pos in self.portfolio.getAllClosedPositions():
            ph = pos.getPositionHistory()
            symbol_revenue[ph.getSymbol()] = ph.getTotalRevenue()
        revenues_sorted = sorted(symbol_revenue, key=lambda symbol: symbol_revenue[symbol], reverse=True)
        self.top_trades = []
        for key in revenues_sorted:
            self.top_trades.append(str(key) + ": " + str(symbol_revenue[key]))
        
        if self.verbose:
            print("--------")
            print("depot value: " + str(self.depot_end_val))
            print("yield: " + str(self.result_yield))
            print("trades: " + str(self.total_trades))
            print("avg positions: " + str(self.avg_position_num))
            print("top trades: " + str(self.top_trades))
            
        self.is_completed = True
        
    def getResults(self):
        return (self.depot_end_val, self.result_yield, self.total_trades, self.transaction_costs, self.avg_position_num, self.top_trades, self.balancing_trades)

if __name__ == "__main__":
    start_date = Util.UtilDate(2014, 1, 1)
    end_date = Util.UtilDate(2014, 12, 31)
    
    api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
    sim_env = SimEnv.SimEnv(start_date)
    algo = TestAlgorithm(sim_env, api_wrapper, 100000, verbose=True, risk_factor=0.001, intelligent_balancing_threshold=0)

    sim_env.simulateAlgorithm(algo, start_date, end_date)
