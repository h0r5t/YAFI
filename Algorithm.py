import SimEnv

class Algorithm:

    def init(self, sim_env, api_wrapper):
        self.sim_env = sim_env
        self.api_wrapper = api_wrapper

    def prepare(self):
        pass

    def doLogic(self, date):
        pass

    def cleanUp(self):
        pass

class TestAlgorithm(Algorithm):

    def __init__(self, sim_env, api_wrapper):
        self.init(sim_env, api_wrapper)
        self.lastDate = None
        self.depot = SimEnv.Depot(sim_env, api_wrapper, "test_depot", 200)
        self.portfolio = SimEnv.Portfolio(sim_env, self.depot, "test_portfolio")
        self.depot.addPortfolio(self.portfolio)

        self.day_counter = 0

    def prepare(self):
        pass

    def doLogic(self, date):
        if self.lastDate is None:
            self.buyApple(date)
            self.lastDate = date
        elif self.day_counter == 7:
            self.buyApple(date)
            self.day_counter = 0
        self.day_counter += 1

    def buyApple(self, date):
        self.portfolio.buy("AAPL", 2)

    def cleanUp(self):
        self.depot.save()
