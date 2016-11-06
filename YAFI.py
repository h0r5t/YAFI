import YAFIApiWrapper
import Util
import SimEnv
import Algorithm
import Calculations
import time
import View
import os
from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource
import numpy as np

class YAFI:

    def __init__(self):
        api_wrapper = YAFIApiWrapper.YAFIApiWrapper()

        hover = HoverTool(
                tooltips=[
                    ("index", "$index"),
                    ("(x,y)", "($x, $y)"),
                    ("text", "@text"),
                ]
            )

        source = ColumnDataSource(
                data=dict(
                    x=[np.datetime64("2015-03-01")],
                    y=[120],
                    text=["test"],
                )
            )
        tools = [hover]
        graph = View.Graph("price", "a", "b", tools)
        graph.addCircle("x", "y", 20, source)
        pv = View.PriceView(api_wrapper, "AAPL", Util.UtilDate(2015,1,1), Util.UtilDate(2015,5,1))
        graph.addView(pv)


        graph.show()

if __name__ == "__main__":
    yafi = YAFI()
