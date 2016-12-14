import math
import os
import shutil

import Algorithm
import Util
import YAFIObjects


class SimEnv:

    def __init__(self, date):
        self.current_date = date

    def setDate(self, date):
        self.current_date = date

    def simulateAlgorithm(self, algo, start_date, end_date):

        algo.prepare(start_date, end_date)

        self.current_date = start_date
        while True:
            algo.preLogic(self.current_date)
            self.current_date = self.current_date.getNextDayDate()
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
        self.starting_cash = cash
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
            if self.info_obj is not None:
                self.starting_cash = float(self.info_obj.getData("starting_cash"))

    def save(self):
        info_filename = Util.getDepotInfoFile(self.name)
        fileh = open(info_filename, "w")
        self.info_obj = YAFIObjects.YAFIObjectDepotInfo([self.starting_cash])
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
        if (self.starting_cash + amount) < 0:
            return False
        self.starting_cash += amount
        return True

    def getCash(self):
        return self.starting_cash

    def getCurrentValue(self):
        sum1 = 0
        for p in self.portfolios:
            sum1 += p.getCurrentValue()
        return sum1 + self.starting_cash

    def removePortfolio(self, portfolio):
        filename = Util.getPortfolioFolder(self.name, portfolio.getName())
        self.portfolios.remove(portfolio)
        shutil.rmtree(filename)

class Portfolio:

    def __init__(self, sim_env, depot, name, costs_per_order):
        self.sim_env = sim_env
        self.depot = depot
        self.name = name
        self.costs_per_order = costs_per_order
        self.position_dict = {}
        self.comp_history = PortfolioCompositionHistory()
        self.loadPositions()

    def makeSnapshot(self):
        self.comp_history.makeSnapshot(self)

    def getCompositionHistory(self):
        return self.comp_history

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
            
    def calculateRawPrice(self, symbol, amount):
        price_for_one = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, self.getCurrentDate()))
        price = (price_for_one * amount)
        return (price_for_one, price)

    def calculateBuyingPrice(self, symbol, amount):
        price_for_one = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, self.getCurrentDate()))
        price = (price_for_one * amount) + self.costs_per_order
        return (price_for_one, price)
    
    def calculateSellingPrice(self, symbol, amount):
        price_for_one = float(self.depot.getApiWrapper().getAdjustedPriceForDate(symbol, self.getCurrentDate()))
        price = (price_for_one * amount) - self.costs_per_order
        return (price_for_one, price)

    def buy(self, symbol, amount, reason):
        price_for_one, price = self.calculateBuyingPrice(symbol, amount)
        success = self.depot.adjustCash(-price)
        if success == False:
            possibleAmount = math.floor((self.depot.getCash() - self.costs_per_order) / price_for_one)
            if possibleAmount > 0:
                self.buy(symbol, possibleAmount, reason)
            return False
        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.buyAmount(amount, price_for_one, reason)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].buyAmount(amount, price_for_one, reason)
        return success

    def sell(self, symbol, amount, reason):
        price_for_one, price = self.calculateSellingPrice(symbol, amount)
        success = self.depot.adjustCash(price)
        if success == False:
            return False
        if symbol in self.position_dict:
            position = self.position_dict[symbol]
            position.sellAmount(amount, price_for_one, reason)
        else:
            self.position_dict[symbol] = PortfolioPosition(self, symbol)
            self.position_dict[symbol].sellAmount(amount, price_for_one, reason)
        return success


    def sellAll(self, symbol, reason):
        self.sell(symbol, self.getPosition(symbol).getCurrentAmount(), reason)

    def getPositions(self):
        # returns list of PortfolioPosition
        list1 = []
        for pos in self.position_dict.values():
            if pos.getCurrentAmount() > 0:
                list1.append(pos)
        return list1
    
    def getAllClosedPositions(self):
        list1 = []
        for pos in self.position_dict.values():
            if pos.getCurrentAmount() <= 0:
                list1.append(pos)
        return list1
    
    def getTotalAmountOfTrades(self):
        sum1 = 0
        for pos in self.position_dict.values():
            sum1 += pos.getAmountOfTrades()
        
        return sum1

    def getSymbols(self):
        # returns list of symbols only
        list1 = []
        for pos in self.position_dict.values():
            if pos.getCurrentAmount() > 0:
                list1.append(pos.getSymbol())
        return list1

    def getPosition(self, symbol):
        return self.position_dict[symbol]

    def getName(self):
        return self.name

    def getDepotName(self):
        return self.depot.getName()

    def getCurrentDate(self):
        return self.sim_env.getCurrentDate()

    def getCurrentValue(self):
        sum1 = 0
        for key, pos in self.position_dict.items():
            if pos.getCurrentAmount() > 0:
                a, val = self.calculateRawPrice(key, pos.getCurrentAmount())
                sum1 += val
        return sum1

