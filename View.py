from bokeh import plotting
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
import Calculations
import time
import numpy as np
from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource

def generateBuySellGraph(api_wrapper, depot_name, portfolio_name, symbol, start_date, end_date):
    # returns the graph

    graph = Graph("BUY/SELL VIEW", "Date", "Adj. Close", True)
    pv = PriceView(api_wrapper, symbol, start_date, end_date)
    graph.addView(pv)

    posh_actions = api_wrapper.getPositionHistoryActionListForDateRange(depot_name, portfolio_name, symbol, start_date, end_date)
    for action in posh_actions:
        graph.addPositionHistoryActionHoverPoint(action)

    return graph

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
                date_np = np.datetime64(price_list[i].getData("date"))
                self.xlist.append(date_np)
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
                date_np = np.datetime64(price_list[i].getData("date"))
                self.xlist.append(date_np)
                self.ylist.append(true_range)
                i+=1

class BuyLabelData():

    def __init__(self):
        self.datelist = []
        self.pricelist = []
        self.textlist = []

    def addLabel(self, date, price, text):
        self.datelist.append(np.datetime64(date.getAsString()))
        self.pricelist.append(price)
        self.textlist.append(text)

    def getDict(self):
        return dict(dates=self.datelist, prices=self.pricelist, text=self.textlist)

class Graph():

    def __init__(self, title, x_label, y_label, hover_tools_enabled=False):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        plotting.output_file("views/view.html")
        if hover_tools_enabled == False:
            self.plot = plotting.figure(title=self.title, x_axis_label=self.x_label, y_axis_label=self.y_label, plot_width=1200, x_axis_type="datetime")
        else:
            hover = HoverTool(
                    tooltips=[
                        ("date", "@date_string"),
                        ("price", "@y"),
                        ("amount", "@amount"),
                        ("volume", "@volume"),
                    ],names=["posh_1", "posh_2"]
                )
            self.plot = plotting.figure(title=self.title, x_axis_label=self.x_label, y_axis_label=self.y_label, plot_width=1200, x_axis_type="datetime", tools=[hover])
        self.color_list = ["blue", "red", "green", "yellow", "orange"]
        self.view_counter = 0

        # dicts for hover tools
        self.dates_list_buy = []
        self.prices_list_buy = []
        self.dates_string_list_buy = []
        self.amounts_list_buy = []
        self.volume_list_buy = []
        self.sizes_list_buy = []

        self.dates_list_sell = []
        self.prices_list_sell = []
        self.dates_string_list_sell = []
        self.amounts_list_sell = []
        self.volume_list_sell = []
        self.sizes_list_sell = []

    def addLabelData(self, label_data):
        source = ColumnDataSource(label_data.getDict())
        labels = LabelSet(x='dates', y='prices', text='text', level='glyph',
              x_offset=5, y_offset=5, source=source, render_mode='canvas')
        self.plot.add_layout(labels)

    def addPositionHistoryActionHoverPoint(self, pos_his_action):
        if pos_his_action.getAction() == "buy":
            self.dates_list_buy.append(np.datetime64(pos_his_action.getDate().getAsString()))
            self.prices_list_buy.append(float(pos_his_action.getPrice()))
            self.dates_string_list_buy.append(pos_his_action.getDate().getAsString())
            self.amounts_list_buy.append(int(pos_his_action.getAmount()))
            self.volume_list_buy.append(float(pos_his_action.getVolume())/1000)
            self.sizes_list_buy.append(self.calculatePoshActionCircleSize(int(pos_his_action.getAmount())))

        elif pos_his_action.getAction() == "sell":
            self.dates_list_sell.append(np.datetime64(pos_his_action.getDate().getAsString()))
            self.prices_list_sell.append(float(pos_his_action.getPrice()))
            self.dates_string_list_sell.append(pos_his_action.getDate().getAsString())
            self.amounts_list_sell.append(int(pos_his_action.getAmount()))
            self.volume_list_sell.append(float(pos_his_action.getVolume())/1000)
            self.sizes_list_sell.append(self.calculatePoshActionCircleSize(int(pos_his_action.getAmount())))

    def calculatePoshActionCircleSize(self, amount):
        a = amount
        if a <= 7:
            return 7
        if a >= 25:
            return 25
        return a

    def activateHoverTools(self):
        source_buy = ColumnDataSource(
                data=dict(
                    x=self.dates_list_buy,
                    y=self.prices_list_buy,
                    date_string=self.dates_string_list_buy,
                    amount=self.amounts_list_buy,
                    volume=self.volume_list_buy,
                    sizes=self.sizes_list_buy
                )
            )

        source_sell = ColumnDataSource(
                data=dict(
                    x=self.dates_list_sell,
                    y=self.prices_list_sell,
                    date_string=self.dates_string_list_sell,
                    amount=self.amounts_list_sell,
                    volume=self.volume_list_sell,
                    sizes=self.sizes_list_sell
                )
            )

        self.plot.circle(x="x", y="y", source=source_buy, color="#4CA07A", name="posh_1", size="sizes")
        self.plot.circle(x="x", y="y", source=source_sell, color="#9B093E", name="posh_2", size="sizes")

    def addView(self, view):
        xlist = view.getXList()
        ylist = view.getYList()
        color = self.color_list[self.view_counter]
        self.view_counter += 1

        self.plot.line(xlist, ylist, legend=view.getLegend(), line_width=2, line_color=color)

    def show(self):
        self.activateHoverTools()
        plotting.show(self.plot)

    def save(self):
        self.activateHoverTools()
        plotting.save(self.plot)
