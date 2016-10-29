import SimEnv
import YAFIApiWrapper
import Util

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
        self.depot = SimEnv.Depot(sim_env, api_wrapper, "test_depot", 200)
        self.portfolio = SimEnv.Portfolio(sim_env, self.depot, "test_portfolio")
        self.depot.addPortfolio(self.portfolio)
        self.setDaysToSkip(6)

    def prepare(self):
        pass

    def doLogic(self, date):
        success = self.portfolio.buy("AAPL", 2)
        if success:
            print("bought")
        else:
            self.portfolio.sell("AAPL", 2)

    def cleanUp(self):
        self.depot.save()

if __name__ == "__main__":
    api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
    sim_env = SimEnv.SimEnv()
    algo = TestAlgorithm(sim_env, api_wrapper)

    start_date = Util.UtilDate(2015, 1, 1)
    end_date = Util.UtilDate(2016, 1, 1)
    sim_env.simulateAlgorithm(algo, start_date, end_date)