class PortfolioCompositionHistory:

    def __init__(self):
        self.snapshot_dict = {}

    def makeSnapshot(self, portfolio):
        portfolio_snapshot = PortfolioSnapshot(portfolio.getCurrentDate())
        for pos in portfolio.getPositions():
            portfolio_snapshot.addPosition(pos)
        self.addPortfolioSnapshot(portfolio_snapshot)

        self.printInfo(portfolio.getCurrentDate())

    def printInfo(self, date):
        self.snapshot_dict[date.getAsString()].printInfo()

    def addPortfolioSnapshot(self, p_snap):
        self.snapshot_dict[p_snap.getDate().getAsString()] = p_snap

    def printAll(self):
        for date_string in self.snapshot_dict:
            print(date_string)
            for pos_snap in self.snapshot_dict[date_string].getPositionSnapshots():
                print("   " + pos_snap.getSymbol() + ", " + str(pos_snap.getAbsoluteAmount()) + ", " + str(pos_snap.getValue()))
            print("")

class PortfolioSnapshot:

    def __init__(self, date):
        self.date = date
        self.position_snapshots = []

    def printInfo(self):
        print(len(self.position_snapshots))

    def addPosition(self, pos):
        self.position_snapshots.append(PositionSnapshot(pos))

    def getPositionSnapshots(self):
        return self.position_snapshots

    def getDate(self):
        return self.date

class PositionSnapshot:

    def __init__(self, pos):
        self.symbol = pos.getSymbol()
        self.abs_amount = pos.getCurrentAmount()
        self.value = pos.getCurrentValue()[1]

    def getSymbol(self):
        return self.symbol

    def getAbsoluteAmount(self):
        return self.abs_amount

    def getValue(self):
        return self.value

class PortfolioPosition:

    def __init__(self, portfolio, symbol):
        self.portfolio = portfolio
        self.symbol = symbol
        self.position_history = Util.loadPositionHistory(portfolio.getDepotName(), portfolio.getName(), symbol)
        self.balance_state = Util.loadBalanceState(portfolio.getDepotName(), portfolio.getName(), symbol)
        self.trades_amount = 0
        
    def getBalanceState(self):
        return self.balance_state
    
    def getAmountOfTrades(self):
        return self.trades_amount
    
    def getPositionHistory(self):
        return self.position_history

    def save(self):
        # save posh
        filename = Util.getPositionHistoryFilename(self.portfolio.getDepotName(), self.portfolio.getName(), self.symbol)
        fileh = open(filename, "w")
        for string in self.position_history.getActionStringList():
            fileh.write(string + "\n")
        fileh.close()
        
        # save bal
        filename = Util.getBalanceStateFilename(self.portfolio.getDepotName(), self.portfolio.getName(), self.symbol)
        fileh = open(filename, "w")
        fileh.write(str(self.balance_state.getBalanceAmount()))
        fileh.close()

    def getSymbol(self):
        return self.symbol

    def getCurrentValue(self):
        return self.portfolio.calculateRawPrice(self.symbol, self.getCurrentAmount())

    def getCurrentAmount(self):
        return self.position_history.getCurrentAmount()

    def buyAmount(self, amount, price, reason):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "buy", amount, price, reason)
        self.position_history.addHistoryAction(action)
        self.trades_amount += 1

    def sellAmount(self, amount, price, reason):
        action = PositionHistoryAction(self.portfolio.getCurrentDate(), "sell", amount, price, reason)
        self.position_history.addHistoryAction(action)
        self.trades_amount += 1
        
class BalanceState:
    
    def __init__(self, amount):
        self.amount = amount
        
    def getBalanceAmount(self):
        return self.amount
    
    def reset(self):
        self.amount = 0
        
    def plus(self, value):
        self.amount += value
        
    def minus(self, value):
        self.amount -= value

class PositionHistory:

    def __init__(self, symbol, list_of_actions):
        self.symbol = symbol
        self.list_of_actions = list_of_actions
        if self.list_of_actions is None:
            self.list_of_actions = []
            
    def getTotalRevenue(self):
        spending = 0
        income = 0
        for action in self.list_of_actions:
            if action.getAction() == "buy":
                spending += int(action.getVolume())
            elif action.getAction() == "sell":
                income += int(action.getVolume())
        return int(income - spending)

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

    def __init__(self, date, action_string, amount, price, reason):
        # action can be "sell" or "buy"
        # reason: string
        self.date = date
        self.action_string = action_string
        self.amount = int(amount)
        self.price = float(price)
        self.reason = reason

    def getAsString(self):
        return("" + self.date.getAsString() + "," + self.action_string + "," + str(self.amount) + "," + str(self.price) + "," + self.reason)

    def getDate(self):
        return self.date

    def getAction(self):
        return self.action_string

    def getAmount(self):
        return self.amount

    def getPrice(self):
        return self.price

    def getReason(self):
        return self.reason

    def getVolume(self):
        return self.price * self.amount

    def getSignedAmount(self):
        if self.action_string == "sell":
            return(-self.amount)
        return self.amount
