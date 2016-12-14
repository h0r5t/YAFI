from multiprocessing import Process, Queue
import os

from Algorithm import TestAlgorithm
import SimEnv
import Util
import YAFIApiWrapper
import YAFIObjects


class ApiWrapperMock():
    
    def __init__(self, start_date, end_date):
        self.api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        self.price_history_cache = {}
        self.symbol_date_price_hashmap = {}
        
        self.createCache(start_date, end_date)
        
    def cachePriceData(self, symbol):
        file_name = Util.getHistoricalDataFilename(symbol)
        if not os.path.isfile(file_name):
            return False
        fhandle = open(file_name, "r")
        csv_dict = Util.getDictFromCsvString(fhandle.read())
        self.price_history_cache[symbol] = csv_dict

        # fill hashmap with per-date data
        date_price_dict = {}
        for index in csv_dict:
            date_string = csv_dict[index][0]
            date_price_dict[date_string] = csv_dict[index]
        self.symbol_date_price_hashmap[symbol] = date_price_dict
        return True

    def createCache(self, start_date, end_date):
        cached_symbols = []
        for year in range(start_date.getYear() - 1, end_date.getYear() + 1):
            sp500symbols = self.api_wrapper.getSP500ComponentsForDate(Util.UtilDate(year, 3, 3))
            for symbol in sp500symbols:
                if symbol in cached_symbols:
                    continue
                else:
                    self.cachePriceData(symbol)
                    cached_symbols.append(symbol)
                    
    def getSP500ComponentsForDate(self, date):
        return self.api_wrapper.getSP500ComponentsForDate(date)
                    
    def getAdjustedPriceDataRangeStackForAmountOfDays(self, symbol, end_date, days):
        if symbol not in self.price_history_cache:
            return None

        fail_counter = 0
        stack = YAFIObjects.HistoricalAdjustedPriceRangeStack()
        date_prices_map = self.symbol_date_price_hashmap[symbol]
        date_counter = end_date
        while True:
            date_string = date_counter.getAsString()
            if days == 0 or fail_counter >= 7:
                break
            if date_string in date_prices_map:
                hist_price_obj = YAFIObjects.YAFIObjectHistoricalPrice(date_prices_map[date_string])
                stack.addPriceObject(hist_price_obj)
                days -= 1
                fail_counter = 0
            date_counter = date_counter.getBeforeDayDate()
            fail_counter += 1
        return stack


class ParallelRunner(Process):
    
    def __init__(self, queue, sim_env, algorithm, start_date, end_date):
        super(ParallelRunner, self).__init__()
        self.queue = queue
        self.sim_env = sim_env
        self.algorithm = algorithm
        self.start_date = start_date
        self.end_date = end_date
        
        self.future = Future(algorithm)
    
    def run(self):
        self.sim_env.simulateAlgorithm(self.algorithm, self.start_date, self.end_date)
        self.queue.put(self.algorithm.getResults()[0])
        
    def isCompleted(self):
        return self.future.isCompleted()
    
    def getResults(self):
        return self.future.getObject().getResults()
    
    def getAlgo(self):
        return self.algorithm


class Future():
    
    def __init__(self, obj):
        self.obj = obj
        
    def isCompleted(self):
        if self.obj.isCompleted():
            return True
        return False
        
    def getObject(self):
        return self.obj


if __name__ == '__main__':
    start_date = Util.UtilDate(2014, 1, 1)
    end_date = Util.UtilDate(2014, 3, 31)
    costs = [6]
    risk_factors = [0.0016, 0.0018]
    bal_thresholds = [1000, 2000]
    runners = []
    
    print("preparing mock...")
    api_wrapper_mock = ApiWrapperMock(start_date, end_date)
    print("done.")
    
    queue = Queue()
    
    for cpo in costs:
        print("~~~~  CPO: " + str(cpo) + "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        for rf in risk_factors:
            for bt in bal_thresholds:
                sim_env = SimEnv.SimEnv(start_date)
                algo = TestAlgorithm(sim_env, api_wrapper_mock, 30000, risk_factor=rf, costs_per_order=cpo, intelligent_balancing_threshold=bt, verbose=False)
                runner = ParallelRunner(queue, sim_env, algo, start_date, end_date)
                runners.append(runner)
                runner.start()
                print(len(runners))
        
    for runner in runners:
        "joining..."
        runner.join()
        print(queue.get())
    
                
def test():
    
    while len(runners) > 0:
        for runner in runners:
            if runner.isCompleted():
                results = runner.getResults()
                value = results[0]
                yield_ = results[1]
                trades = results[2]
                trans_costs = results[3]
                avg_pos_num = results[4]
                top_trades = results[5]
                
                rf = runner.getAlgo().getRiskFactor()
                bt = runner.getAlgo().getIntBalTreshold()
                
                print("[rf:" + str(rf) + ", bal_t:" + str(bt) + "]   [val=" + str(value) + ", yield=" + str(yield_) + ", trades=" + str(trades) + ", trans_costs=" + str(trans_costs) + ", avg_pos=" + str(avg_pos_num) + "]")
                print("trades: " + str(top_trades))
                print("")
                
                runners.remove(runner)
            
