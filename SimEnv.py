import os
import Algorithm
import Util
import YAFIObjects

class SimEnv:

    def __init__(self, start_date):
        self.current_date = start_date
        self.depot = Depot(self, "depot1")
        self.portfolio1 = Portfolio(self, self.depot, "portfolio1")
        self.depot.addPortfolio(self.portfolio1)
        self.portfolio1.buy("AAPL", 3)
        self.portfolio1.buy("MSFT", 4)
        self.current_date = self.current_date.getNextDayDate()
        self.portfolio1.buy("AAPL", 3)
        self.portfolio1.buy("MSFT", 4)
        print(self.portfolio1.getPosition("AAPL").getCurrentAmount())
        self.depot.save()

    def simulateAlgorithm(self, algo, start_date, end_date):
        pass

    def buy(self, symbol, amount):
        pass

    def sell(self, symbol, amount):
        pass

    def getCurrentDate(self):
        return self.current_date

class Depot:

    # /depot
    # /depot/info.depot
    # /depot/portfolio
    # /depot/portfolio/AAA.posh
    # /depot/portfolio/BBB.posh
    # /depot/portfolio/...

    def __init__(self, sim_env, name):
        self.sim_env = sim_env
        self.name = name
        self.portfolios = []
        self.info_obj = None
        self.cash = 0
        self.loadStuff()

    def getName(self):
        return self.name

    def addPortfolio(self, portfolio):
        self.portfolios.append(portfolio)

    def loadStuff(self):
        foldername = Util.getDepotFolder(self.name)
        if not os.path.exists(foldername):
            os.makedirs(foldername)
            self.info_obj = YAFIObjects.YAFIObjectDepotInfo([0])
            self.cash = 0
        else:
            self.loadPortfolios()
            self.info_obj = self.loadInfo()
            self.cash = self.info_obj.getData("cash")

    def save(self):
        info_filename = Util.getDepotInfoFile(self.name)
        fileh = open(info_filename, "w")
        fileh.write(self.info_obj.getAsString())

        for portfolio in self.portfolios:
            portfolio.save()

    def loadPortfolios(self):
        for name in Util.getFileList(Util.getDepotFolder(self.name)):
            if not name.endswith(".depot"):
                self.portfolios.append(Portfolio(self.sim_env, self, name))

    def loadInfo(self):
        return Util.loadDepotInfo(self.name)

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

    def buy(self, symbol, amount):
        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.buyAmount(amount)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].buyAmount(amount)

    def sell(self, symbol, amount):
        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.sellAmount(amount)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].sellAmount(amount)

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

    def buyAmount(self, amount):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "buy", amount)
        self.position_history.addHistoryAction(action)

    def sellAmount(self, amount):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "sell", amount)
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

    def __init__(self, date, action_string, amount):
        # action can be "sell" or "buy"
        self.date = date
        self.action_string = action_string
        self.amount = int(amount)

    def getAsString(self):
        return("" + self.date.getAsString() + "," + self.action_string + "," + str(self.amount))

    def getDate(self):
        return self.date

    def getAction(self):
        return self.action_string

    def getAmount(self):
        return self.amount

    def getSignedAmount(self):
        if self.action_string == "sell":
            return(-self.amount)
        return self.amount
