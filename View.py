from bokeh import plotting
import Calculations

class View():

    def __init__(self, api_wrapper):
        self.xlist = []
        self.ylist = []
        self.legend = "test"

    def getXList(self):
        return self.xlist

    def getYList(self):
        return self.ylist

    def getLegend(self):
        return self.legend

class PriceView(View):

    def __init__(self, api_wrapper, symbol, start_date, end_date):
        self.api_wrapper = api_wrapper
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.legend = symbol
        self.xlist = []
        self.ylist = []

        price_stack = api_wrapper.getAdjustedPriceDataRangeStack(self.symbol, self.start_date, self.end_date)
        price_list = price_stack.getList()
        size = len(price_list)
        if price_stack.getSize() <= 1:
            print("weird date.")
            return 0

        i = 0
        while True:
            if i >= len(price_list):
                break
            else:
                adj_price = float(price_list[i].getData("adj_close"))
                self.xlist.append(i)
                self.ylist.append(adj_price)
                i += 1


class TrueRangeView(View):

    def __init__(self, api_wrapper, symbol, start_date, end_date):
        self.api_wrapper = api_wrapper
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.legend = symbol
        self.xlist = []
        self.ylist = []

        price_stack = api_wrapper.getAdjustedPriceDataRangeStack(self.symbol, self.start_date, self.end_date)
        price_list = price_stack.getList()
        size = len(price_list)
        if price_stack.getSize() <= 1:
            print("weird date.")
            return 0

        i = 1
        while True:
            if i >= len(price_list):
                break
            else:
                true_range = Calculations.calculateTrueRange(price_list[i], price_list[i-1])
                self.xlist.append(i)
                self.ylist.append(true_range)
                i+=1

class Graph():

    def __init__(self, title, x_label, y_label):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        plotting.output_file("view.html")
        self.plot = plotting.figure(title=self.title, x_axis_label=self.x_label, y_axis_label=self.y_label, plot_width=1200)
        self.color_list = ["red", "blue", "green", "yellow", "orange"]
        self.view_counter = 0

    def addView(self, view):
        xlist = view.getXList()
        ylist = view.getYList()
        color = self.color_list[self.view_counter]
        self.view_counter += 1

        self.plot.line(xlist, ylist, legend=view.getLegend(), line_width=2, line_color=color)

    def show(self):
        plotting.show(self.plot)
