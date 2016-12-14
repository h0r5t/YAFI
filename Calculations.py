import math

from pylab import *
from scipy.optimize import curve_fit
from scipy.stats import linregress


class MomentumData():

    def __init__(self, slope, atr):
        self.slope = slope
        self.atr = atr

    def getSlope(self):
        return self.slope

    def getATR(self):
        return self.atr

    def calculatePositionSize(self, depot_value, risk_factor):
        return int(calculatePositionSize(depot_value, self.atr, risk_factor))

def calculatePositionSize(depot_size, atr, risk_factor=0.001):
    size = depot_size * risk_factor / atr
    return int(size)

def calculateMovingAverage(price_stack, days):
    if days > price_stack.getSize():
        return 0
    price_sum = 0
    p_list = price_stack.getList()
    size = len(p_list)
    for i in range(0, days):
        price_obj = p_list[size - 1 - i]
        price_sum += float(price_obj.getData("adj_close"))
    return price_sum / days

def gapExists(price_stack, days, max_gap_size_in_percent=0.15):
    # returns True if no gap of this size (or bigger) present
    if days > price_stack.getSize():
        return 0
    p_list = price_stack.getList()
    size = len(p_list)
    for i in range(0, days):
        price_obj = p_list[size - 1 - i]
        day_before_obj = p_list[size - 2 - i]
        current_price = float(price_obj.getData("adj_close"))
        day_before_price = float(day_before_obj.getData("adj_close"))
        ratio = (current_price - day_before_price) / day_before_price
        if abs(ratio) > max_gap_size_in_percent:
            return True
    return False

def calculateATR(price_stack, interval=20):
    price_list = price_stack.getList()
    size = len(price_list)
    if price_stack.getSize() <= 1:
        return 0
    sum1 = 0
    for i in range(0, interval):
        sum1 += calculateTrueRange(price_list[size - 1 - i], price_list[size - 2 - i])
    atr = sum1 / interval
    return atr

def calculateTrueRange(price_obj, prev_obj):
    high = float(price_obj.getData("high"))
    low = float(price_obj.getData("low"))
    close = float(price_obj.getData("close"))
    close_prev = float(prev_obj.getData("close"))
    adj_close = float(price_obj.getData("adj_close"))

    factor1 = (high - low) / close
    n1 = factor1 * adj_close
    factor2 = abs(high - close_prev) / close
    n2 = factor2 * adj_close
    factor3 = abs(low - close_prev) / close
    n3 = factor3 * adj_close
    true_range = max([n1, n2, n3])

    return true_range

def getAdjustedAnnualizedSlope(price_stack):
    price_list = price_stack.getList()
    if len(price_list) < 90:
        return 0

    return_list = []
    for i in range(0, 90):
        price = price_list[price_stack.getSize() - 1 - i]
        return_list.insert(0, float(price.getData("adj_close")))
    prices_array = np.asarray(return_list)

    if prices_array is None or len(prices_array) < 90:
        return 0

    array_log = np.log(prices_array)
    xdata = np.linspace(0, 89, 90)
    slope, intercept, r_value, p_value, std_err = linregress(xdata, array_log)
    r_squared = r_value ** 2
    normalized = np.exp(slope)
    annualized = (np.power(normalized, 250) - 1) * 100
    adj_annualized_slope = annualized * r_squared

    return adj_annualized_slope
