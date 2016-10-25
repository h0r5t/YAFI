from scipy.optimize import curve_fit
from scipy.stats import linregress
from pylab import *
import math
from bokeh.plotting import figure, output_file, show
from Util import UtilDate

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
    price_list = price_stack.getList()
    return np.asarray(price_list)

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
