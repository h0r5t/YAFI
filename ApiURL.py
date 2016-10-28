
class ApiURL():

    def __init__(self, api, symbol, data_format):
        # supported APIs: "yafi", "quandl"
        self.api = api
        self.url = ""
        if self.api == "quandl":
            self.url = "https://www.quandl.com/api/v3/datasets/WIKI/"
            self.setSymbol(symbol)
            self.setFormat(data_format)
        else:
            print("api not supported yet: " + str(self.api))

    def getURL(self):
        return self.url

    def setSymbol(self, symbol):
        self.url += str(symbol)

    def setFormat(self, fformat):
        # "json" or "csv"
        self.url += ("." + str(fformat) + "?")

    def setDateRange(self, start_date, end_date):
        s_date_str = start_date.getAsString()
        e_date_str = end_date.getAsString()
        self.addParameter("start_date", s_date_str)
        self.addParameter("end_date", e_date_str)

    def setInterval(self, interval):
        # "daily", "monthly", "yearly"
        self.addParameter("collapse", interval)

    def addParameter(self, name, value):
        self.url += ("&" + str(name) + "=" + str(value))
