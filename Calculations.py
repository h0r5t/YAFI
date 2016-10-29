from scipy.optimize import curve_fit
from scipy.stats import linregress
from pylab import *
import math
from bokeh.plotting import figure, output_file, show
from Util import UtilDate

def calculatePositionSize(depot_size, atr, risk_factor=0.001):
    size = depot_size * risk_factor / atr
    return int(size)

def calculateMovingAverage(price_stack, days):
    if days > price_stack.getSize():
        print("error, average days > price_stack size")
        return 0
    price_sum = 0
    for price_obj in price_stack.getList():
        price_sum += float(price_obj.getData("adj_close"))
    return price_sum / days

def calculateATR(api_wrapper, price_stack, interval=20):
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

def getAdjustedAnnualizedSlope(api_wrapper, symbol, date, showGraph=False):
    prices_array = get90DaysPriceArray(api_wrapper, symbol, date)
    if prices_array is None or len(prices_array) < 90:
        return 0

    array_log = np.log(prices_array)
    xdata = np.linspace(0, 89, 90)
    slope, intercept, r_value, p_value, std_err = linregress(xdata, array_log)
    r_squared = r_value**2
    normalized = np.exp(slope)
    annualized = (np.power(normalized, 250) - 1) * 100
    adj_annualized_slope = annualized * r_squared

    if showGraph:
        drawGraph(xdata, prices_array)

    return adj_annualized_slope

def get90DaysPriceArray(api_wrapper, symbol, date):
    price_stack = api_wrapper.getAdjustedPriceDataRangeStackForAmountOfDays(symbol, date, 90)
    if price_stack is None:
        return None
    # calculate atr !!! with stack
    price_list = price_stack.getList()
    return_list = []
    for price in price_list:
        return_list.append(float(price.getData("adj_close")))
    return np.asarray(return_list)

def get90Days(array1):
    array_log = np.log(array1)
    xdata = np.linspace(0, 89, 90)
    slope, intercept, r_value, p_value, std_err = linregress(xdata, array_log)
    r_squared = r_value**2
    normalized = np.exp(slope)
    annualized = (np.power(normalized, 250) - 1) * 100


def drawGraph(xlist, ylist):

    output_file("lines.html")
    p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')
    p.line(xlist, ylist, legend="Temp.", line_width=2)
    show(p)
