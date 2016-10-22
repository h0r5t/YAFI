import YAFIApiWrapper
import Util
import SimEnv
import Algorithm

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()
        sim_env = SimEnv.SimEnv()
        algo = Algorithm.TestAlgorithm(sim_env, api_wrapper)
        sim_env.simulateAlgorithm(algo, Util.UtilDate(2009, 1, 1), Util.UtilDate(2009, 3, 30), 1)

if __name__ == "__main__":
    yafi = YAFI()
