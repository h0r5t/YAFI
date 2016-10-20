

class Algorithm:

    def init(self, sim_env, api_wrapper):
        self.sim_env = sim_env
        self.api_wrapper = api_wrapper

    def doLogic(self, date):
        pass

class TestAlgorithm(Algorithm):

    def __init__(self, sim_env, api_wrapper):
        self.init(sim_env, api_wrapper)

    def doLogic(self, date):
        pass
