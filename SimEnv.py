import os
import Algorithm
import Util
import YAFIObjects
import shutil

class SimEnv:

    def __init__(self):
        self.current_date = None

    def simulateAlgorithm(self, algo, start_date, end_date, interval):

        algo.prepare()

        self.current_date = start_date
        while True:
            algo.doLogic(self.current_date)
            self.current_date = self.current_date.getAfterDate(interval)
            if self.current_date > end_date:
                break

        algo.cleanUp()

    def getCurrentDate(self):
        return self.current_date

class Depot:

    # /depot
    # /depot/info.depot
    # /depot/portfolio
    # /depot/portfolio/AAA.posh
    # /depot/portfolio/BBB.posh
    # /depot/portfolio/...

    def __init__(self, sim_env, api_wrapper, name, cash):
        self.sim_env = sim_env
        self.api_wrapper = api_wrapper
        self.name = name
        self.portfolios = []
        self.info_obj = YAFIObjects.YAFIObjectDepotInfo([0])
        self.cash = cash
        self.loadStuff()

    def getName(self):
        return self.name

    def getApiWrapper(self):
        return self.api_wrapper

    def addPortfolio(self, portfolio):
        self.portfolios.append(portfolio)

    def loadStuff(self):
        foldername = Util.getDepotFolder(self.name)
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        else:
            self.loadPortfolios()
            self.info_obj = self.loadInfo()
            self.cash = float(self.info_obj.getData("cash"))

    def save(self):
        info_filename = Util.getDepotInfoFile(self.name)
        fileh = open(info_filename, "w")
        self.info_obj = YAFIObjects.YAFIObjectDepotInfo([self.cash])
        fileh.write(self.info_obj.getAsString())

        for portfolio in self.portfolios:
            portfolio.save()

    def loadPortfolios(self):
        for name in Util.getFileList(Util.getDepotFolder(self.name)):
            if not name.endswith(".depot"):
                self.portfolios.append(Portfolio(self.sim_env, self, name))

    def loadInfo(self):
        return Util.loadDepotInfo(self.name)

    def adjustCash(self, amount):
        if (self.cash + amount) < 0:
            return False
        self.cash += amount
        return True

    def getCash(self):
        return self.cash

    def removePortfolio(self, portfolio):
        filename = Util.getPortfolioFolder(self.name, portfolio.getName())
        self.portfolios.remove(portfolio)
        shutil.rmtree(filename)

class Portfolio:

    def __init__(self, sim_env, depot, name):
        self.sim_env = sim_env
        self.depot = depot
        self.name = name
        self.position_dict = {}
        self.loadPositions()

    def loadPositions(self):
        foldername = Util.getPortfolioFolder(self.depot.getName(), self.name)
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        else:
            for name in Util.getFileList(foldername):
                if name.endswith(".posh"):
                    symbol = name.split(".")[0]
                    self.position_dict[symbol] = PortfolioPosition(self, symbol)

    def save(self):
        for key in self.position_dict:
            self.position_dict[key].save()

    def calculatePrice(self, symbol, amount):
        price = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, self.getCurrentDate()))
        price = price * amount
        return price

    def buy(self, symbol, amount):
        price = self.calculatePrice(symbol, amount)
        success = self.depot.adjustCash(-price)
        if success == False:
            print("!!! cant make purchase: cash=" + Util.floatToStr(self.depot.getCash()) + " ,price=" + Util.floatToStr(price))
            return False
        else:
            print("made purchase: cash=" + Util.floatToStr(self.depot.getCash()) + " ,price=" + Util.floatToStr(price))

        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.buyAmount(amount, price)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].buyAmount(amount, price)
        return success

    def sell(self, symbol, amount):
        price = self.calculatePrice(symbol, amount)
        success = self.depot.adjustCash(price)
        if success == False:
            return False

        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.sellAmount(amount, price)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].sellAmount(amount, price)
        return success

    def getPosition(self, symbol):
        return self.position_dict[symbol]

    def getName(self):
        return self.name

    def getDepotName(self):
        return self.depot.getName()

    def getCurrentDate(self):
        return self.sim_env.getCurrentDate()


class PortfolioPosition:

    def __init__(self, portfolio, symbol):
        self.portfolio = portfolio
        self.symbol = symbol
        self.position_history = Util.loadPositionHistory(portfolio.getDepotName(), portfolio.getName(), symbol)

    def save(self):
        filename = Util.getPositionHistoryFilename(self.portfolio.getDepotName(), self.portfolio.getName(), self.symbol)
        fileh = open(filename, "w")
        for string in self.position_history.getActionStringList():
            fileh.write(string + "\n")
        fileh.close()

    def getSymbol(self):
        return self.symbol

    def getCurrentAmount(self):
        return self.position_history.getCurrentAmount()

    def buyAmount(self, amount, price):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "buy", amount, price)
        self.position_history.addHistoryAction(action)

    def sellAmount(self, amount, price):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "sell", amount, price)
        self.position_history.addHistoryAction(action)

class PositionHistory:

    def __init__(self, symbol, list_of_actions):
        self.symbol = symbol
        self.list_of_actions = list_of_actions
        if self.list_of_actions is None:
            self.list_of_actions = []

    def getActionStringList(self):
        list1 = []
        for a in self.list_of_actions:
            list1.append(a.getAsString())
        return list1

    def getCurrentAmount(self):
        value = 0
        for action in self.list_of_actions:
            value += action.getSignedAmount()
        return value

    def addHistoryAction(self, pos_history_action):
        self.list_of_actions.append(pos_history_action)

    def getSymbol(self):
        return self.symbol

    def getListOfActions(self):
        return self.list_of_actions

class PositionHistoryAction:

    def __init__(self, date, action_string, amount, price):
        # action can be "sell" or "buy"
        self.date = date
        self.action_string = action_string
        self.amount = int(amount)
        self.price = float(price)

    def getAsString(self):
        return("" + self.date.getAsString() + "," + self.action_string + "," + str(self.amount) + "," + str(self.price))

    def getDate(self):
        return self.date

    def getAction(self):
        return self.action_string

    def getAmount(self):
        return self.amount

    def getPrice(self):
        return self.price

    def getVolume(self):
        return self.price * self.amount

    def getSignedAmount(self):
        if self.action_string == "sell":
            return(-self.amount)
        return self.amount
